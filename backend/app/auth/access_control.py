"""
Department-based access control utilities.
"""
from fastapi import HTTPException, status, Depends

def require_department(department: str):
    def checker(user=Depends(lambda request: request.state.user)):
        if user.get('department') != department:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied for department')
        return user
    return checker
