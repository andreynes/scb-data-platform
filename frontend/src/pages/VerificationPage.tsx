// frontend/src/pages/VerificationPage.tsx
import React, { useState } from 'react';
import { VerificationQueueTable } from '../features/verification/components/VerificationQueueTable';
import { useVerificationQueue } from '../features/verification/hooks/useVerificationQueue';
import { DataVerifier } from '../features/verification/components/DataVerifier'; 
import { Button } from 'antd';

const VerificationPage: React.FC = () => {
  const { tasks, isLoading, fetchQueue } = useVerificationQueue();
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);

  React.useEffect(() => {
    // Загружаем очередь только если ID задачи не выбран
    if (!selectedTaskId) {
      fetchQueue();
    }
  }, [selectedTaskId, fetchQueue]);

  if (selectedTaskId) {
    return (
      <DataVerifier 
        taskId={selectedTaskId} 
        onClose={() => setSelectedTaskId(null)} 
      />
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