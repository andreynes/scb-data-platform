# scripts/create_admin.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

# --- НАСТРОЙКИ (поменяйте, если нужно) ---
MONGO_URL = "mongodb://andrewkrylov:12345dbscb@localhost:27017/"
MONGO_DB_NAME = "scb_db"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "12345dbscb" 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def create_admin_user():
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[MONGO_DB_NAME]
    users_collection = db.users
    
    print(f"Checking for user '{ADMIN_USERNAME}'...")
    existing_user = await users_collection.find_one({"username": ADMIN_USERNAME})
    
    if existing_user:
        print(f"User '{ADMIN_USERNAME}' already exists. Updating password.")
        hashed_password = get_password_hash(ADMIN_PASSWORD)
        await users_collection.update_one(
            {"username": ADMIN_USERNAME},
            {"$set": {"hashed_password": hashed_password}}
        )
        print("Password updated successfully.")
    else:
        print(f"User '{ADMIN_USERNAME}' not found. Creating new user.")
        hashed_password = get_password_hash(ADMIN_PASSWORD)
        user_data = {
            "username": ADMIN_USERNAME,
            "email": "admin@example.com",
            "hashed_password": hashed_password,
            "is_active": True,
            "is_superuser": True,
            "role": "admin"
        }
        await users_collection.insert_one(user_data)
        print("Admin user created successfully.")
        
    client.close()

if __name__ == "__main__":
    asyncio.run(create_admin_user())