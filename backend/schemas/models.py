"""Pydantic request / response schemas."""
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


# ---------- Auth ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# ---------- Detection ----------
class DetectionResult(BaseModel):
    modality: str                       # image | video | audio | text
    prediction: str                     # "real" | "fake"
    confidence: float                   # 0.0 – 1.0
    metrics: dict                       # accuracy, precision, recall, f1
    explanation: dict                   # modality-specific data (e.g. heatmap path)
    file_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TextDetectRequest(BaseModel):
    text: str = Field(min_length=1)


class TextRewriteRequest(BaseModel):
    text: str = Field(min_length=1)


class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str
