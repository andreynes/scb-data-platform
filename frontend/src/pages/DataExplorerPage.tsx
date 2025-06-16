// frontend/src/pages/DataExplorerPage.tsx

import React from 'react';
import { Typography } from 'antd';
import QueryBuilder from '../features/dataExplorer/components/QueryBuilder';

const { Title } = Typography;

const DataExplorerPage: React.FC = () => {
  return (
    <div>
      <Title level={2}>Исследователь Данных</Title>
      <QueryBuilder />
    </div>
  );
};

export default DataExplorerPage;