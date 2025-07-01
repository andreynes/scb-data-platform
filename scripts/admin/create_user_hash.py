# scripts/admin/create_user_hash.py
import sys
# Убедимся, что Python может найти наши модули из backend
sys.path.append('.') 

from app.core.security import get_password_hash

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: poetry run python scripts/admin/create_user_hash.py <password>")
        sys.exit(1)
    
    password = sys.argv[1]
    hashed_password = get_password_hash(password)
    print(f"Password: {password}")
    print(f"Hashed password: {hashed_password}")