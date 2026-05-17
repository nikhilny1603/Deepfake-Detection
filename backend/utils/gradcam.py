"""
Grad-CAM implementation for visualising the regions that drove the prediction.

Reference: Selvaraju et al., 2017 — "Grad-CAM: Visual Explanations from Deep
Networks via Gradient-based Localization."
"""
from __future__ import annotations
import numpy as np
import torch
import torch.nn.functional as F
import cv2


class GradCAM:
    def __init__(self, model: torch.nn.Module, target_layer: torch.nn.Module):
        self.model = model
        self.target_layer = target_layer
        self.activations: torch.Tensor | None = None
        self.gradients: torch.Tensor | None = None

        target_layer.register_forward_hook(self._save_activation)
        target_layer.register_full_backward_hook(self._save_gradient)

    def _save_activation(self, _module, _inp, output):
        self.activations = output.detach()

    def _save_gradient(self, _module, _grad_in, grad_out):
        self.gradients = grad_out[0].detach()

    def __call__(self, input_tensor: torch.Tensor, class_idx: int | None = None):
        """Returns a (H, W) heatmap normalised to [0, 1]."""
        self.model.eval()
        logits = self.model(input_tensor)
        if class_idx is None:
            class_idx = int(logits.argmax(dim=1).item())

        self.model.zero_grad()
        logits[0, class_idx].backward(retain_graph=True)

        # Global-average-pool the gradients over the spatial dims
        weights = self.gradients.mean(dim=(2, 3), keepdim=True)  # [B,C,1,1]
        cam = (weights * self.activations).sum(dim=1, keepdim=True)  # [B,1,h,w]
        cam = F.relu(cam)
        cam = F.interpolate(
            cam, size=input_tensor.shape[2:], mode="bilinear", align_corners=False
        )
        cam = cam[0, 0].cpu().numpy()
        cam -= cam.min()
        if cam.max() > 0:
            cam /= cam.max()
        return cam, class_idx


def overlay_heatmap(image_bgr: np.ndarray, heatmap: np.ndarray, alpha: float = 0.45) -> np.ndarray:
    """Blend a heatmap (HxW in [0,1]) over a BGR image. Returns BGR uint8."""
    heat_u8 = np.uint8(255 * heatmap)
    heat_color = cv2.applyColorMap(heat_u8, cv2.COLORMAP_JET)
    if heat_color.shape[:2] != image_bgr.shape[:2]:
        heat_color = cv2.resize(heat_color, (image_bgr.shape[1], image_bgr.shape[0]))
    return cv2.addWeighted(image_bgr, 1 - alpha, heat_color, alpha, 0)
