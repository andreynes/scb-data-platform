// frontend/src/features/verification/components/VerificationQueueTable.tsx
import React from 'react';
import { Table, Button, Tag, Tooltip } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { VerificationTaskSchema } from '../../../services/generated';
import { formatDate } from '../../../utils/dateUtils';

interface VerificationQueueTableProps {
  tasks: VerificationTaskSchema[];
  isLoading: boolean;
  onSelectTask: (taskId: string) => void;
}

// Тип для строки таблицы, в данном случае он совпадает со схемой
type VerificationTaskRow = VerificationTaskSchema;

export const VerificationQueueTable: React.FC<VerificationQueueTableProps> = ({
  tasks,
  isLoading,
  onSelectTask,
}) => {
  const columns: ColumnsType<VerificationTaskRow> = [
    {
      title: 'ID Документа',
      dataIndex: 'document_id',
      key: 'document_id',
      render: (text: string) => (
        <Button type="link" onClick={() => onSelectTask(text)} style={{ padding: 0 }}>
          {text}
        </Button>
      ),
      sorter: (a, b) => a.document_id.localeCompare(b.document_id),
    },
    {
      title: 'Источник',
      dataIndex: 'source',
      key: 'source',
      sorter: (a, b) => (a.source || '').localeCompare(b.source || ''),
    },
    {
      title: 'Имя файла',
      dataIndex: 'filename',
      key: 'filename',
    },
    {
      title: 'Дата загрузки',
      dataIndex: 'upload_timestamp',
      key: 'upload_timestamp',
      render: (date) => formatDate(date),
      sorter: (a, b) => new Date(a.upload_timestamp).getTime() - new Date(b.upload_timestamp).getTime(),
      width: 170,
    },
    {
      title: 'Причина',
      dataIndex: 'reason_for_verification',
      key: 'reason_for_verification',
      render: (reason) => <Tag color="orange">{reason}</Tag>,
    },
    {
      title: 'Действие',
      key: 'action',
      render: (_, record: VerificationTaskRow) => (
        <Button type="primary" onClick={() => onSelectTask(record.document_id)}>
          Верифицировать
        </Button>
      ),
      align: 'center',
      width: 180,
    },
  ];

  return (
    <Table<VerificationTaskRow>
      columns={columns}
      dataSource={tasks}
      loading={isLoading}
      rowKey="document_id"
      size="small"
    />
  );
};