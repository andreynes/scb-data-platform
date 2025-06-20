// frontend/src/features/fileUpload/FileUploadSection.tsx
import React from 'react';
import { Button, Space } from 'antd';
import { FileUploadDropzone } from './components/FileUploadDropzone';
import { FileUploadList } from './components/FileUploadList';
import { useFileUploadManager } from './hooks/useFileUploadManager';

export const FileUploadSection: React.FC = () => {
  const { uploads, handleUploadStart, clearCompleted } = useFileUploadManager();
  
  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <FileUploadDropzone onUploadStart={handleUploadStart} />
      {uploads.length > 0 && (
        <Button onClick={clearCompleted} style={{ marginTop: '16px' }}>
          Очистить завершенные
        </Button>
      )}
      <FileUploadList uploads={uploads} />
    </Space>
  );
};