"""GET /api/history — list past detections for the logged-in user."""
from fastapi import APIRouter, Depends
from ..database import detections_col
from ..auth.jwt_handler import require_user

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history")
async def history(user=Depends(require_user)):
    cursor = (
        detections_col()
        .find({"user_id": user["_id"]})
        .sort("created_at", -1)
        .limit(100)
    )
    items = []
    async for d in cursor:
        d["_id"] = str(d["_id"])
        items.append(d)
    return {"items": items}
