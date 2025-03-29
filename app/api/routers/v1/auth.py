from app.core.database import get_db
from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.libs.auth.dependencies import require_role
from app.libs.checkSyntax import check_is_email
from app.repositories.users import get_info_async, login_async
from app.schemas.user import LoginUser, getInfoUser

# from app.repositories.users import check_email_async


router = APIRouter(prefix="/auth", tags=["Auth"])


# @router.get("/check_email", status_code=status.HTTP_200_OK)
# async def check_email(email: str = Query(...), db: AsyncSession = Depends(get_db)):
#     if not check_is_email(email):
#         raise HTTPException(status_code=400, detail="Email không hợp lệ")
#     return 1


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    request: Request,
    schema: LoginUser = Body(...),
    db: AsyncSession = Depends(get_db),
):
    return await login_async(schema, db, response, request)


@router.get("/get-info", status_code=status.HTTP_200_OK)
async def get_info(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=require_role(),
):
    return await get_info_async(request, db, current_user)
