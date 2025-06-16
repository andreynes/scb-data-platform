// frontend/src/features/dataExplorer/components/QueryBuilder.tsx

import React, { useEffect } from 'react';
import { Card, Button, Spin, Alert, Row, Col, Space } from 'antd';
import { useDataExplorer } from '../hooks/useDataExplorer';
import DataTable from './DataTable'; // Мы создадим его на следующем шаге

const QueryBuilder: React.FC = () => {
  // Получаем все необходимое из нашего нового хука
  const {
    queryParams,
    setQueryParams, // Пока не используем, но понадобится для фильтров
    executeQuery,
    queryResult,
    isLoading,
    error,
  } = useDataExplorer();

  // Для примера, выполним запрос для первого документа при загрузке
  // В будущем это будет делаться по действию пользователя
  useEffect(() => {
    // Устанавливаем ID документа для теста. В будущем это будет динамически.
    // Используйте ID, который точно есть в вашей БД после выполнения ETL.
    // Например, ID файла, который вы загружали для тестирования ETL.
    const testDocumentId = "ID_ВАШЕГО_ТЕСТОВОГО_ДОКУМЕНТА"; // !!! ЗАМЕНИТЕ НА РЕАЛЬНЫЙ ID !!!
    
    setQueryParams({ document_id: testDocumentId });
    
    // Запускаем запрос автоматически для демонстрации
    // executeQuery(); // Лучше сделать по кнопке, чтобы не было лишних запросов
  }, []); // Пустой массив зависимостей, чтобы выполнилось один раз


  const handleQuerySubmit = () => {
    executeQuery();
  };

  return (
    <Row gutter={[16, 16]}>
      <Col xs={24} lg={8}>
        <Card title="Параметры запроса" bordered={false}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <p>Здесь будут фильтры и другие настройки.</p>
            <p>Текущий документ: {queryParams.document_id || "не выбран"}</p>
            <Button
              type="primary"
              onClick={handleQuerySubmit}
              loading={isLoading}
              block
            >
              Выполнить запрос
            </Button>
          </Space>
        </Card>
      </Col>
      <Col xs={24} lg={16}>
        <Card title="Результаты">
          <Spin spinning={isLoading}>
            {error && <Alert message="Ошибка запроса" description={error} type="error" showIcon />}
            {queryResult && (
              <DataTable
                data={queryResult.data || []}
                loading={isLoading}
              />
            )}
            {!queryResult && !isLoading && !error && (
              <div>Выполните запрос, чтобы увидеть результаты.</div>
            )}
          </Spin>
        </Card>
      </Col>
    </Row>
  );
};

export default QueryBuilder;