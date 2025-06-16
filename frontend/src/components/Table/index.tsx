import React from 'react';
import { Table } from 'antd';
import type { TableProps } from 'antd/es/table';

// Используем дженерики, чтобы компонент был типизированным
function AppTable<T extends object>(props: TableProps<T>): JSX.Element {
  // Просто возвращаем компонент Table из Ant Design, передавая ему все пропсы
  // В будущем здесь можно будет добавить кастомную логику или стили
  return <Table<T> {...props} />;
}

export default AppTable;