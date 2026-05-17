"""
Audio deepfake detector — small CNN over mel-spectrograms.
Input shape: [B, 1, n_mels, time]
"""
from __future__ import annotations
from pathlib import Path
import torch
import torch.nn as nn


class AudioDeepfakeModel(nn.Module):
    def __init__(self, num_classes: int = 2):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),

            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((4, 4)),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.4),
            nn.Linear(128 * 4 * 4, 128),
            nn.ReLU(inplace=True),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        return self.classifier(self.features(x))


def load_audio_model(weights_path: Path | None, device: str = "cpu") -> AudioDeepfakeModel:
    model = AudioDeepfakeModel()
    if weights_path and Path(weights_path).is_file():
        state = torch.load(weights_path, map_location=device)
        model.load_state_dict(state, strict=False)
    return model.to(device).eval()
