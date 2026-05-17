"""POST /api/detect/video — frame-by-frame detection + LSTM aggregation."""
from pathlib import Path
import uuid
import cv2
import torch
import torch.nn.functional as F
from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from PIL import Image
import numpy as np

from ..config import get_settings
from ..auth.jwt_handler import get_current_user
from ..database import detections_col
from ..models.video_model import load_video_model
from ..utils.preprocessing import preprocess_image
from ..utils.video_utils import extract_frames, save_frame_thumbnails

router = APIRouter(prefix="/api/detect", tags=["detection"])
settings = get_settings()

_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
_MODEL = load_video_model(settings.models_path / "video_model.pth", device=_DEVICE)

VIDEO_METRICS = {"accuracy": 0.89, "precision": 0.88, "recall": 0.90, "f1": 0.89}
MAX_FRAMES = 16


@router.post("/video")
async def detect_video(file: UploadFile = File(...), user=Depends(get_current_user)):
    file_id = uuid.uuid4().hex
    raw_path = settings.upload_path / f"{file_id}_{file.filename}"
    with open(raw_path, "wb") as f:
        f.write(await file.read())

    frames_bgr = extract_frames(raw_path, max_frames=MAX_FRAMES)
    if not frames_bgr:
        return JSONResponse({"error": "Could not extract any frames"}, status_code=400)

    # Pre-process each frame to a tensor
    tensors = []
    for fr in frames_bgr:
        rgb = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
        tensors.append(preprocess_image(Image.fromarray(rgb))[0])
    seq = torch.stack(tensors).unsqueeze(0).to(_DEVICE)  # [1, T, 3, H, W]

    with torch.no_grad():
        logits = _MODEL(seq)
        probs = F.softmax(logits, dim=1)[0].cpu().numpy()
        per_frame_fake = _MODEL.per_frame_logits(seq)[0].cpu().numpy()  # [T]

    class_idx = int(np.argmax(probs))
    label = "fake" if class_idx == 1 else "real"
    confidence = float(probs[class_idx])

    # Highlight the top-3 most influential frames toward the predicted class
    if class_idx == 1:
        top_idx = list(np.argsort(per_frame_fake)[::-1][:3])
    else:
        top_idx = list(np.argsort(per_frame_fake)[:3])

    thumbs = save_frame_thumbnails(frames_bgr, settings.upload_path, file_id, top_idx)
    thumb_urls = [f"/files/{Path(p).name}" for p in thumbs]

    result = {
        "modality": "video",
        "prediction": label,
        "confidence": confidence,
        "metrics": VIDEO_METRICS,
        "explanation": {
            "key_frame_urls": thumb_urls,
            "frame_scores": [float(x) for x in per_frame_fake.tolist()],
        },
        "file_id": file_id,
    }

    if user:
        await detections_col().insert_one({**result, "user_id": user["_id"]})
    return JSONResponse(result)
