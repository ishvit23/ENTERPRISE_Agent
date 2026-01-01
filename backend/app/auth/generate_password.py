import random
import string

def generate_password(length=10, max_length=72):
    # Use only ASCII characters to avoid multi-byte issues
    length = min(length, max_length)
    chars = string.ascii_letters + string.digits + '!@#$%^&*()-_=+[]{};:,.<>?/'
    # Ensure at least one lowercase, one uppercase, one digit, one special
    while True:
        password = ''.join(random.choice(chars) for _ in range(length))
        if (any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in '!@#$%^&*()-_=+[]{};:,.<>?/' for c in password)):
            # Ensure password is ASCII and ≤72 bytes
            password_bytes = password.encode('ascii', errors='ignore')[:max_length]
            return password_bytes.decode('ascii', errors='ignore')
