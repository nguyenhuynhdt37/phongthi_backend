from io import BytesIO
from typing import List
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.libs.auth.dependencies import require_role
from app.repositories.excel import handleExcel

router = APIRouter(prefix="/excel", tags=["Excel"])


@router.post("/upload")
async def upload_file(
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=require_role(["admin"]),
):
    return handleExcel(files)
