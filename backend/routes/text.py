"""POST /api/detect/text and /api/text/humanize — AI text detection + rewriter."""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
import torch

from ..config import get_settings
from ..auth.jwt_handler import get_current_user
from ..database import detections_col
from ..models.text_model import TextDeepfakeModel, humanize_text
from ..schemas.models import TextDetectRequest, TextRewriteRequest

router = APIRouter(prefix="/api", tags=["detection"])
settings = get_settings()

_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
_MODEL = TextDeepfakeModel(settings.models_path / "text_model.pth", device=_DEVICE)

TEXT_METRICS = {"accuracy": 0.95, "precision": 0.95, "recall": 0.96, "f1": 0.95}


@router.post("/detect/text")
async def detect_text(payload: TextDetectRequest, user=Depends(get_current_user)):
    p_ai, p_human = _MODEL.predict(payload.text)
    sentence_scores = _MODEL.highlight_ai_tokens(payload.text)
    label = "fake" if p_ai >= 0.5 else "real"   # "fake" == AI-generated
    confidence = float(max(p_ai, p_human))

    result = {
        "modality": "text",
        "prediction": label,
        "confidence": confidence,
        "metrics": TEXT_METRICS,
        "explanation": {
            "ai_percent": round(p_ai * 100, 2),
            "human_percent": round(p_human * 100, 2),
            "sentences": sentence_scores,
        },
    }

    if user:
        await detections_col().insert_one(
            {**result, "user_id": user["_id"], "input_text": payload.text[:1000]}
        )
    return JSONResponse(result)


@router.post("/text/humanize")
async def humanize(payload: TextRewriteRequest):
    rewritten = humanize_text(payload.text)
    p_ai_before, _ = _MODEL.predict(payload.text)
    p_ai_after, _ = _MODEL.predict(rewritten)
    return {
        "original": payload.text,
        "rewritten": rewritten,
        "ai_percent_before": round(p_ai_before * 100, 2),
        "ai_percent_after": round(p_ai_after * 100, 2),
    }
