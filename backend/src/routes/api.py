from fastapi import APIRouter
from backend.src.routes.analyzer import router as analyzer_router

api_router = APIRouter()
api_router.include_router(analyzer_router)
