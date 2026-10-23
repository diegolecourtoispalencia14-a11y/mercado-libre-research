from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.config import settings
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.security_middleware import brute_force_protector

router = APIRouter(prefix="/auth", tags=["auth"])
security_scheme = HTTPBearer(auto_error=False)


# --- Pydantic Schemas ---
class LoginRequest(BaseModel):
    username: str
    password: str
    honeypot: Optional[str] = None  # Bot protection field


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: str
    is_active: bool


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# --- Seed Initial Admin ---
def ensure_admin_user(db: Session) -> User:
    """Ensures at least one administrator user exists."""
    user = db.query(User).filter(User.username == settings.admin_username).first()
    if not user:
        p_hash, salt = hash_password(settings.admin_password)
        user = User(
            username=settings.admin_username,
            email=settings.admin_email,
            password_hash=p_hash,
            salt=salt,
            role="admin",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


# --- Auth Dependency ---
def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Validates the bearer token and returns the authenticated user.
    """
    if not credentials or not credentials.credentials:
        if not settings.auth_enabled:
            return User(
                id=1,
                username="admin",
                email="admin@flamante.lab",
                role="admin",
                is_active=True,
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida. Token no proporcionado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada o token no válido. Inicia sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token malformado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.username == username, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo o no encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# --- Endpoints ---
@router.post("/login", response_model=LoginResponse)
def login(
    body: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    # 1. Honeypot Anti-Bot check (Fail-Closed)
    if body.honeypot:
        # Silently reject bot submissions
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solicitud no válida.")

    client_ip = request.client.host if request.client else "unknown"
    brute_key = f"{client_ip}:{body.username}"

    # 2. Brute Force Lockout check
    is_locked, remaining_sec = brute_force_protector.is_locked(brute_key)
    if is_locked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Demasiados intentos fallidos. Acceso bloqueado por {remaining_sec} segundos.",
            headers={"Retry-After": str(remaining_sec)},
        )

    # Make sure default admin exists if DB is newly provisioned
    ensure_admin_user(db)

    # 3. Find User
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.salt, user.password_hash) or not user.is_active:
        # Record failed attempt
        count, lock_time = brute_force_protector.record_failure(brute_key)
        if lock_time > 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Límite de 5 intentos excedido. Bloqueo temporal activado por {lock_time}s.",
                headers={"Retry-After": str(lock_time)},
            )
        # Generic message anti-enumeration (OWASP Top 10)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales no válidas. Verifica tus datos de acceso.",
        )

    # 4. Successful login: Reset failures
    brute_force_protector.reset(brute_key)

    # 5. Issue token
    token = create_access_token({
        "sub": user.username,
        "user_id": user.id,
        "role": user.role,
    })

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Sesión cerrada correctamente"}
