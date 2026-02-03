from datetime import datetime, timedelta
from typing import Optional, List
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class AuthService:
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    async def get_current_user(
        self, 
        token: str = Depends(oauth2_scheme), 
        db: AsyncSession = Depends(get_db)
    ) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
            
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user is None:
            raise credentials_exception
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
            
        return user

    def check_permissions(self, allowed_roles: List[str]):
        """Dependency factory for role-based access"""
        async def role_checker(current_user: User = Depends(self.get_current_user)):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
            return current_user
        return role_checker

auth_service = AuthService()
