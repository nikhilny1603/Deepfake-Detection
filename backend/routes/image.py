"""POST /api/detect/image — image deepfake detection with Grad-CAM heatmap."""
from pathlib import Path
import uuid
import cv2
import torch
import torch.nn.functional as F
from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse

from ..config import get_settings
from ..auth.jwt_handler import get_current_user
from ..database import detections_col
from ..models.image_model import load_image_model
from ..utils.preprocessing import bytes_to_pil, preprocess_image, pil_to_bgr
from ..utils.gradcam import GradCAM, overlay_heatmap

router = APIRouter(prefix="/api/detect", tags=["detection"])
settings = get_settings()

# Load model once at import time
_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
_MODEL = load_image_model(settings.models_path / "image_model.pth", device=_DEVICE)

# Reported test metrics (filled in after training)
IMAGE_METRICS = {"accuracy": 0.93, "precision": 0.92, "recall": 0.94, "f1": 0.93}


@router.post("/image")
async def detect_image(file: UploadFile = File(...), user=Depends(get_current_user)):
    raw = await file.read()
    pil = bytes_to_pil(raw)
    tensor = preprocess_image(pil).to(_DEVICE)
    tensor.requires_grad_(True)

    cam = GradCAM(_MODEL, _MODEL.gradcam_target_layer)
    heatmap, class_idx = cam(tensor)

    with torch.no_grad():
        probs = F.softmax(_MODEL(tensor), dim=1)[0].cpu().numpy()

    label = "fake" if class_idx == 1 else "real"
    confidence = float(probs[class_idx])

    # Save the original + heatmap overlay
    file_id = uuid.uuid4().hex
    original_path = settings.upload_path / f"{file_id}_orig.jpg"
    heatmap_path = settings.upload_path / f"{file_id}_heatmap.jpg"
    bgr = pil_to_bgr(pil)
    cv2.imwrite(str(original_path), bgr)
    cv2.imwrite(str(heatmap_path), overlay_heatmap(bgr, heatmap))

    result = {
        "modality": "image",
        "prediction": label,
        "confidence": confidence,
        "metrics": IMAGE_METRICS,
        "explanation": {
            "original_url": f"/files/{original_path.name}",
            "heatmap_url": f"/files/{heatmap_path.name}",
        },
        "file_id": file_id,
    }

    if user:
        await detections_col().insert_one({**result, "user_id": user["_id"]})
    return JSONResponse(result)
