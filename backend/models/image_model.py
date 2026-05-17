"""
Image deepfake detector — EfficientNet-B0 backbone with a 2-class head.
Uses `timm` for the backbone so weights load from ImageNet by default.
"""
from __future__ import annotations
from pathlib import Path
import torch
import torch.nn as nn
import timm


class ImageDeepfakeModel(nn.Module):
    def __init__(self, num_classes: int = 2, pretrained: bool = True):
        super().__init__()
        self.backbone = timm.create_model(
            "efficientnet_b0", pretrained=pretrained, num_classes=0, global_pool="avg"
        )
        feat_dim = self.backbone.num_features
        self.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(feat_dim, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        feats = self.backbone(x)
        return self.classifier(feats)

    @property
    def gradcam_target_layer(self) -> nn.Module:
        # Last convolutional block in EfficientNet-B0
        return self.backbone.blocks[-1]


def load_image_model(weights_path: Path | None, device: str = "cpu") -> ImageDeepfakeModel:
    model = ImageDeepfakeModel(pretrained=True)
    if weights_path and Path(weights_path).is_file():
        state = torch.load(weights_path, map_location=device)
        model.load_state_dict(state, strict=False)
    return model.to(device).eval()
