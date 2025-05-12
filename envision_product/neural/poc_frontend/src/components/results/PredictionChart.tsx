import React, { useState, useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Box, Typography, Paper } from '@mui/material';
import { PredictionResult } from '../../types/data.types';
import { formatYearMonth } from '../../utils/formatters';

interface PredictionChartProps {
  results: PredictionResult[];
  title?: string;
}

const PredictionChart: React.FC<PredictionChartProps> = ({
  results,
  title = 'Predicted Order Volume',
}) => {
  // Prepare data for chart
  const chartData = useMemo(() => {
    if (!results || results.length === 0) return [];

    // Group by source city, destination city, order type, and date
    const groupedData: Record<string, Record<string, number>> = {};

    results.forEach((result) => {
      const key = `${result['SOURCE CITY']}-${result['DESTINATION CITY']}-${result['ORDER TYPE']}`;
      const date = result['PREDICTION DATE'];

      if (!groupedData[key]) {
        groupedData[key] = {};
      }

      groupedData[key][date] = result['PREDICTED ORDER VOLUME'];
    });

    // Convert to chart data format
    const allDates = Array.from(new Set(results.map((r) => r['PREDICTION DATE']))).sort();
    
    return allDates.map((date) => {
      const dataPoint: Record<string, any> = { date };
      Object.keys(groupedData).forEach((key) => {
        dataPoint[key] = groupedData[key][date] || 0;
      });
      return dataPoint;
    });
  }, [results]);

  // Generate lines for each source-destination-type combination
  const lines = useMemo(() => {
    if (!results || results.length === 0) return [];

    const uniqueCombinations = Array.from(
      new Set(
        results.map(
          (r) => `${r['SOURCE CITY']}-${r['DESTINATION CITY']}-${r['ORDER TYPE']}`
        )
      )
    );

    // Generate random colors for lines
    const colors = [
      '#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#0088FE', '#00C49F',
      '#FFBB28', '#FF8042', '#a4de6c', '#d0ed57'
    ];

    return uniqueCombinations.map((key, index) => ({
      key,
      color: colors[index % colors.length],
      name: key,
    }));
  }, [results]);

  if (!results || results.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', my: 4 }}>
        <Typography variant="body1" color="textSecondary">
          No prediction data available
        </Typography>
      </Box>
    );
  }

  return (
    <Paper sx={{ p: 3, mb: 4 }}>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Box sx={{ height: 400, width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tickFormatter={(value) => formatYearMonth(value)}
            />
            <YAxis />
            <Tooltip
              labelFormatter={(value) => `Date: ${formatYearMonth(value as string)}`}
              formatter={(value, name, props) => {
                const formattedName = typeof name === 'string' ? name.split('-').join(' → ') : name;
                return [value, formattedName];
              }}
            />
            <Legend formatter={(value) => typeof value === 'string' ? value.split('-').join(' → ') : value} />
            {lines.map((line) => (
              <Line
                key={line.key}
                type="monotone"
                dataKey={line.key}
                stroke={line.color}
                name={line.name}
                activeDot={{ r: 8 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
};

export default PredictionChart; 