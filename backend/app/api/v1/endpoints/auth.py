# backend/app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm 
from typing import Any

from app.schemas.token_schemas import TokenSchema
from app.schemas.user_schemas import UserSchema, UserCreateSchema
from app.services.auth_service import AuthService
from app.api.v1.deps import get_auth_service, get_current_active_user 
from app.services.exceptions import UserAlreadyExistsError, InvalidCredentialsError

router = APIRouter()

@router.post("/auth/token", response_model=TokenSchema, summary="Получение JWT токена")
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
    
    if not user: # Дополнительная проверка, хотя authenticate_user должен выбросить исключение
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль (пользователь не найден)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token_for_user(user=user)
    return TokenSchema(access_token=access_token, token_type="bearer")

@router.post("/auth/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED, summary="Регистрация нового пользователя (MVP-опционально)")
async def register_user(
    user_in: UserCreateSchema,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Создает нового пользователя.
    В MVP этот эндпоинт может быть отключен или доступен только администраторам.
    """
    try:
        created_user = await auth_service.create_user(user_in=user_in)
        # Возвращаем данные пользователя без пароля
        return UserSchema.model_validate(created_user) 
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e: # Общая ошибка
        # logger.error(f"Ошибка при регистрации пользователя: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка на сервере при регистрации пользователя.",
        )


@router.get("/users/me", response_model=UserSchema, summary="Получение данных текущего пользователя")
async def read_users_me(
    current_user: UserSchema = Depends(get_current_active_user)
):
    """
    Возвращает данные текущего аутентифицированного пользователя.
    """
    return current_user