"""
API dependencies for authentication.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.core.database import get_db
from app.core.config import settings
from app.models.user import AdminUser, AppUser

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        if not username or not role:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if role == "admin":
        user = db.query(AdminUser).filter(
            AdminUser.username == username, AdminUser.is_active == True
        ).first()
    else:
        user = db.query(AppUser).filter(
            AppUser.email == username, AppUser.is_active == True
        ).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")
    return {"role": role, "user": user}


def get_current_admin(
    current=Depends(get_current_user),
) -> AdminUser:
    if current["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current["user"]


def get_current_staff_or_admin(
    current=Depends(get_current_user),
):
    if current["role"] not in {"admin", "staff"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Staff access required")
    return current


def get_current_any_user(
    current=Depends(get_current_user),
):
    if current["role"] not in {"admin", "staff", "student"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return current
