// frontend/src/features/admin/components/ReparsePanel.tsx
import React, { useState } from 'react';
import { Table, Button, Checkbox, message } from 'antd';
import type { TableProps } from 'antd';
// import { useAdminApi } from '../../services/adminApi'; // Пример импорта API

// Мок-данные, пока нет реального списка файлов
const mockDocuments = [
  { key: 'doc-id-1', filename: 'report_2022.xlsx', status: 'Processed' },
  { key: 'doc-id-2', filename: 'analytics_h1.pdf', status: 'Error' },
  { key: 'doc-id-3', filename: 'forecast.xlsx', status: 'Processed' },
];

interface DataType {
  key: string;
  filename: string;
  status: string;
}

export const ReparsePanel: React.FC = () => {
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [loading, setLoading] = useState(false);

  const onSelectChange = (newSelectedRowKeys: React.Key[]) => {
    setSelectedRowKeys(newSelectedRowKeys);
  };

  const rowSelection = {
    selectedRowKeys,
    onChange: onSelectChange,
  };

  const handleReparse = async () => {
    setLoading(true);
    try {
      // Здесь будет вызов API
      // await adminApi.triggerManualReparse({ document_ids: selectedRowKeys as string[] });
      console.log('Triggering reparse for:', selectedRowKeys);
      message.success(`Запущен репарсинг для ${selectedRowKeys.length} документов.`);
      setSelectedRowKeys([]);
    } catch (error) {
      message.error('Ошибка при запуске репарсинга.');
    } finally {
      setLoading(false);
    }
  };

  const columns: TableProps<DataType>['columns'] = [
    { title: 'Имя файла', dataIndex: 'filename' },
    { title: 'Статус', dataIndex: 'status' },
  ];

  return (
    <div>
      <Button
        type="primary"
        onClick={handleReparse}
        disabled={selectedRowKeys.length === 0}
        loading={loading}
        style={{ marginBottom: 16 }}
      >
        Запустить репарсинг для выбранных
      </Button>
      <Table
        rowSelection={rowSelection}
        columns={columns}
        dataSource={mockDocuments}
      />
    </div>
  );
};