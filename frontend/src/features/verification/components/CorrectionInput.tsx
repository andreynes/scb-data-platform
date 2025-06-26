// frontend/src/features/verification/components/CorrectionInput.tsx
import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import { Form, Input, Button, Select, Checkbox, Space } from 'antd';
import { OntologyAttribute } from '../../../services/generated';
import { CorrectionInfo, SelectedCellInfo } from '../types'; // Предполагаем, что эти типы определены локально

interface CorrectionInputProps {
  cellData: SelectedCellInfo;
  ontologyAttributes: OntologyAttribute[];
  onSubmitCorrection: (correction: CorrectionInfo) => void;
  onCancel: () => void;
}

interface CorrectionFormData {
  attributeName: string;
  value: any;
  isNotApplicable: boolean;
}

export const CorrectionInput: React.FC<CorrectionInputProps> = ({
  cellData,
  ontologyAttributes,
  onSubmitCorrection,
  onCancel,
}) => {
  const { control, handleSubmit, watch, setValue } = useForm<CorrectionFormData>({
    defaultValues: {
      attributeName: cellData.columnKey,
      value: cellData.currentValue,
      isNotApplicable: cellData.currentValue === null,
    },
  });

  const selectedAttributeName = watch('attributeName');
  const isNotApplicable = watch('isNotApplicable');

  const selectedAttribute = ontologyAttributes.find(
    (attr) => attr.name === selectedAttributeName
  );

  const handleFormSubmit = (formData: CorrectionFormData) => {
    const correction: CorrectionInfo = {
      atomId: cellData.atomId,
      fieldName: selectedAttributeName,
      newValue: formData.isNotApplicable ? null : formData.value,
    };
    onSubmitCorrection(correction);
  };

  // Динамический рендеринг поля ввода в зависимости от типа атрибута
  const renderValueInput = () => {
    const inputDisabled = isNotApplicable;
    switch (selectedAttribute?.type) {
      case 'integer':
      case 'float':
        return <Input.Number style={{ width: '100%' }} disabled={inputDisabled} />;
      case 'date':
      case 'datetime':
        return <Input type="date" style={{ width: '100%' }} disabled={inputDisabled} />;
      default:
        return <Input disabled={inputDisabled} />;
    }
  };

  return (
    <Form layout="vertical" onFinish={handleSubmit(handleFormSubmit)}>
      <Form.Item label="Исходное значение">
        <Input value={String(cellData.currentValue ?? 'пусто')} disabled />
      </Form.Item>

      <Form.Item label="Атрибут Онтологии" required>
        <Controller
          name="attributeName"
          control={control}
          render={({ field }) => (
            <Select {...field} showSearch>
              {ontologyAttributes.map((attr) => (
                <Select.Option key={attr.name} value={attr.name}>
                  {attr.description || attr.name} ({attr.type})
                </Select.Option>
              ))}
            </Select>
          )}
        />
      </Form.Item>
      
      <Form.Item label="Новое значение">
        <Controller name="value" control={control} render={({ field }) => renderValueInput()} />
      </Form.Item>
      
      <Form.Item name="isNotApplicable" valuePropName="checked">
        <Controller
          name="isNotApplicable"
          control={control}
          render={({ field }) => <Checkbox {...field} checked={field.value}>Значение неприменимо (N/A)</Checkbox>}
        />
      </Form.Item>
      
      <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
        <Button onClick={onCancel}>Отмена</Button>
        <Button type="primary" htmlType="submit">Сохранить исправление</Button>
      </Space>
    </Form>
  );
};