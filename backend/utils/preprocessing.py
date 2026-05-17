"""Common image preprocessing for the deepfake CNNs."""
import io
from typing import Tuple
import numpy as np
import cv2
import torch
from PIL import Image
from torchvision import transforms

IMG_SIZE = 224
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

_image_transform = transforms.Compose(
    [
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ]
)


def bytes_to_pil(b: bytes) -> Image.Image:
    return Image.open(io.BytesIO(b)).convert("RGB")


def preprocess_image(pil: Image.Image) -> torch.Tensor:
    """Returns a [1, 3, H, W] float tensor on CPU."""
    return _image_transform(pil).unsqueeze(0)


def pil_to_bgr(pil: Image.Image) -> np.ndarray:
    arr = np.array(pil)
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def denormalise(t: torch.Tensor) -> np.ndarray:
    """Convert a normalised [3,H,W] tensor back to a HxWx3 uint8 BGR image."""
    img = t.detach().cpu().numpy().transpose(1, 2, 0)
    img = img * np.array(IMAGENET_STD) + np.array(IMAGENET_MEAN)
    img = np.clip(img * 255, 0, 255).astype(np.uint8)
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
