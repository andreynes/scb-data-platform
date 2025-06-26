// frontend/src/features/dataExplorer/components/QueryBuilder.tsx

import React, { useState } from 'react';
import { Card, Button, Space, Tooltip, message, Alert, Spin, Row, Col } from 'antd';
import { FlagOutlined } from '@ant-design/icons';

import { useDataExplorer } from '../hooks/useDataExplorer';
// ИСПРАВЛЕНО: Используем правильное имя сервиса
import { flagDocumentForVerification } from '../../../services/dataApi'; 

// ИСПРАВЛЕНО: Предполагаем, что DataTable экспортируется как именованный экспорт
import DataTable from './DataTable';
import { DataChart } from './DataChart';
import { ExportButton } from './ExportButton';

export const QueryBuilder: React.FC = () => {
  const [viewMode, setViewMode] = useState<'table' | 'chart'>('table');

  const { 
    queryParams, 
    queryResult, 
    isLoading,
    error,
    executeQuery 
  } = useDataExplorer();

  const handleQuerySubmit = () => {
    executeQuery();
  };

  const handleFlagForVerification = async () => {
    const docId = queryParams.document_id;
    if (!docId) {
      message.error("ID документа не определен, чтобы отправить его на верификацию.");
      return;
    }

    try {
      await flagDocumentForVerification(docId);
      message.success(`Документ ${docId} успешно отправлен на верификацию.`);
    } catch (err: any) {
      const errorMessage = err?.body?.detail || "Не удалось отправить документ на верификацию.";
      message.error(errorMessage);
    }
  };

  const hasData = queryResult && queryResult.data && queryResult.data.length > 0;

  return (
    <Row gutter={[16, 16]}>
      <Col xs={24} lg={8}>
        <Card title="Параметры запроса">
          <p>Здесь будут фильтры. (Документ: {queryParams.document_id || 'не выбран'})</p>
          <Button 
            type="primary" 
            onClick={handleQuerySubmit} 
            loading={isLoading}
            block
          >
            Выполнить запрос
          </Button>
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
                {hasData && <ExportButton queryParams={queryParams} />}
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
              <div>Выполните запрос, чтобы увидеть результаты.</div>
            )}
          </Card>
        </Spin>
      </Col>
    </Row>
  );
};