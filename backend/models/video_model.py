"""
Video deepfake detector — EfficientNet-B0 (per-frame features) + LSTM aggregator.
"""
from __future__ import annotations
from pathlib import Path
import torch
import torch.nn as nn
import timm


class VideoDeepfakeModel(nn.Module):
    def __init__(self, num_classes: int = 2, hidden: int = 256, pretrained: bool = True):
        super().__init__()
        self.cnn = timm.create_model(
            "efficientnet_b0", pretrained=pretrained, num_classes=0, global_pool="avg"
        )
        feat_dim = self.cnn.num_features
        self.lstm = nn.LSTM(feat_dim, hidden, batch_first=True, bidirectional=True)
        self.classifier = nn.Sequential(
            nn.Dropout(0.4),
            nn.Linear(hidden * 2, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: [B, T, 3, H, W] → logits [B, num_classes]"""
        B, T, C, H, W = x.shape
        feats = self.cnn(x.view(B * T, C, H, W)).view(B, T, -1)
        seq, _ = self.lstm(feats)
        pooled = seq.mean(dim=1)
        return self.classifier(pooled)

    def per_frame_logits(self, x: torch.Tensor) -> torch.Tensor:
        """Returns per-frame contribution scores for the FAKE class.

        Shape: [B, T]. Used to highlight the most influential frames.
        """
        B, T, C, H, W = x.shape
        feats = self.cnn(x.view(B * T, C, H, W)).view(B, T, -1)
        seq, _ = self.lstm(feats)
        # Project each timestep through the classifier head
        per_step = self.classifier(seq)  # [B, T, num_classes]
        # Use softmax probability of FAKE (class index 1)
        return torch.softmax(per_step, dim=-1)[..., 1]


def load_video_model(weights_path: Path | None, device: str = "cpu") -> VideoDeepfakeModel:
    model = VideoDeepfakeModel(pretrained=True)
    if weights_path and Path(weights_path).is_file():
        state = torch.load(weights_path, map_location=device)
        model.load_state_dict(state, strict=False)
    return model.to(device).eval()
