// frontend/src/pages/UserProfilePage.tsx
import React from 'react';
import { Typography } from 'antd';

const { Title } = Typography;

const UserProfilePage: React.FC = () => {
  // Здесь будет логика отображения и изменения профиля
  return (
    <div>
      <Title level={2}>Профиль Пользователя</Title>
      <p>Раздел находится в разработке.</p>
    </div>
  );
};

export default UserProfilePage;