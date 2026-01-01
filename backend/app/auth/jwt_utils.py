"""
JWT utilities for validation and extraction of user info.
"""
from jose import jwt, JWTError
from fastapi import Request, HTTPException, status, Depends
from starlette.config import Config

config = Config('.env')
JWT_SECRET = config('JWT_SECRET', cast=str, default='supersecret')
JWT_ALGORITHM = 'HS256'


# Dependency to extract and validate JWT from Authorization header
def get_current_user(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing or invalid token')
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

# Function to create JWT for a user
def create_jwt(email: str, department: str, role: str, name: str = "") -> str:
    payload = {
        "sub": email,
        "department": department,
        "role": role,
        "name": name
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token
