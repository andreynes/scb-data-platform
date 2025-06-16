from fastapi import APIRouter

# Импортируем роутеры из всех модулей эндпоинтов
from .endpoints import auth, data, ontology, files

# Переименовываем переменную, чтобы она совпадала с импортом в main.py
api_router_v1 = APIRouter()

# Подключаем роутеры с префиксами и тегами для группировки в документации
api_router_v1.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router_v1.include_router(data.router, prefix="/data", tags=["Data Query"])
api_router_v1.include_router(ontology.router, prefix="/ontology", tags=["Ontology"])
api_router_v1.include_router(files.router, prefix="/files", tags=["File Upload"])
# api_router_v1.include_router(admin.router, prefix="/admin", tags=["Admin"]) # Правильно, что это закомментировано