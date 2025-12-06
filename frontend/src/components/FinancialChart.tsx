import React from 'react';
import { motion } from 'framer-motion';

interface FinancialChartProps {
  data: number[];
}

const FinancialChart: React.FC<FinancialChartProps> = ({ data }) => {
  if (data.length < 2) {
    return (
      <div className="h-full w-full flex items-center justify-center text-gray-400 text-sm italic">
        Not enough data yet...
      </div>
    );
  }

  const maxVal = Math.max(...data) * 1.1;
  const minVal = Math.min(...data) * 0.9;
  const range = maxVal - minVal;

  // Normalize points to 0-100 range
  const points = data.map((val, i) => {
    const x = (i / (data.length - 1)) * 100;
    const y = 100 - ((val - minVal) / range) * 100;
    return `${x},${y}`;
  }).join(' ');

  return (
    <div className="h-full w-full relative p-4">
      <svg className="w-full h-full overflow-visible" viewBox="0 0 100 100" preserveAspectRatio="none">
        {/* Grid Lines */}
        <line x1="0" y1="0" x2="100" y2="0" stroke="#eee" strokeWidth="0.5" />
        <line x1="0" y1="50" x2="100" y2="50" stroke="#eee" strokeWidth="0.5" />
        <line x1="0" y1="100" x2="100" y2="100" stroke="#eee" strokeWidth="0.5" />

        {/* The Chart Line */}
        <motion.polyline
          points={points}
          fill="none"
          stroke="#10B981"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1, ease: "easeInOut" }}
        />
      </svg>
      
      {/* Labels */}
      <div className="absolute top-2 left-2 text-xs text-gray-400 font-mono">${maxVal.toFixed(0)}</div>
      <div className="absolute bottom-2 left-2 text-xs text-gray-400 font-mono">${minVal.toFixed(0)}</div>
    </div>
  );
};

export default FinancialChart;
