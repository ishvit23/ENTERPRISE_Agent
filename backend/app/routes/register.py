
from fastapi import APIRouter, HTTPException, Body, Depends
from app.db.database import get_db
from app.db.models import User
from sqlalchemy.orm import Session
from app.auth.password_utils import verify_password
from app.auth.jwt_utils import create_jwt


router = APIRouter()


# Standard email/password login
@router.post("/login")
def login_user(
    email: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="You are not registered with the enterprise. Please contact the admin.")
    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    # Issue JWT
    token = create_jwt(user.email, user.department, user.role or "", getattr(user, "name", ""))
    return {"access_token": token, "token_type": "bearer"}
