// frontend/src/pages/FileUploadPage.tsx
import React from 'react';
import FileUploadSection from '../features/fileUpload/components/FileUploadSection'; // Уточните путь!
// или тот компонент, который вы хотите здесь видеть

const FileUploadPage: React.FC = () => {
  return (
    <div>
      <h1>Загрузка Файлов</h1>
      <FileUploadSection />
    </div>
  );
};
export default FileUploadPage;