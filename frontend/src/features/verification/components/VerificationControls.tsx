// frontend/src/features/verification/components/VerificationControls.tsx
import React from 'react';
import { Button, Space, Popconfirm } from 'antd';
import { CheckCircleOutlined, IssuesCloseOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { VerificationStatus } from '../../../services/generated';

interface VerificationControlsProps {
  onSubmit: (status: VerificationStatus) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

export const VerificationControls: React.FC<VerificationControlsProps> = ({
  onSubmit,
  onCancel,
  isSubmitting,
}) => {
  return (
    <Space style={{ width: '100%', justifyContent: 'flex-end', marginTop: '24px' }}>
      <Button icon={<CloseCircleOutlined />} onClick={onCancel} disabled={isSubmitting}>
        Отмена
      </Button>

      <Popconfirm
        title="Отправить на доработку?"
        description="Задача будет помечена как требующая дополнительного внимания."
        onConfirm={() => onSubmit(VerificationStatus.NEEDS_FIXING)}
        okText="Да, отправить"
        cancelText="Нет"
        disabled={isSubmitting}
      >
        <Button icon={<IssuesCloseOutlined />} loading={isSubmitting} disabled={isSubmitting}>
          Требует доработки
        </Button>
      </Popconfirm>

      <Popconfirm
        title="Завершить верификацию?"
        description="Задача будет помечена как 'Проверено человеком'."
        onConfirm={() => onSubmit(VerificationStatus.VERIFIED)}
        okText="Да, завершить"
        cancelText="Нет"
        disabled={isSubmitting}
      >
        <Button
          type="primary"
          icon={<CheckCircleOutlined />}
          loading={isSubmitting}
          disabled={isSubmitting}
        >
          Проверено
        </Button>
      </Popconfirm>
    </Space>
  );
};