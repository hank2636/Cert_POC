from app.api.routes import cart, login, logout, production, users
from app.core.config import settings
from fastapi import APIRouter

api_router = APIRouter()

if settings.ENVIRONMENT == "local":
    api_router.include_router(login.router)
    api_router.include_router(logout.router)
    api_router.include_router(users.router)
    api_router.include_router(production.router)
    api_router.include_router(cart.router)
