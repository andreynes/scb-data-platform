// frontend/src/features/dataExplorer/components/DataTable.tsx

import React, { useMemo } from 'react';
import { Table } from 'antd';
import type { ColumnsType } from 'antd/es/table';

// Тип для строки данных, может быть любым объектом
type TableRowData = Record<string, any>;

interface DataTableProps {
  data: TableRowData[];
  loading: boolean;
}

// Вспомогательная функция для генерации колонок
const generateColumns = (data: TableRowData[]): ColumnsType<TableRowData> => {
  if (!data || data.length === 0) {
    return [];
  }
  
  // Берем ключи из первого объекта данных как основу для колонок
  const keys = Object.keys(data[0]);
  
  return keys.map(key => ({
    title: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()), // Делаем заголовки читаемыми
    dataIndex: key,
    key: key,
    sorter: (a, b) => {
      if (typeof a[key] === 'number' && typeof b[key] === 'number') {
        return a[key] - b[key];
      }
      return String(a[key] ?? '').localeCompare(String(b[key] ?? ''));
    },
  }));
};

const DataTable: React.FC<DataTableProps> = ({ data, loading }) => {
  // Мемоизируем генерацию колонок, чтобы она не выполнялась на каждый рендер
  const tableColumns = useMemo(() => generateColumns(data), [data]);
  
  return (
    <Table
      columns={tableColumns}
      dataSource={data}
      loading={loading}
      rowKey={(record) => record.id || record._id || JSON.stringify(record)}
      pagination={{ pageSize: 15 }}
      scroll={{ x: 'max-content' }}
      size="small"
    />
  );
};

export default DataTable;