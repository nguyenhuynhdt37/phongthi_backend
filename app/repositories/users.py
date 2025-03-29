from datetime import datetime, timedelta
import json
import httpx
from email.message import EmailMessage
from ipaddress import ip_address
import random
import aiosmtplib
from fastapi import HTTPException, Path, Request, Response
import jwt
from sqlalchemy import and_, insert, null, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.libs.auth.jwt import create_access_token
from app.libs.directory.index import get_image_directory
from app.libs.formart.response import CustomException, format_response
from app.libs.template.render import render_template
from app.models.models import Tblrole, Tblsesson, Tbluser
from app.schemas import user
from app.schemas.user import LoginUser
import os
from dotenv import load_dotenv

load_dotenv()
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
MAIL_USERNAME = os.getenv("EMAIL_SENDER", "")
MAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))

# async def check_email_async(email: str, db: AsyncSession) -> dict:
#     email = email.lower()
#     exists = (await db.execute(select(TblUser).filter(TblUser.email == email))).scalar_one_or_none()

#     if exists:
#         raise HTTPException(status_code=400, detail="Email đã tồn tại")

#     return {"message": "Email hợp lệ"}


async def send_email(to_email: str, subject: str, template_name: str, **context):
    # Render template
    body = render_template(template_name, **context)

    # Tạo email message
    message = EmailMessage()
    # người gửi, người nhận, tiêu đề, nội dung
    message["From"] = MAIL_USERNAME
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body, subtype="html")  # Sử dụng HTML content

    # Gửi email
    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            username=MAIL_USERNAME,
            password=MAIL_PASSWORD,
            start_tls=True,
        )
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")


async def get_location_from_ip(ip: str):
    url = f"http://ip-api.com/json/{ip}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
    return {
        "ip": ip,
        "country": data.get("country"),
        "region": data.get("regionName"),
        "city": data.get("city"),
        "lat": data.get("lat"),
        "lon": data.get("lon"),
        "isp": data.get("isp"),
    }


async def login_async(
    schema: LoginUser, db: AsyncSession, response: Response, request: Request
) -> dict:
    try:
        result = await db.execute(
            select(Tbluser)
            .options(selectinload(Tbluser.role))  # Load quan hệ role
            .filter(
                and_(
                    Tbluser.email == schema.email,
                    Tbluser.password == schema.password,
                )
            )
        )
        user = result.scalars().first()
        if not user:
            raise CustomException(status_code=404, message="Tài khoản không tồn tại")
        device_info = request.headers.get("User-Agent", "unknown")
        client_ip = request.headers.get(
            "x-forwarded-for", request.client.host if request.client else "unknown"
        )  # Lấy IP client
        location = await get_location_from_ip(client_ip)
        user_data = {
            "id": user.id,
            "email": user.email,
            "role": user.role.role_name,
        }
        access_token = create_access_token(
            user_data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        # kiểm tra nó có đáng tin cậy không

        # trush_device = await db.execute(
        #     select(Tblsesson).filter(
        #         and_(
        #             Tblsesson.user_id == user.id,
        #             Tblsesson.device_info == device_info,
        #             Tblsesson.is_trusted == True,
        #         )
        #     )
        # )
        # is_trusted: bool = trush_device.scalars().first() is not None
        # session_data = {
        #     "user_id": user.id,
        #     "token": access_token,
        #     "device_info": device_info,
        #     "ip_address": ip_address,
        #     "login_time": datetime.utcnow(),
        #     "is_active": is_trusted,  # Active ngay nếu trusted
        #     "is_trusted": is_trusted,
        #     "location_city": location.get("city"),
        #     "location_country": location.get("country"),
        # }
        # if not is_trusted:
        #     approval_code = random.randint(100000, 999999)  # Mã 6 ký tự ngẫu nhiên
        #     session_data["approval_code"] = approval_code
        #     session_data["approval_expires"] = datetime.utcnow() + timedelta(minutes=15)
        #     if user.email:
        #         await send_email(
        #             "nguyenhuynhdt37@gmail.com",
        #             "Phê duyệt thiết bị đăng nhập",
        #             "email_template.html",
        #             approval_code=approval_code,
        #             email=user.email,
        #             device_info=device_info,
        #             ip_address=ip_address,
        #         )
        # await db.execute(insert(Tblsesson).values(session_data))
        # await db.commit()
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            path="/",
            max_age=10 * 24 * 60 * 60,  # 10 ngày (giống C#)
        )
        return format_response(status_code=200, message="Login success", data=user_data)
    except Exception as e:
        await db.rollback()
        raise


async def get_info_async(request: Request, db: AsyncSession, current_user: dict):
    try:
        result = await db.execute(
            select(Tbluser).join(Tblrole).filter(Tbluser.id == current_user.get("user"))
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=404, detail=format_response(404, "User not found")
            )
        user.avatar = get_image_directory(user.avatar) if user.avatar else None
        user.password = None  # Không trả mật khẩu về
        return format_response(
            data=user, status_code=200, message="Get user info success"
        )
    except Exception as e:
        await db.rollback()
        raise
