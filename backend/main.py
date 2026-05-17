"""
FastAPI application entrypoint.

Run with:
    uvicorn backend.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .auth.routes import router as auth_router
from .routes.image import router as image_router
from .routes.video import router as video_router
from .routes.audio import router as audio_router
from .routes.text import router as text_router
from .routes.contact import router as contact_router
from .routes.history import router as history_router

settings = get_settings()

app = FastAPI(
    title="Deepfake Detection API",
    description="Detects deepfake content across image, video, audio, and text.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded / generated artefacts (heatmaps, key frames, waveforms)
app.mount("/files", StaticFiles(directory=settings.UPLOAD_DIR), name="files")

# Routers
app.include_router(auth_router)
app.include_router(image_router)
app.include_router(video_router)
app.include_router(audio_router)
app.include_router(text_router)
app.include_router(contact_router)
app.include_router(history_router)


@app.get("/")
async def root():
    return {
        "name": "Deepfake Detection API",
        "version": "1.0.0",
        "endpoints": [
            "/api/auth/register",
            "/api/auth/login",
            "/api/auth/me",
            "/api/detect/image",
            "/api/detect/video",
            "/api/detect/audio",
            "/api/detect/text",
            "/api/text/humanize",
            "/api/contact",
            "/api/history",
        ],
        "docs": "/docs",
    }


@app.get("/api/health")
async def health():
    return {"status": "ok"}
