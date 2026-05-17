"""Authentication endpoints: /register, /login, /me."""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from ..database import users_col
from ..schemas.models import UserCreate, TokenResponse
from .jwt_handler import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_user,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate):
    if await users_col().find_one({"email": payload.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    doc = {
        "email": payload.email,
        "name": payload.name,
        "password": hash_password(payload.password),
    }
    res = await users_col().insert_one(doc)
    user_out = {"id": str(res.inserted_id), "email": payload.email, "name": payload.name}
    token = create_access_token({"sub": payload.email})
    return TokenResponse(access_token=token, user=user_out)


@router.post("/login", response_model=TokenResponse)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = await users_col().find_one({"email": form.username})
    if not user or not verify_password(form.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user["email"]})
    user_out = {"id": str(user["_id"]), "email": user["email"], "name": user["name"]}
    return TokenResponse(access_token=token, user=user_out)


@router.get("/me")
async def me(user=Depends(require_user)):
    return user
