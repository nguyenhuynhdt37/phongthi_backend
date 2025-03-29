from typing import Callable, List, Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer

from app.libs.auth.jwt import verify_token

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login") # vô dụng rồi


def get_current_user(request: Request):
    token = request.cookies.get("access_token")  # Lấy token từ cookie
    if not token:
        raise HTTPException(status_code=401, detail="Token not found in cookies")
    try:
        return verify_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_role(required_roles: Optional[List[str]] = None) -> Callable:
    def role_checker(
        current_user: dict = Depends(get_current_user),
    ):  # ✅ Dependency hợp lệ
        if not required_roles:  # Nếu không yêu cầu quyền, trả về user luôn
            return current_user
        user_roles = current_user.get("role", [])
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(status_code=403, detail="Permission denied")
        return current_user

    return Depends(role_checker)  # ✅ Trả về một dependency hợp lệ
