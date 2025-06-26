// frontend/src/components/Chart/AppLineChart.tsx
import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

interface AppLineChartProps {
  data: any[];
  xKey: string;
  yKeys: string[];
}

export const AppLineChart: React.FC<AppLineChartProps> = ({ data, xKey, yKeys }) => {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xKey} />
        <YAxis />
        <Tooltip />
        <Legend />
        {yKeys.map((key, index) => (
          <Line 
            key={key} 
            type="monotone" 
            dataKey={key} 
            // Цвета можно будет кастомизировать позже
            stroke={index % 2 === 0 ? '#8884d8' : '#82ca9d'} 
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
};