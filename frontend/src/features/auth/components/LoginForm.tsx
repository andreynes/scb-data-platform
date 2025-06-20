// Путь: frontend/src/features/auth/components/LoginForm.tsx

import React from 'react';
import { useForm, Controller, SubmitHandler } from 'react-hook-form';
import { Form, Input, Button, Alert, Space } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { LoginFormData } from '../types'; // Предполагаем, что этот тип существует

// Определяем пропсы для нашего компонента
interface LoginFormProps {
  onSubmit: (data: LoginFormData) => Promise<void> | void;
  isLoading: boolean;
  error: string | null;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSubmit, isLoading, error }) => {
  // Инициализируем react-hook-form
  const {
    control, // Важный объект для связи с UI-компонентами
    handleSubmit, // Функция-обертка для отправки формы
    formState: { errors }, // Объект с ошибками валидации
  } = useForm<LoginFormData>({
    mode: 'onSubmit', // Валидация при отправке
    reValidateMode: 'onChange', // Повторная валидация при изменении
    defaultValues: {
      username: '',
      password: '',
    },
  });

  // Этот обработчик будет вызван только после успешной валидации
  const handleFormSubmit: SubmitHandler<LoginFormData> = (data) => {
    onSubmit(data);
  };

  const isButtonDisabled = isLoading;

  return (
    <Form
      name="login_form"
      onFinish={handleSubmit(handleFormSubmit)} // Связываем Ant Design Form с React Hook Form
      layout="vertical"
    >
      {/* Поле Имя пользователя/Email */}
      <Form.Item
        label="Имя пользователя или Email"
        validateStatus={errors.username ? 'error' : ''}
        help={errors.username?.message}
        required
      >
        <Controller
          name="username"
          control={control}
          rules={{ required: 'Это поле обязательно' }}
          render={({ field }) => (
            <Input
              {...field}
              prefix={<UserOutlined />}
              placeholder="Имя пользователя или Email"
              disabled={isButtonDisabled}
            />
          )}
        />
      </Form.Item>

      {/* Поле Пароль */}
      <Form.Item
        label="Пароль"
        validateStatus={errors.password ? 'error' : ''}
        help={errors.password?.message}
        required
      >
        <Controller
          name="password"
          control={control}
          rules={{ required: 'Это поле обязательно' }}
          render={({ field }) => (
            <Input.Password
              {...field}
              prefix={<LockOutlined />}
              placeholder="Пароль"
              disabled={isButtonDisabled}
            />
          )}
        />
      </Form.Item>

      {/* Отображение ошибки от сервера */}
      {error && (
        <Form.Item>
          <Alert message={error} type="error" showIcon />
        </Form.Item>
      )}

      {/* Кнопка Войти */}
      <Form.Item>
        <Button
          type="primary"
          htmlType="submit"
          loading={isLoading}
          disabled={isButtonDisabled}
          block
        >
          Войти
        </Button>
      </Form.Item>
    </Form>
  );
};