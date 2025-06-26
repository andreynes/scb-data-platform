// frontend/src/features/dataExplorer/components/ExportButton.tsx
import React, { useState } from 'react';
import { Button, Dropdown, message } from 'antd';
import type { MenuProps } from 'antd';
import { DownloadOutlined, LoadingOutlined } from '@ant-design/icons';
// ИСПРАВЛЕНО: Убираем импорт ExportFormat, так как его нет
import { DataQuerySchema } from '../../../services/generated';
import { startDataExport } from '../../../services/dataApi';

interface ExportButtonProps {
  queryParams: DataQuerySchema;
}

// Определяем тип для формата экспорта прямо здесь
type ExportFormatType = 'excel' | 'csv';

export const ExportButton: React.FC<ExportButtonProps> = ({ queryParams }) => {
  const [loading, setLoading] = useState(false);

  const handleExport = async (format: ExportFormatType) => {
    setLoading(true);
    try {
      // ИСПРАВЛЕНО: startDataExport теперь возвращает Blob напрямую
      const responseBlob = await startDataExport(queryParams, format);
      
      if (!responseBlob) {
        throw new Error("Сервер не вернул файл для скачивания.");
      }

      const url = window.URL.createObjectURL(responseBlob);
      const link = document.createElement('a');
      link.href = url;
      const extension = format === 'excel' ? 'xlsx' : 'csv';
      const filename = `export_${queryParams.document_id || 'query'}.${extension}`;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      message.success('Экспорт успешно начат!');
    } catch (error) {
      console.error('Export failed:', error);
      message.error('Не удалось экспортировать данные.');
    } finally {
      setLoading(false);
    }
  };

  const items: MenuProps['items'] = [
    {
      key: 'excel',
      label: 'Экспорт в Excel (.xlsx)',
    },
    {
      key: 'csv',
      label: 'Экспорт в CSV (.csv)',
    },
  ];

  const handleMenuClick: MenuProps['onClick'] = (e) => {
    handleExport(e.key as ExportFormatType);
  };

  return (
    <Dropdown.Button
      type="primary"
      icon={loading ? <LoadingOutlined /> : <DownloadOutlined />}
      onClick={() => handleExport('excel')} // Действие по умолчанию
      menu={{ items, onClick: handleMenuClick }}
      disabled={loading}
    >
      {loading ? 'Экспорт...' : 'Экспорт'}
    </Dropdown.Button>
  );
};