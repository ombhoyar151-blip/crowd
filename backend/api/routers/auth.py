from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dependencies import get_current_user, get_db
from backend.db.models import UserORM
from backend.schemas.auth import LoginRequest, TokenResponse, UserResponse
from config.settings import Settings

router = APIRouter(prefix="/auth", tags=["auth"])
settings = Settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


@router.post("/token", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(UserORM).where(UserORM.username == body.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user.username)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def me(user: UserORM = Depends(get_current_user)):
    return UserResponse(id=user.id, username=user.username, role=user.role, is_active=user.is_active)
