import React, { useState, useCallback, useEffect } from 'react';
import { Input, Button, Card, Space, Alert, Row, Col, Typography } from 'antd';
import { useAppDispatch, useAppSelector } from '../../../app/hooks';
import {
  fetchDataQueryThunk,
  setQueryParams,
  clearDataExplorerState, // Используем для полного сброса
  selectQueryParams,
  selectDataQueryStatus,
  selectDataQueryError,
} from '../slice';
import { DataTable } from './DataTable'; // Импортируем наш основной компонент отображения

const { Text } = Typography;

const QueryBuilder: React.FC = () => {
  const dispatch = useAppDispatch();

  // Получаем состояние из Redux store
  const queryParams = useAppSelector(selectQueryParams);
  const status = useAppSelector(selectDataQueryStatus);
  const error = useAppSelector(selectDataQueryError);

  // Локальное состояние для поля ввода, синхронизированное с Redux
  const [documentIdInput, setDocumentIdInput] = useState<string>(queryParams.document_id || '');

  // Синхронизируем инпут, если ID документа меняется извне (например, при переходе по ссылке)
  useEffect(() => {
    setDocumentIdInput(queryParams.document_id || '');
  }, [queryParams.document_id]);
  
  const handleQuerySubmit = useCallback(() => {
    const trimmedId = documentIdInput.trim();
    if (trimmedId) {
      // Сначала обновляем параметры в сторе, затем запускаем thunk, который их оттуда возьмет
      dispatch(setQueryParams({ document_id: trimmedId }));
      dispatch(fetchDataQueryThunk()); 
    }
  }, [dispatch, documentIdInput]);

  // Сбрасываем состояние при размонтировании компонента
  useEffect(() => {
    return () => {
      dispatch(clearDataExplorerState());
    };
  }, [dispatch]);

  return (
    <Row gutter={[16, 16]}>
      {/* Панель запроса */}
      <Col xs={24} lg={8}>
        <Card title="Параметры запроса (MVP)" bordered={false}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Text>ID Документа</Text>
            <Input
              placeholder="Введите Document ID"
              value={documentIdInput}
              onChange={(e) => setDocumentIdInput(e.target.value)}
              onPressEnter={handleQuerySubmit}
              disabled={status === 'loading'} // Блокируем ввод во время загрузки
            />
            <Button
              type="primary"
              onClick={handleQuerySubmit}
              loading={status === 'loading'} // Индикатор загрузки
              disabled={!documentIdInput.trim()} // Кнопка неактивна, если поле пустое
              block
            >
              Запросить данные
            </Button>
          </Space>
        </Card>
      </Col>

      {/* Панель результатов */}
      <Col xs={24} lg={16}>
        <Card title="Результаты из СКЛАДА" bordered={false}>
          {/* DataTable теперь сам обрабатывает isLoading и error, получая их из стора */}
          <DataTable />
        </Card>
      </Col>
    </Row>
  );
};

export default QueryBuilder;