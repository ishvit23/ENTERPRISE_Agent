from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.auth.jwt_utils import get_current_user
from app.auth.password_utils import hash_password
from app.auth.generate_password import generate_password

router = APIRouter()

ADMIN_EMAIL = "dhruvkhajuria23@gmail.com"

# Dependency to check admin

def require_admin(user=Depends(get_current_user)):
    if user.get("sub") != ADMIN_EMAIL or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required.")
    return user

@router.post("/admin/users/add")
def add_user(
    email: str = Body(...),
    name: str = Body(...),
    department: str = Body(...),
    role: str = Body(...),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="User already exists.")
    password = generate_password()
    password_hash = hash_password(password)
    user = User(email=email, department=department, role=role, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"status": "created", "user_id": user.id, "password": password}

@router.get("/admin/users/list")
def list_users(db: Session = Depends(get_db), admin=Depends(require_admin)):
    users = db.query(User).all()
    return [
        {"id": u.id, "email": u.email, "name": getattr(u, "name", ""), "department": u.department, "role": u.role}
        for u in users
    ]

@router.delete("/admin/users/delete/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    db.delete(user)
    db.commit()
    return {"status": "deleted"}

@router.put("/admin/users/edit/{user_id}")
def edit_user(
    user_id: int,
    department: str = Body(None),
    role: str = Body(None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if department:
        user.department = department
    if role:
        user.role = role
    db.commit()
    return {"status": "updated"}
