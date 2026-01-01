from fastapi import APIRouter, HTTPException, Body, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.auth.password_utils import hash_password
import secrets

router = APIRouter()

@router.post("/auth/request-password-reset")
def request_password_reset(email: str = Body(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    # Generate a reset token (in production, store in DB and email to user)
    token = secrets.token_urlsafe(32)
    # For demo: just return the token (in real app, email it)
    return {"reset_token": token}

@router.post("/auth/reset-password")
def reset_password(email: str = Body(...), token: str = Body(...), new_password: str = Body(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    # In production, verify token matches what was sent/stored
    user.password_hash = hash_password(new_password)
    db.commit()
    return {"status": "password reset"}
