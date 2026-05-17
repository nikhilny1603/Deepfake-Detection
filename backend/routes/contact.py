"""POST /api/contact — store contact form submissions."""
from datetime import datetime
from fastapi import APIRouter
from ..database import contact_col
from ..schemas.models import ContactMessage

router = APIRouter(prefix="/api", tags=["contact"])


@router.post("/contact")
async def submit_contact(msg: ContactMessage):
    doc = msg.model_dump()
    doc["created_at"] = datetime.utcnow()
    res = await contact_col().insert_one(doc)
    return {"ok": True, "id": str(res.inserted_id)}
