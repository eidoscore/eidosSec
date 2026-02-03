from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from app.database import get_db
from app.models import User
from app.schemas import Token, UserResponse, UserCreate
from app.services.auth import auth_service
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/setup", response_model=UserResponse)
async def setup_admin(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Initial setup: creation of the first admin account.
    Only works if the users table is empty.
    """
    result = await db.execute(select(User))
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Setup already completed. Use regular registration or login."
        )
    
    new_user = User(
        email=user_in.email,
        hashed_password=auth_service.get_password_hash(user_in.password),
        role="admin",
        is_active=True
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user
