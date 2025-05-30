# backend/app/api/v1/api.py
from fastapi import APIRouter

from app.api.v1.endpoints import auth, ontology
# --- НОВЫЙ ИМПОРТ ---
from app.api.v1.endpoints import files 
# --- КОНЕЦ НОВОГО ИМПОРТА ---

api_router_v1 = APIRouter() 

api_router_v1.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router_v1.include_router(ontology.router, prefix="/ontology", tags=["ontology"])
# --- ПОДКЛЮЧЕНИЕ НОВОГО РОУТЕРА ---
api_router_v1.include_router(files.router, prefix="", tags=["files"]) 
# --- КОНЕЦ ПОДКЛЮЧЕНИЯ ---