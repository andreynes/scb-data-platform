// frontend/src/features/verification/components/VerificationControls.tsx
import React from 'react';
import { Button, Space, message, Popconfirm } from 'antd';
import { CheckOutlined, CloseOutlined } from '@ant-design/icons';

// ИСПРАВЛЕНИЕ: 
// 1. Убираем несуществующий импорт VerificationTaskStatus.
// 2. Вместо него определяем тип прямо здесь, так как он используется только в этом компоненте.
type VerificationStatus = 'Verified' | 'NeedsFixing';

interface VerificationControlsProps {
  // Используем наш локально определенный тип
  onUpdateStatus: (status: VerificationStatus) => void;
  isSubmitting: boolean;
}

export const VerificationControls: React.FC<VerificationControlsProps> = ({ 
  onUpdateStatus, 
  isSubmitting 
}) => {
  const handleConfirm = () => {
    // ИСПРАВЛЕНИЕ: Используем строковый литерал вместо enum
    onUpdateStatus('Verified'); 
    message.success('Статус "Проверено человеком" будет установлен.');
  };

  const handleNeedsFixing = () => {
    // ИСПРАВЛЕНИЕ: Используем строковый литерал вместо enum
    onUpdateStatus('NeedsFixing');
    message.warning('Статус "Требует доработки" будет установлен.');
  };

  return (
    <Space style={{ marginTop: 16, display: 'flex', justifyContent: 'flex-end' }}>
      <Popconfirm
        title="Отправить на доработку?"
        description="Этот документ будет помечен как требующий исправлений."
        onConfirm={handleNeedsFixing}
        okText="Да"
        cancelText="Нет"
      >
        <Button 
          icon={<CloseOutlined />} 
          danger 
          loading={isSubmitting}
        >
          Требует доработки
        </Button>
      </Popconfirm>
      
      <Popconfirm
        title="Завершить верификацию?"
        description="Вы уверены, что все данные корректны?"
        onConfirm={handleConfirm}
        okText="Да, все верно"
        cancelText="Отмена"
      >
        <Button 
          type="primary" 
          icon={<CheckOutlined />} 
          loading={isSubmitting}
        >
          Проверено
        </Button>
      </Popconfirm>
    </Space>
  );
};