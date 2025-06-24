// frontend/src/features/verification/components/DataVerifier.tsx
import React from 'react';
import { Alert, Spin, Descriptions, Table, Typography } from 'antd';
import { useVerificationTask } from '../hooks/useVerificationTask';
import { VerificationControls } from './VerificationControls';

interface DataVerifierProps {
  taskId: string;
}

const { Title, Text } = Typography;

export const DataVerifier: React.FC<DataVerifierProps> = ({ taskId }) => {
  const {
    verificationData,
    isLoading,
    error,
    isSubmitting,
    submitVerification,
  } = useVerificationTask(taskId);

  if (isLoading) {
    return <Spin tip="Загрузка данных для верификации..." size="large" />;
  }

  if (error) {
    return <Alert message="Ошибка загрузки данных" description={error} type="error" showIcon />;
  }
  
  if (!verificationData) {
     return <Alert message="Данные для верификации не найдены." type="warning" />;
  }

  const atomicDataColumns = verificationData.atomic_data?.[0]
    ? Object.keys(verificationData.atomic_data[0]).map(key => ({
        title: key,
        dataIndex: key,
        key: key,
      }))
    : [];

  return (
    <div>
      <Title level={4}>Верификация документа: {verificationData.document_id}</Title>
      
      <Descriptions bordered column={1} style={{ marginBottom: 24 }}>
        <Descriptions.Item label="Исходное JSON представление">
          <pre style={{ maxHeight: '300px', overflow: 'auto', background: '#f5f5f5', padding: '10px' }}>
            {JSON.stringify(verificationData.json_representation, null, 2)}
          </pre>
        </Descriptions.Item>
      </Descriptions>

      <Title level={5}>Распознанные Атомарные Данные</Title>
      <Table
        columns={atomicDataColumns}
        dataSource={verificationData.atomic_data?.map((item, index) => ({...item, key: index}))}
        bordered
        size="small"
        pagination={false}
        scroll={{ x: 'max-content' }}
      />
      
      <VerificationControls
        isSubmitting={isSubmitting}
        onSubmit={submitVerification}
        onCancel={() => { /* TODO: Логика для кнопки отмены */ }}
      />
    </div>
  );
};