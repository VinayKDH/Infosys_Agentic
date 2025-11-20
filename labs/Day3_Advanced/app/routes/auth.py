from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Simplified user database (use proper DB in production)
# Passwords will be hashed lazily on first login
USERS_DB = {
    "admin": {
        "username": "admin",
        "password": "admin123",  # Plain password, will be hashed on first use
        "role": "admin"
    },
    "user": {
        "username": "user",
        "password": "user123",  # Plain password, will be hashed on first use
        "role": "user"
    }
}

# Cache for hashed passwords
_hashed_passwords = {}

def _get_hashed_password(username: str) -> str:
    """Get hashed password for user, hashing on first access"""
    if username not in _hashed_passwords:
        if username in USERS_DB:
            try:
                _hashed_passwords[username] = pwd_context.hash(USERS_DB[username]["password"])
            except Exception as e:
                # Fallback: use a simple hash if bcrypt fails
                import hashlib
                _hashed_passwords[username] = hashlib.sha256(USERS_DB[username]["password"].encode()).hexdigest()
        else:
            return None
    return _hashed_passwords[username]

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """Login endpoint"""
    user = USERS_DB.get(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    hashed_password = _get_hashed_password(username)
    if not hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Verify password
    try:
        if not pwd_context.verify(password, hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
    except Exception as e:
        # Fallback verification if bcrypt fails
        import hashlib
        if hashed_password != hashlib.sha256(password.encode()).hexdigest():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
    
    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}

