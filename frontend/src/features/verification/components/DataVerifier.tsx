// frontend/src/features/verification/components/DataVerifier.tsx
import React, { useState, useMemo } from 'react';
import { Alert, Spin, Descriptions, Table, Typography, Modal, Tag } from 'antd';
import { useVerificationTask } from '../hooks/useVerificationTask';
import { VerificationControls } from './VerificationControls';
import { CorrectionInput } from './CorrectionInput'; // <<< НОВЫЙ ИМПОРТ
import { SelectedCellInfo } from '../types';

interface DataVerifierProps {
  taskId: string;
  onClose: () => void; // Колбэк для кнопки "Назад к очереди"
}

const { Title } = Typography;

export const DataVerifier: React.FC<DataVerifierProps> = ({ taskId, onClose }) => {
  const {
    verificationData,
    isLoading,
    error,
    isSubmitting,
    submitVerification,
    appliedCorrections, // <<< ПОЛУЧАЕМ ИСПРАВЛЕНИЯ ИЗ ХУКА
    applyCorrection,    // <<< ПОЛУЧАЕМ ФУНКЦИЮ ДЛЯ ИСПРАВЛЕНИЙ
  } = useVerificationTask(taskId);
  
  const [selectedCell, setSelectedCell] = useState<SelectedCellInfo | null>(null);

  const handleCellClick = (atomId: string, columnKey: string, currentValue: any) => {
    setSelectedCell({ atomId, columnKey, currentValue });
  };

  const handleModalClose = () => {
    setSelectedCell(null);
  };

  const handleCorrectionSubmit = (correction: any) => {
    applyCorrection(correction); // Обновляем локальное состояние исправлений через хук
    handleModalClose();
  };

  // Логика генерации колонок теперь включает обработку клика и подсветку исправлений
  const tableColumns = useMemo(() => {
    if (!verificationData?.atomic_data?.[0]) return [];
    const keys = Object.keys(verificationData.atomic_data[0]);
    
    return keys.map((key) => ({
      title: key,
      dataIndex: key,
      key: key,
      render: (text: any, record: any) => {
        const atomId = record._id || record.id;
        const correction = appliedCorrections.find(c => c.atomId === atomId && c.fieldName === key);

        const cellValue = correction ? correction.newValue : text;
        const displayValue = String(cellValue ?? '-');
        
        return (
          <div 
            onClick={() => handleCellClick(atomId, key, text)} 
            style={{ cursor: 'pointer', minWidth: '100px' }}
          >
            {correction ? <Tag color="blue">Исправлено</Tag> : null}
            {displayValue}
          </div>
        );
      },
    }));
  }, [verificationData, appliedCorrections]);

  // ... (блоки isLoading, error, !verificationData остаются такими же) ...
  if (isLoading) { /* ... */ }
  if (error) { /* ... */ }
  if (!verificationData) { /* ... */ }

  return (
    <div>
      <Button onClick={onClose} style={{ marginBottom: 16 }}>
        ← Назад к очереди
      </Button>
      <Title level={4}>Верификация документа: {verificationData.document_id}</Title>
      
      <Title level={5}>Атомарные Данные (кликните на ячейку для исправления)</Title>
      <Table
        columns={tableColumns}
        dataSource={verificationData.atomic_data?.map((item: any) => ({ ...item, key: item._id || item.id }))}
        bordered
        size="small"
        pagination={false}
        scroll={{ x: 'max-content' }}
      />
      
      {selectedCell && (
        <Modal
          title={`Исправление: ${selectedCell.columnKey}`}
          open={!!selectedCell}
          onCancel={handleModalClose}
          footer={null} // Управление кнопками внутри CorrectionInput
          destroyOnClose
        >
          <CorrectionInput
            cellData={selectedCell}
            ontologyAttributes={verificationData.ontology_schema?.attributes || []}
            onSubmitCorrection={handleCorrectionSubmit}
            onCancel={handleModalClose}
            vocabularies={{}} // TODO: Передать сюда реальные словари
          />
        </Modal>
      )}
      
      <VerificationControls
        isSubmitting={isSubmitting}
        onSubmit={submitVerification}
        onCancel={onClose}
      />
    </div>
  );
};