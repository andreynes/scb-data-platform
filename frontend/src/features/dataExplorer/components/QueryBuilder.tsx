// frontend/src/features/dataExplorer/components/QueryBuilder.tsx

import React from 'react';
// <<< ДОБАВЛЕНЫ Tooltip, message >>>
import { Card, Button, Space, Typography, Tooltip, message } from 'antd';
// <<< ДОБАВЛЕНА ИКОНКА >>>
import { FlagOutlined } from '@ant-design/icons';

// <<< ДОБАВЛЕН ИМПОРТ API И ХУКА >>>
import { useDataExplorer } from '../hooks/useDataExplorer';
import { flagDocumentForVerification } from '../../../services/dataApi';

export const QueryBuilder: React.FC = () => {
  // Используем хук для управления состоянием
  const { 
    queryParams, 
    queryResult, 
    isLoading,
    executeQuery 
  } = useDataExplorer();

  const handleQuerySubmit = () => {
    // executeQuery уже не принимает аргументов, т.к. берет их из стейта
    executeQuery();
  };

  // <<< НОВАЯ ФУНКЦИЯ-ОБРАБОТЧИК >>>
  const handleFlagForVerification = async () => {
    const docId = queryParams.document_id;
    if (!docId) {
      message.error("ID документа не определен, чтобы отправить его на верификацию.");
      return;
    }

    try {
      await flagDocumentForVerification(docId);
      message.success(`Документ ${docId} успешно отправлен на верификацию.`);
    } catch (error: any) {
      const errorMessage = error?.body?.detail || "Не удалось отправить документ на верификацию.";
      message.error(errorMessage);
    }
  };

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      <Card title="Параметры запроса">
        <p>Здесь будут фильтры и другие настройки. (Текущий документ: {queryParams.document_id || 'не выбран'})</p>
        <Button 
          type="primary" 
          onClick={handleQuerySubmit} 
          loading={isLoading}
        >
          Выполнить запрос
        </Button>
      </Card>
      
      {/* Отображаем результаты только если они есть */}
      {queryResult && (
        <Card 
          title="Результаты" 
          extra={
            <Space>
              {/* <<< НАЧАЛО НОВОЙ КНОПКИ >>> */}
              <Tooltip title="Сообщить об ошибке или неточности в этих данных">
                <Button 
                  icon={<FlagOutlined />} 
                  onClick={handleFlagForVerification}
                  danger
                >
                  На верификацию
                </Button>
              </Tooltip>
              {/* <<< КОНЕЦ НОВОЙ КНОПКИ >>> */}
            </Space>
          }
        >
          {/* Здесь будет DataTable, пока просто выводим JSON */}
          <pre>{JSON.stringify(queryResult.data, null, 2)}</pre>
        </Card>
      )}
    </Space>
  );
};