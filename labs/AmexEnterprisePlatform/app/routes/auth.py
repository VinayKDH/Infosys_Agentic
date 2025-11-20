"""Authentication routes"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.models import LoginRequest, TokenResponse
from app.auth import authenticate_user, create_access_token, get_current_active_user
from datetime import timedelta
from app.config import settings

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(login_request: LoginRequest):
    """Authenticate user and return JWT token"""
    user = authenticate_user(login_request.username, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    """Get current user information"""
    return {
        "username": current_user["username"],
        "role": current_user["role"],
        "customer_id": current_user.get("customer_id")
    }

