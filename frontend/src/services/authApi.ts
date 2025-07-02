// frontend/src/services/authApi.ts (ФИНАЛЬНАЯ РАБОЧАЯ ВЕРСИЯ)

// Импорты уже правильные, оставляем их
import { AuthService } from './generated/services/AuthService';
import type {
  TokenSchema,
  UserSchema,
  Body_login_for_access_token_api_v1_auth_token_post as LoginCredentials,
} from './generated/index';

/**
 * Отправляет учетные данные на API для получения JWT токена.
 */
export const login = async (credentials: LoginCredentials): Promise<TokenSchema> => {
  return AuthService.loginForAccessTokenApiV1AuthTokenPost({ formData: credentials });
};

/**
 * Запрашивает данные текущего аутентифицированного пользователя.
 */
export const fetchCurrentUser = async (): Promise<UserSchema> => {
  // ===== ИСПРАВЛЕНО ИМЯ ФУНКЦИИ ЗДЕСЬ =====
  // Вызываем тот метод, который реально существует в AuthService.ts
  return AuthService.readUsersMeApiV1AuthMeGet();
};