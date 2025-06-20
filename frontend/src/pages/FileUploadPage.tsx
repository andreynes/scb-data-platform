// frontend/src/pages/FileUploadPage.tsx
import React from 'react';
import { Typography, Card } from 'antd';
import { FileUploadSection } from '../features/fileUpload'; // <-- Проверьте этот импорт

const { Title } = Typography;

const FileUploadPage: React.FC = () => {
  return (
    <div>
      <Title level={2}>Загрузка новых документов</Title>
      <Card>
        <FileUploadSection />
      </Card>
    </div>
  );
};

export default FileUploadPage;