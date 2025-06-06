# backend/app/api/v1/api.py
from fastapi import APIRouter

# Импортируем существующие роутеры
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import ontology
# from app.api.v1.endpoints import files # Оставим, если он у вас уже есть и работает для загрузки файлов
# from app.api.v1.endpoints import admin # Если есть

# --- НОВЫЙ ИМПОРТ ДЛЯ РОУТЕРА ДАННЫХ ---
from app.api.v1.endpoints import data 
# --- КОНЕЦ НОВОГО ИМПОРТА ---

api_router_v1 = APIRouter() 

# Подключаем существующие роутеры
api_router_v1.include_router(auth.router, prefix="/auth", tags=["Authentication"]) # Рекомендую более описательные теги
api_router_v1.include_router(ontology.router, prefix="/ontology", tags=["Ontology Management"])

# --- ПОДКЛЮЧЕНИЕ НОВОГО РОУТЕРА ДАННЫХ ---
api_router_v1.include_router(data.router, prefix="/data", tags=["Data Access (Warehouse)"]) 
# --- КОНЕЦ ПОДКЛЮЧЕНИЯ ---

# Если у вас есть другие роутеры, они остаются здесь:
# if 'files' in locals(): # Проверка, существует ли импорт files, чтобы не было ошибки если его нет
#     api_router_v1.include_router(files.router, prefix="/files", tags=["File Management"])
# if 'admin' in locals():
#     api_router_v1.include_router(admin.router, prefix="/admin", tags=["Administration"])