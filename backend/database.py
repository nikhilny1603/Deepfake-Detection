"""MongoDB connection (Motor async driver)."""
from motor.motor_asyncio import AsyncIOMotorClient
from .config import get_settings

_settings = get_settings()
_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(_settings.MONGODB_URI)
    return _client


def get_db():
    return get_client()[_settings.DB_NAME]


# Convenience collection helpers
def users_col():
    return get_db()["users"]


def detections_col():
    return get_db()["detections"]


def contact_col():
    return get_db()["contact_messages"]
