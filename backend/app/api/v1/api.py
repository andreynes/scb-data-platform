# backend/app/api/v1/api.py
from fastapi import APIRouter

from backend.app.api.v1.endpoints import ontology # ДОБАВИТЬ ЭТОТ ИМПОРТ
# from backend.app.api.v1.endpoints import auth  # Пример для будущего
# from backend.app.api.v1.endpoints import data # Пример для будущего

api_router_v1 = APIRouter()

# Подключаем роутеры из подмодулей endpoints
api_router_v1.include_router(ontology.router, prefix="/ontology", tags=["ontology"]) # ДОБАВИТЬ ЭТУ СТРОКУ
# api_router_v1.include_router(auth.router, prefix="/auth", tags=["auth"]) # Пример для будущего
# api_router_v1.include_router(data.router, prefix="/data", tags=["data"]) # Пример для будущего