// Путь: frontend/src/services/authApi.ts

import {
  AuthService,
  TokenSchema,
  UserSchema,
  Body_login_for_access_token_api_v1_auth_token_post as LoginCredentials, // Это правильный тип для formData
} from './generated';

/**
 * Отправляет учетные данные на API для получения JWT токена.
 * @param credentials - Имя пользователя и пароль.
 * @returns Promise, который разрешается объектом TokenSchema.
 */
export const login = async (credentials: LoginCredentials): Promise<TokenSchema> => {
  try {
    //
    // --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
    //
    // Имя функции изменено на loginForAccessTokenApiV1AuthTokenPost,
    // чтобы оно точно соответствовало сгенерированному файлу.
    const response = await AuthService.loginForAccessTokenApiV1AuthTokenPost({
      formData: credentials,
    });
    return response;
  } catch (error) {
    console.error("Login API error:", error);
    // Пробрасываем ошибку дальше, чтобы ее мог поймать Redux Thunk
    throw error;
  }
};

/**
 * Запрашивает данные текущего аутентифицированного пользователя.
 * Токен аутентификации должен быть добавлен автоматически конфигурацией OpenAPI клиента.
 * @returns Promise, который разрешается объектом UserSchema.
 */
export const fetchCurrentUser = async (): Promise<UserSchema> => {
  try {
    // Вызываем соответствующий сгенерированный метод
    const userData = await AuthService.readUsersMeApiV1AuthMeGet();
    return userData;
  } catch (error) {
    console.error("Fetch current user API error:", error);
    throw error;
  }
};

// Примечание: Функция для регистрации (registerUser) может быть добавлена здесь по аналогии, если она потребуется.