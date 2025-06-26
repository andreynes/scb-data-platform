// frontend/src/features/dataExplorer/components/DataChart.tsx
import React, { useMemo } from 'react';
import { Alert } from 'antd';
import { AppLineChart } from '../../../components/Chart/AppLineChart';
import { AtomicDataRow } from '../../../services/generated';

interface DataChartProps {
  data: AtomicDataRow[];
}

export const DataChart: React.FC<DataChartProps> = ({ data }) => {
  // useMemo, чтобы вычисления не производились на каждый рендер
  const chartConfig = useMemo(() => {
    if (!data || data.length === 0) {
      return null;
    }

    const sample = data[0];
    const keys = Object.keys(sample);

    // Простая логика: ищем ключ для оси X (первый ключ с датой/годом)
    const xKey = keys.find(k => k.includes('date') || k.includes('year')) || keys[0];

    // Ищем ключи для оси Y (все числовые поля, кроме оси X)
    const yKeys = keys.filter(
      k => k !== xKey && typeof sample[k] === 'number'
    );

    if (!xKey || yKeys.length === 0) {
      return null; // Невозможно построить график
    }

    return { xKey, yKeys };
  }, [data]);

  if (!data || data.length === 0) {
    return <p>Нет данных для отображения.</p>;
  }

  if (!chartConfig) {
    return <Alert message="Не удалось автоматически определить оси для графика." type="warning" />;
  }
  
  return (
    <AppLineChart 
      data={data} 
      xKey={chartConfig.xKey} 
      yKeys={chartConfig.yKeys} 
    />
  );
};