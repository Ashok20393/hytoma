from cmath import e
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime,timedelta
from fastapi import Request, HTTPException, Depends, Cookie

from fastapi.security import HTTPBearer
from jose import JWTError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "044448e3e29843c30534c0aff193c3b6a5a7c55e1e43d39f7faf3f3608004898"
ALGORITHM = "HS256"

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=8)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Cookie(None)):
   

    if not token:
        raise HTTPException(status_code=401, detail="Not logged in")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        return payload
    except JWTError as e:
        
        raise HTTPException(status_code=401, detail="Invalid token")



def require_admin(user=Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user