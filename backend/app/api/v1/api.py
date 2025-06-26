# backend/app/api/v1/api.py

from fastapi import APIRouter

# ИСПРАВЛЕНИЕ: Добавляем 'admin' в импорт
from .endpoints import auth, ontology, files, data, admin 

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(ontology.router, prefix="/ontology", tags=["ontology"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(data.router, prefix="/data", tags=["data"])
# Теперь эта строка будет работать, так как 'admin' импортирован
api_router.include_router(admin.router, prefix="/admin", tags=["admin"]) 