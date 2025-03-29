# Hàm chuẩn hóa phản hồi
from typing import Any

from fastapi import HTTPException


def format_response(status_code: int, message: str, data: Any = None):
    return {"status_code": status_code, "message": message, "data": data}


class CustomException(HTTPException):
    def __init__(self, status_code: int, message: str, data: Any = None):
        detail = {"status_code": status_code, "message": message, "data": data}
        super().__init__(status_code=status_code, detail=detail)
