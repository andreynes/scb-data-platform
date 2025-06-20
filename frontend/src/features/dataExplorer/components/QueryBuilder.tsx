// frontend/src/features/dataExplorer/components/QueryBuilder.tsx
import React from 'react';
import { Card, Button, Space, Typography } from 'antd';

const { Title } = Typography;

export const QueryBuilder: React.FC = () => {
  // Здесь в будущем будет логика для получения данных и управления состоянием

  const handleQuerySubmit = () => {
    alert('Запрос данных в разработке!');
  };

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      <Card title="Параметры запроса">
        <p>Здесь будут фильтры и другие настройки.</p>
        <Button type="primary" onClick={handleQuerySubmit}>
          Выполнить запрос
        </Button>
      </Card>
      <Card title="Результаты">
        <p>Здесь будут отображаться результаты запроса.</p>
      </Card>
    </Space>
  );
};