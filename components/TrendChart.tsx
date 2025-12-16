import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { EnvironmentalData, MetricType } from '../types';

interface TrendChartProps {
  data: EnvironmentalData[];
  metric: MetricType;
}

const TrendChart: React.FC<TrendChartProps> = ({ data, metric }) => {
  let dataKey: keyof EnvironmentalData = 'occupancy';
  let color = '#0ea5e9'; // sky
  let unit = '';

  switch (metric) {
    case MetricType.OCCUPANCY:
      dataKey = 'occupancy';
      color = '#0ea5e9';
      unit = '%';
      break;
    case MetricType.WATER_QUALITY:
      dataKey = 'waterQuality';
      color = '#0d9488'; // teal
      unit = ' WQI';
      break;
    case MetricType.POLLUTION:
      dataKey = 'pollutionLevel';
      color = '#8b5cf6'; // violet
      unit = '%';
      break;
    case MetricType.AIR_QUALITY:
      dataKey = 'airQuality';
      color = '#f59e0b'; // amber
      unit = ' AQI';
      break;
    case MetricType.TEMPERATURE:
      dataKey = 'temperature';
      color = '#ef4444'; // red
      unit = '°C';
      break;
  }

  return (
    <div className="w-full h-[300px] md:h-[400px]">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{
            top: 10,
            right: 30,
            left: 0,
            bottom: 0,
          }}
        >
          <defs>
            <linearGradient id={`color-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.3} />
              <stop offset="95%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
          <XAxis 
            dataKey="date" 
            stroke="#64748b" 
            fontSize={12} 
            tickLine={false}
            axisLine={false}
          />
          <YAxis 
            stroke="#64748b" 
            fontSize={12} 
            tickLine={false} 
            axisLine={false}
            tickFormatter={(val) => `${val}${unit}`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
            }}
            formatter={(value: number) => [`${value}${unit}`, metric]}
            labelStyle={{ color: '#64748b', marginBottom: '4px' }}
          />
          <Area
            type="monotone"
            dataKey={dataKey}
            stroke={color}
            strokeWidth={3}
            fillOpacity={1}
            fill={`url(#color-${dataKey})`}
            animationDuration={1500}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TrendChart;