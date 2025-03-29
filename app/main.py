from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from h11 import Request
from sqlalchemy import true
from app.api.routers.v1.auth import router as auth_router
from app.api.routers.v1.excel import router as excel_router
from app.api.routers.v1.users import router as users_router
import os
from starlette.middleware.sessions import SessionMiddleware

load_dotenv()
HOST: str = os.getenv("HOST", "localhost")
PORT: int = int(os.getenv("PORT", 8000))


app = FastAPI(debug=True)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(excel_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.add_middleware(SessionMiddleware, secret_key="fsdfsdfsd3333222xx1")
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):  # Nếu đã là dict, giữ nguyên
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})


@app.get("/", tags=["Root"])
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        reload=True,
        log_level="debug",
        workers=1,
        limit_concurrency=1,
        limit_max_requests=1,
    )
