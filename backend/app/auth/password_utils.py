# Password hashing utilities for user authentication
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # bcrypt only supports passwords up to 72 bytes
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')[:72]
    else:
        password_bytes = password[:72]
    # Always decode to ASCII, ignoring errors, to avoid multi-byte issues
    safe_password = password_bytes.decode('ascii', errors='ignore')
    return pwd_context.hash(safe_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # bcrypt only supports passwords up to 72 bytes
    if isinstance(plain_password, str):
        password_bytes = plain_password.encode('utf-8')[:72]
    else:
        password_bytes = plain_password[:72]
    safe_password = password_bytes.decode('ascii', errors='ignore')
    return pwd_context.verify(safe_password, hashed_password)
