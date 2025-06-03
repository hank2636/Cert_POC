'''
主程式
All API : Cert_POC/backend/app/api/router.py
允許跨域請求: .env 的 BACKEND_CORS_ORIGINS
API URL path 開頭: .env 的 API_V1_STR
'''

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.all_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
# 將圖片路徑一併納入服務中供前端取用
img_path = "/home/omni/Cert_POC/frontend/public/production_picture"
app.mount(img_path, StaticFiles(directory=img_path), name="production_picture")
# app.mount("/production_picture", StaticFiles(directory="/home/omni/Cert_POC/frontend/public/production_picture"), name="production_picture")

