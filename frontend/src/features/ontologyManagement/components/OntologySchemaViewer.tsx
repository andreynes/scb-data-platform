// frontend/src/features/ontologyManagement/components/OntologySchemaViewer.tsx
import React from 'react';
import { Descriptions, Spin, Alert, Table, Tag } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useAppSelector } from '../../../app/hooks'; // Наши типизированные хуки
import {
  selectOntologySchema,
  selectOntologyIsLoading,
  selectOntologyError,
} from '../slice'; 
import type { OntologySchema, OntologyAttribute } from '../../../services/generated'; // Типы

// Тип для строки таблицы атрибутов
interface AttributeTableRow extends OntologyAttribute {
  key: string; // React требует key для элементов списка
}

const OntologySchemaViewer: React.FC = () => {
  const schema = useAppSelector(selectOntologySchema);
  const isLoading = useAppSelector(selectOntologyIsLoading);
  const error = useAppSelector(selectOntologyError);

  if (isLoading) {
    return <Spin tip="Загрузка схемы онтологии..." size="large"><div style={{ height: '200px' }} /></Spin>;
  }

  if (error) {
    return <Alert message="Ошибка загрузки схемы онтологии" description={error} type="error" showIcon />;
  }

  if (!schema) {
    // Это состояние может быть, если 'idle' и данные еще не запрошены,
    // или если запрос был, но схема не пришла (что должно было бы вызвать error)
    // Для MVP можно просто показать сообщение или ничего.
    // Позже, когда страница будет вызывать fetch, это состояние будет маловероятно.
    return <Alert message="Схема онтологии не доступна." type="info" showIcon />;
  }

  // Колонки для таблицы атрибутов
  const attributeColumns: ColumnsType<AttributeTableRow> = [
    {
      title: 'Имя атрибута (Техн.)',
      dataIndex: 'name',
      key: 'name',
      sorter: (a, b) => a.name.localeCompare(b.name),
    },
    {
      title: 'Тип данных',
      dataIndex: 'type',
      key: 'type',
      width: 150,
    },
    {
      title: 'Описание / Название',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: 'Роль',
      dataIndex: 'role',
      key: 'role',
      width: 120,
      render: (role) => (role ? <Tag color={role === 'measure' ? 'blue' : 'green'}>{role}</Tag> : '-'),
    },
    {
      title: 'Справочник',
      dataIndex: 'vocabulary',
      key: 'vocabulary',
      render: (vocab) => vocab || '-',
      width: 150,
    },
    // Можно добавить другие поля, например, is_nullable, default_value, is_pii
  ];

  const attributesData: AttributeTableRow[] = schema.attributes
    ? schema.attributes.map(attr => ({ ...attr, key: attr.name }))
    : [];

  return (
    <div>
      <Descriptions title={`Онтология (Версия: ${schema.version || 'N/A'})`} bordered column={1} size="small">
        <Descriptions.Item label="Описание версии">
          {schema.description || '-'}
        </Descriptions.Item>
      </Descriptions>

      <h3 style={{ marginTop: '24px', marginBottom: '16px' }}>Атрибуты:</h3>
      <Table
        columns={attributeColumns}
        dataSource={attributesData}
        pagination={false} // Для MVP отключаем пагинацию, если атрибутов много, можно включить
        size="small"
        bordered
        // rowKey="name" // Если 'name' уникален
      />

      {/* 
      В будущем здесь можно добавить отображение иерархий (schema.hierarchies)
      и возможность выбора и просмотра справочников (из vocabularies, которые мы тоже должны будем получать)
      <h3 style={{ marginTop: '24px', marginBottom: '16px' }}>Иерархии:</h3>
      <pre>{JSON.stringify(schema.hierarchies, null, 2)}</pre>
      */}
    </div>
  );
};

export default OntologySchemaViewer;