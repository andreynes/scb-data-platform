// frontend/src/features/auth/types.ts
import type { UserSchema } from '../../schemas/user_schemas'; // Импортируем базовую схему

/**
 * Тип для данных формы входа
 */
export type LoginFormData = Pick<UserSchema, 'username' | 'password'>;

/**
 * Тип для возвращаемого значения хука useAuth
 */
export interface AuthHookResult {
  isAuthenticated: boolean;
  user: UserSchema | null;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginFormData) => Promise<void>;
  logout: () => void;
}