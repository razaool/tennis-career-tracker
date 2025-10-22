import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

interface TrajectoryPoint {
  match_number: number;
  date: string;
  rating: number;
}

interface PlayerTrajectory {
  name: string;
  data_points: number;
  trajectory: TrajectoryPoint[];
}

interface TrajectoryChartProps {
  data: PlayerTrajectory[];
  ratingSystem: 'elo' | 'tsr' | 'glicko2';
  title: string;
  height?: number;
}

const COLORS = [
  '#3B82F6', // Blue
  '#EF4444', // Red  
  '#10B981', // Green
  '#F59E0B', // Orange
  '#8B5CF6', // Purple
  '#EC4899', // Pink
  '#06B6D4', // Cyan
  '#84CC16', // Lime
];

export default function TrajectoryChart({ 
  data, 
  ratingSystem, 
  title, 
  height = 400 
}: TrajectoryChartProps) {
  // Transform data for Recharts using dates
  const chartData = React.useMemo(() => {
    // Collect all unique dates from all players
    const allDates = new Set<string>();
    data.forEach(player => {
      player.trajectory.forEach(point => {
        allDates.add(point.date);
      });
    });
    
    // Sort dates chronologically
    const sortedDates = Array.from(allDates).sort();
    
    // Create chart points for each date
    const chartPoints: any[] = [];
    
    sortedDates.forEach(date => {
      const point: any = { date };
      
      data.forEach(player => {
        // Find the trajectory point for this date
        const trajectoryPoint = player.trajectory.find(p => p.date === date);
        if (trajectoryPoint) {
          point[player.name] = trajectoryPoint.rating;
        }
      });
      
      chartPoints.push(point);
    });
    
    return chartPoints;
  }, [data]);

  // Calculate appropriate Y-axis range
  const yAxisRange = React.useMemo(() => {
    const allRatings = data.flatMap(player => 
      player.trajectory.map(point => point.rating)
    ).filter(rating => rating != null);
    
    if (allRatings.length === 0) return [0, 3000];
    
    const minRating = Math.min(...allRatings);
    const maxRating = Math.max(...allRatings);
    
    // Set minimum to 1500 (reasonable starting ELO) or 100 below the actual minimum
    const yMin = Math.min(1500, minRating - 100);
    // Set maximum to 100 above the actual maximum
    const yMax = maxRating + 100;
    
    return [yMin, yMax];
  }, [data]);

  const getSystemLabel = () => {
    switch (ratingSystem) {
      case 'tsr': return 'TSR';
      case 'glicko2': return 'Glicko-2';
      default: return 'ELO';
    }
  };

  const formatTooltipValue = (value: number) => {
    return Math.round(value);
  };

  const formatTooltipLabel = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const formatXAxisTick = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.getFullYear().toString();
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="mb-6">
        <h3 className="text-xl font-bold text-white mb-2">{title}</h3>
        <p className="text-sm text-gray-400">
          Career progression based on {getSystemLabel()} ratings
        </p>
      </div>
      
      <div className="mb-4">
        <ResponsiveContainer width="100%" height={height}>
          <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="date" 
              stroke="#9CA3AF"
              tickFormatter={formatXAxisTick}
              label={{ value: 'Year', position: 'insideBottom', offset: -10, style: { textAnchor: 'middle', fill: '#9CA3AF' } }}
            />
            <YAxis 
              stroke="#9CA3AF"
              domain={yAxisRange}
              label={{ value: `${getSystemLabel()} Rating`, angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#9CA3AF' } }}
            />
            <ReferenceLine y={1500} stroke="#6B7280" strokeDasharray="2 2" />
            <Tooltip
              contentStyle={{ 
                backgroundColor: '#1F2937', 
                border: '1px solid #374151', 
                borderRadius: '8px',
                color: '#F9FAFB'
              }}
              labelStyle={{ color: '#F9FAFB', fontWeight: 'bold' }}
              itemStyle={{ color: '#F9FAFB' }}
              formatter={(value: number) => [formatTooltipValue(value), getSystemLabel()]}
              labelFormatter={formatTooltipLabel}
            />
            
            {data.map((player, index) => (
              <Line
                key={player.name}
                type="monotone"
                dataKey={player.name}
                stroke={COLORS[index % COLORS.length]}
                strokeWidth={2.5}
                dot={false}
                activeDot={{ r: 4, stroke: COLORS[index % COLORS.length], strokeWidth: 2 }}
                connectNulls={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      {/* Legend */}
      <div className="flex flex-wrap gap-4 justify-center">
        {data.map((player, index) => (
          <div key={player.name} className="flex items-center space-x-2">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: COLORS[index % COLORS.length] }}
            />
            <span className="text-sm text-gray-300 font-medium">{player.name}</span>
            <span className="text-xs text-gray-500">({player.data_points} matches)</span>
          </div>
        ))}
      </div>
    </div>
  );
}
