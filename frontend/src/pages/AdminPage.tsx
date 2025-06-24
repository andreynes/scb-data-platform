// frontend/src/pages/AdminPage.tsx
import React from 'react';
import { Typography, Space } from 'antd';
import { ReparsePanel } from '../features/admin/components/ReparsePanel'; // Импортируем нашу панель

const { Title } = Typography;

const AdminPage: React.FC = () => {
  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Title level={2}>Панель Администратора</Title>
      
      {/* Здесь будет наша панель для репарсинга */}
      <ReparsePanel />

      {/* В будущем сюда можно добавлять другие админ-панели */}
    </Space>
  );
};

export default AdminPage;