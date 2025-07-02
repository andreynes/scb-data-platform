// frontend/src/features/auth/components/LoginForm.tsx (ФИНАЛЬНАЯ РАБОЧАЯ ВЕРСИЯ)

import React from 'react';
import { useForm, Controller, SubmitHandler } from 'react-hook-form';
import { Form, Input, Button, Alert } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { LoginFormData } from '../types';

interface LoginFormProps {
  onSubmit: (data: LoginFormData) => Promise<void> | void;
  isLoading: boolean;
  error: string | null;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSubmit, isLoading, error }) => {
  const {
    control,
    handleSubmit,
    formState: { errors },
    // С помощью trigger мы можем запустить валидацию вручную
    trigger,
  } = useForm<LoginFormData>({
    mode: 'onChange', // Меняем режим для более отзывчивой валидации
  });

  // Эта функция остается такой же
  const handleFormSubmit: SubmitHandler<LoginFormData> = (data) => {
    onSubmit(data);
  };

  const isButtonDisabled = isLoading;

  // ===== КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: Новый обработчик для кнопки =====
  // Эта функция будет вызвана при клике на нашу кнопку.
  const handleButtonClick = async () => {
    // 1. Сначала мы вручную запускаем валидацию всех полей.
    const isValid = await trigger();

    // 2. Если валидация прошла успешно...
    if (isValid) {
      // 3. ...то мы вызываем handleSubmit, который гарантированно
      // вызовет нашу функцию `handleFormSubmit` с данными.
      handleSubmit(handleFormSubmit)();
    }
  };

  return (
    // Мы убрали лишний тег <form>. Теперь AntD <Form> - единственный.
    <Form layout="vertical">
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

      {error && (
        <Form.Item>
          <Alert message={error} type="error" showIcon />
        </Form.Item>
      )}

      <Form.Item>
        {/*
          УБИРАЕМ htmlType="submit" и вешаем наш обработчик на onClick.
          Теперь мы полностью контролируем процесс отправки.
        */}
        <Button
          type="primary"
          onClick={handleButtonClick} // <-- Используем наш новый обработчик
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