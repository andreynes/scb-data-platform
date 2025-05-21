from fastapi import FastAPI

app = FastAPI(
    title="SCB DB Backend",
    version="0.1.0", # Начальная версия для MVP
    description="API для доступа к данным и управления системой SCB DB"
)

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Проверяет работоспособность API.
    Возвращает статус "ok", если API работает.
    """
    return {"status": "ok_updated"}

# В будущем здесь будут обработчики startup/shutdown и подключение роутеров
# @app.on_event("startup")
# async def startup_event():
#     # pass # Логика инициализации (например, подключение к БД)
#     print("FastAPI application startup")

# @app.on_event("shutdown")
# async def shutdown_event():
#     # pass # Логика очистки ресурсов
#     print("FastAPI application shutdown")