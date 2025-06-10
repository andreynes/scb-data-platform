import React, { useMemo } from 'react';
import { Alert, Spin } from 'antd';
import type { ColumnsType } from 'antd/es/table';

import { useAppSelector } from '../../../app/hooks';
import AppTable from '../../../components/Table/AppTable'; // Наш универсальный компонент таблицы

import {
  selectQueryResult,
  selectDataQueryStatus,
  selectDataQueryError,
} from '../slice';
import type { AtomicDataRow } from '../../../services/generated';

/**
 * Компонент для отображения результатов запроса к СКЛАДУ.
 * Он получает состояние (данные, статус загрузки, ошибку) напрямую из Redux store.
 */
export const DataTable: React.FC = () => {
  // Получаем данные из Redux store с помощью селекторов
  const queryResult = useAppSelector(selectQueryResult);
  const status = useAppSelector(selectDataQueryStatus);
  const error = useAppSelector(selectDataQueryError);

  // Используем useMemo для генерации колонок, чтобы это не происходило на каждый рендер.
  // Эта логика будет усложняться (получение названий из онтологии и т.д.).
  const tableColumns = useMemo((): ColumnsType<AtomicDataRow> => {
    // Если данных нет, нет и колонок
    if (!queryResult?.data || queryResult.data.length === 0) {
      return [];
    }
    // Для MVP просто берем ключи из первого объекта данных
    const keys = Object.keys(queryResult.data[0]);
    
    return keys.map((key) => ({
      title: key.replace(/_/g, ' ').toUpperCase(), // Простое форматирование заголовка
      dataIndex: key,
      key: key,
      sorter: true, // Включаем серверную сортировку для всех колонок
    }));
  }, [queryResult?.data]); // Пересчитываем только при изменении данных

  // --- Условный рендеринг в зависимости от статуса ---

  if (status === 'loading') {
    return <Spin tip="Загрузка данных..." size="large" />;
  }

  if (status === 'failed') {
    return <Alert message="Ошибка при загрузке данных" description={error} type="error" showIcon />;
  }

  if (status === 'succeeded' && (!queryResult?.data || queryResult.data.length === 0)) {
    return <Alert message="Данные не найдены" description="По вашему запросу не найдено ни одной записи." type="info" showIcon />;
  }

  // Если все успешно и данные есть
  return (
    <AppTable<AtomicDataRow>
      columns={tableColumns}
      dataSource={queryResult?.data || []}
      loading={status === 'loading'}
      // TODO: Добавить обработку серверной пагинации и сортировки через onTableChange
    />
  );
};