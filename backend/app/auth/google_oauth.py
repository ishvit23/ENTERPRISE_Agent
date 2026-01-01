"""
Handles Google OAuth authentication and JWT issuance.
"""
from fastapi import APIRouter, Request, HTTPException, Depends

from fastapi.responses import RedirectResponse
from jose import jwt
import os
import requests
from starlette.config import Config

from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from datetime import datetime, timedelta
from app.db.database import SessionLocal
from app.db.models import User

router = APIRouter()

# Load secrets from environment or .env
config = Config('.env')
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID', cast=str, default='')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET', cast=str, default='')
JWT_SECRET = config('JWT_SECRET', cast=str, default='supersecret')
JWT_ALGORITHM = 'HS256'

@router.get('/auth/google/login')
def login():
    # Redirect to Google OAuth consent screen
    return RedirectResponse(
        f"https://accounts.google.com/o/oauth2/v2/auth?client_id={GOOGLE_CLIENT_ID}&response_type=code&scope=openid%20email%20profile&redirect_uri=http://localhost:8000/auth/google/callback"
    )


@router.get('/auth/google/callback')
def callback(request: Request):
    # Get code from query params
    code = request.query_params.get('code')
    if not code:
        return JSONResponse({"error": "Missing code in callback."}, status_code=400)

    # Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    redirect_uri = "http://localhost:8000/auth/google/callback"
    data = {
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    token_resp = requests.post(token_url, data=data)
    if not token_resp.ok:
        return JSONResponse({"error": "Failed to exchange code for token."}, status_code=400)
    tokens = token_resp.json()
    id_token = tokens.get('id_token')
    access_token = tokens.get('access_token')
    if not id_token or not access_token:
        return JSONResponse({"error": "Missing tokens from Google."}, status_code=400)

    # Get user info
    userinfo_resp = requests.get(
        'https://openidconnect.googleapis.com/v1/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    if not userinfo_resp.ok:
        return JSONResponse({"error": "Failed to fetch user info."}, status_code=400)
    userinfo = userinfo_resp.json()
    email = userinfo.get('email')
    name = userinfo.get('name', '')

    # Check DB for user registration

    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        db.close()
        # Redirect to frontend with error for unregistered users
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return RedirectResponse(f"{frontend_url}/?error=not_registered")
    department = user.department
    role = user.role if user.role else ''
    db.close()

    jwt_token = create_jwt(email, department, role, name)

    # Redirect to frontend with token as query param (or return as JSON for API clients)
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    return RedirectResponse(f"{frontend_url}/?token={jwt_token}")

# Utility to create JWT
def create_jwt(user_email: str, department: str, role: str, name: str = ""):
    payload = {
        "sub": user_email,
        "department": department,
        "role": role,
        "name": name,
        "exp": datetime.utcnow() + timedelta(hours=12)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
