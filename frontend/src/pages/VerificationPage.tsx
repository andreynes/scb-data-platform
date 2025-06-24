// frontend/src/pages/VerificationPage.tsx
import React, { useState } from 'react';
import { VerificationQueueTable } from '../features/verification/components/VerificationQueueTable';
import { useVerificationQueue } from '../features/verification/hooks/useVerificationQueue';
import { DataVerifier } from '../features/verification/components/DataVerifier'; // Примерный компонент для просмотра
import { Button } from 'antd';

const VerificationPage: React.FC = () => {
  const { tasks, isLoading, fetchQueue } = useVerificationQueue();
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);

  // Загружаем очередь при первом рендере
  React.useEffect(() => {
    fetchQueue();
  }, [fetchQueue]);

  if (selectedTaskId) {
    // Здесь будет компонент для просмотра ОДНОЙ задачи
    return (
      <div>
        <Button onClick={() => setSelectedTaskId(null)} style={{ marginBottom: 16 }}>
          ← Назад к очереди
        </Button>
        {/* Этот компонент будет получать данные по taskID через свой хук */}
        {/* <DataVerifier taskId={selectedTaskId} /> */}
        <p>Просмотр задачи: {selectedTaskId}</p> 
        {/* Временная заглушка для DataVerifier */}
      </div>
    );
  }

  return (
    <div>
      <h1>Очередь на верификацию</h1>
      <VerificationQueueTable
        tasks={tasks}
        isLoading={isLoading}
        onSelectTask={setSelectedTaskId}
      />
    </div>
  );
};

export default VerificationPage;