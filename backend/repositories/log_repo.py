# backend/repositories/log_repo.py

from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any

class LogRepo:
    """
    Репозиторий для работы с логами действий пользователей.
    В MVP может быть заглушкой, но должен существовать для корректной работы зависимостей.
    """
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = self.db.get_collection("user_activity_logs")

    async def log_data_request(self, user_id: str, request_details: Dict, involved_doc_ids: List[str]) -> None:
        # В MVP эта функция может ничего не делать
        pass

    async def get_file_popularity_scores(self, time_period_days: int = 30) -> Dict[str, int]:
        # В MVP возвращаем пустой словарь, т.к. логика еще не реализована
        return {}