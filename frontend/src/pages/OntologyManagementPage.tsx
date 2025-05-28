// frontend/src/pages/OntologyManagementPage.tsx
import React, { useEffect } from 'react';
import { Typography, Spin, Alert } from 'antd';
import { useAppDispatch, useAppSelector } from '../app/hooks'; // Наши типизированные хуки
import OntologySchemaViewer from '../features/ontologyManagement/components/OntologySchemaViewer';
import {
  fetchActiveOntologySchema, // Наш Thunk
  selectOntologyIsLoading,
  selectOntologyError,
  selectOntologySchema // Нам не нужен весь schema здесь, только его наличие для useEffect
} from '../features/ontologyManagement/ontologySlice';

const { Title } = Typography;

const OntologyManagementPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const isLoading = useAppSelector(selectOntologyIsLoading);
  const error = useAppSelector(selectOntologyError);
  const schema = useAppSelector(selectOntologySchema); // Получаем схему для проверки, загружена ли

  useEffect(() => {
    // Загружаем схему при монтировании компонента, если она еще не загружена
    // и не находится в процессе загрузки или ошибки (чтобы избежать повторных запросов при ошибке)
    if (!schema && !isLoading && !error) {
      dispatch(fetchActiveOntologySchema());
    }
    // Зависимость от dispatch, schema, isLoading, error для корректной работы useEffect
  }, [dispatch, schema, isLoading, error]);

  // Отображаем глобальный индикатор загрузки или ошибку, если OntologySchemaViewer
  // сам не обрабатывает эти верхнеуровневые состояния (хотя в нашем случае он их обрабатывает)
  // Этот блок можно упростить или убрать, если OntologySchemaViewer полностью самодостаточен.
  if (isLoading && !schema) { // Показываем Spin только если схема ЕЩЕ НЕ загружена
    return <Spin tip="Загрузка данных онтологии..." size="large" style={{ display: 'block', marginTop: '50px' }} />;
  }

  // Ошибку лучше обрабатывать в OntologySchemaViewer, но можно и здесь для глобальных проблем
  // if (error && !schema) {
  //   return <Alert message="Не удалось загрузить данные онтологии" description={error} type="error" showIcon />;
  // }

  return (
    <div>
      <Title level={2} style={{ marginBottom: '24px' }}>Управление Онтологией</Title>
      {/* 
        OntologySchemaViewer сам получит данные из Redux store,
        но мы вызвали fetch здесь, чтобы инициировать загрузку.
        Если бы OntologySchemaViewer принимал schema, isLoading, error как props,
        мы бы передали их сюда. В нашей текущей реализации OntologySchemaViewer
        сам использует селекторы.
      */}
      <OntologySchemaViewer />
    </div>
  );
};

export default OntologyManagementPage;