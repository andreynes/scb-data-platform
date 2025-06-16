# backend/app/api/v1/endpoints/auth.py
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any

from app.schemas.token_schemas import TokenSchema
from app.schemas.user_schemas import UserSchema, UserCreateSchema
from app.services.auth_service import AuthService
from app.api.v1.deps import get_auth_service, get_current_active_user
from app.services.exceptions import UserAlreadyExistsError, InvalidCredentialsError

router = APIRouter()
logger = logging.getLogger(__name__)

# ПУТЬ ИЗМЕНЕН: было "/auth/token"
@router.post("/token", response_model=TokenSchema, summary="Получение JWT токена")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Стандартный эндпоинт OAuth2 для получения токена по имени пользователя и паролю.
    Данные передаются в формате `application/x-www-form-urlencoded`.
    """
    try:
        user = await auth_service.authenticate_user(
            username=form_data.username, password=form_data.password
        )
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль (пользователь не найден)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Исправляем вызов функции для создания токена
    access_token = auth_service.create_access_token_for_user(user=user)
    return TokenSchema(access_token=access_token, token_type="bearer")

# ПУТЬ ИЗМЕНЕН: было "/auth/register"
@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED, summary="Регистрация нового пользователя")
async def register_user(
    user_in: UserCreateSchema,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Создает нового пользователя.
    """
    try:
        created_user = await auth_service.create_user(user_in=user_in)
        return UserSchema.model_validate(created_user)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error during user registration: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка на сервере при регистрации пользователя.",
        )

# ПУТЬ ИЗМЕНЕН: было "/users/me"
@router.get("/me", response_model=UserSchema, summary="Получение данных текущего пользователя")
async def read_users_me(
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Возвращает данные текущего аутентифицированного пользователя.
    """
    return current_user