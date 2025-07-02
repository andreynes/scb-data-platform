// Файл: frontend/src/features/dataExplorer/components/QueryBuilder.tsx

import React, { useState, useCallback } from 'react';
import { Card, Button, Space, Tooltip, message, Alert, Spin, Row, Col } from 'antd';
import { FlagOutlined } from '@ant-design/icons';
import { useDataExplorer } from '../hooks/useDataExplorer';
import { flagDocumentForVerification } from '../../../services/dataApi';
import DataTable from './DataTable';
import { DataChart } from './DataChart';
import { ExportButton } from './ExportButton';
// === НОВОЕ: Импортируем компонент загрузки файла ===
import { FileUploadSection } from '../../fileUpload/components/FileUploadSection'; 
import { DataQuerySchema } from '../../../schemas/data_schemas';

export const QueryBuilder: React.FC = () => {
  const [viewMode, setViewMode] = useState<'table' | 'chart'>('table');
  
  // === НОВОЕ: Локальное состояние для хранения ID документа ===
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);

  const { 
    queryParams, 
    queryResult, 
    isLoading,
    error,
    executeQuery 
  } = useDataExplorer();

  // === НОВЫЙ ОБРАБОТЧИК: Вызывается после успешной загрузки файла из FileUploadSection ===
  const handleUploadSuccess = (docId: string, filename: string) => {
      message.success(`Файл "${filename}" успешно загружен. ID документа: ${docId}`);
      setSelectedDocumentId(docId); // Сохраняем ID для последующих запросов
  };
    
  // === ОБНОВЛЕННЫЙ ОБРАБОТЧИК: Теперь он будет использовать сохраненный ID ===
  const handleQuerySubmit = useCallback(() => {
    if (!selectedDocumentId) {
      message.error('Пожалуйста, сначала загрузите файл.');
      return;
    }
    // Формируем запрос с ID документа
    const query: DataQuerySchema = {
      ...queryParams,
      document_id: selectedDocumentId,
    };
    executeQuery(query);
  }, [executeQuery, queryParams, selectedDocumentId]);

  const handleFlagForVerification = async () => {
    if (!selectedDocumentId) {
      message.error("ID документа не определен, чтобы отправить его на верификацию.");
      return;
    }
    try {
      await flagDocumentForVerification(selectedDocumentId);
      message.success(`Документ ${selectedDocumentId} успешно отправлен на верификацию.`);
    } catch (err: any) {
      const errorMessage = err?.body?.detail || "Не удалось отправить документ на верификацию.";
      message.error(errorMessage);
    }
  };

  const hasData = queryResult && queryResult.data && queryResult.data.length > 0;

  return (
    <Row gutter={[16, 16]}>
      <Col xs={24} lg={8}>
        <Card title="Загрузка и Параметры" bordered={false}>
          <Space direction="vertical" style={{ width: '100%' }}>
            {/* === НОВОЕ: Добавлен компонент для загрузки файлов === */}
            <FileUploadSection onUploadSuccess={handleUploadSuccess} />
            <p>Выбранный документ: {selectedDocumentId || 'не выбран'}</p>
            {/* Здесь в будущем будет FilterPanel */}
            <Button 
              type="primary" 
              onClick={handleQuerySubmit} 
              loading={isLoading}
              block
              disabled={!selectedDocumentId || isLoading} // Кнопка неактивна, пока документ не загружен
            >
              Выполнить запрос
            </Button>
          </Space>
        </Card>
      </Col>

      <Col xs={24} lg={16}>
        <Spin spinning={isLoading}>
          <Card 
            title="Результаты" 
            extra={
              <Space>
                {hasData && (
                  <Button.Group>
                    <Button onClick={() => setViewMode('table')} type={viewMode === 'table' ? 'primary' : 'default'}>Таблица</Button>
                    <Button onClick={() => setViewMode('chart')} type={viewMode === 'chart' ? 'primary' : 'default'}>График</Button>
                  </Button.Group>
                )}
                {hasData && <ExportButton queryParams={{...queryParams, document_id: selectedDocumentId!}} />}
                {hasData && (
                  <Tooltip title="Сообщить об ошибке в данных">
                    <Button icon={<FlagOutlined />} onClick={handleFlagForVerification} danger />
                  </Tooltip>
                )}
              </Space>
            }
          >
            {error && <Alert message="Ошибка запроса данных" description={error} type="error" showIcon style={{ marginBottom: 16 }} />}
            
            {hasData && viewMode === 'table' && queryResult.data && (
              <DataTable data={queryResult.data} />
            )}
            
            {hasData && viewMode === 'chart' && queryResult.data && (
               <DataChart data={queryResult.data} />
            )}
            
            {!hasData && !isLoading && !error && (
              <div>Загрузите файл и выполните запрос, чтобы увидеть результаты.</div>
            )}
          </Card>
        </Spin>
      </Col>
    </Row>
  );
};