// frontend/src/pages/DataExplorerPage.tsx
import React from 'react';
import { Layout, Typography } from 'antd';
// Предположим, что QueryBuilder будет основным компонентом этой фичи
import QueryBuilder from '../features/dataExplorer/components/QueryBuilder'; 
// Если основной макет MainLayout еще не создан, его можно добавить позже
// import MainLayout from '../components/Layout/MainLayout'; // Пример

const { Content } = Layout;
const { Title } = Typography;

const DataExplorerPage: React.FC = () => {
    return (
        // Если используете MainLayout, оберните Content в него
        // <MainLayout> 
        <Content style={{ padding: '20px', margin: '0 auto', maxWidth: '1200px' }}>
            <Title level={2} style={{ textAlign: 'center', marginBottom: '24px' }}>
                Исследователь Данных
            </Title>
            <QueryBuilder />
        </Content>
        // </MainLayout>
    );
};

export default DataExplorerPage;