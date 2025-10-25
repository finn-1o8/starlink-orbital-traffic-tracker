/**
 * Dashboard Component
 * Analytics dashboard with charts and metrics
 */
import { useState } from 'react';
import { X, TrendingUp, Activity, AlertTriangle } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { congestionApi } from '../services/api';
import type { SatellitePosition } from '../types';

interface DashboardProps {
  positions: SatellitePosition[];
  onClose: () => void;
}

const COLORS = ['#ef4444', '#00d9ff', '#facc15', '#6b7280'];

function Dashboard({ positions, onClose }: DashboardProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'congestion' | 'eo'>('overview');

  // Fetch altitude distribution
  const { data: altitudeData } = useQuery({
    queryKey: ['altitude-distribution'],
    queryFn: () => congestionApi.getAltitudeDistribution(),
    refetchInterval: 60000, // Refresh every minute
  });

  // Calculate stats
  const stats = {
    total: positions.length,
    avgAltitude: positions.reduce((sum, p) => sum + p.alt_km, 0) / positions.length || 0,
    avgVelocity: positions.reduce((sum, p) => sum + p.velocity_km_s, 0) / positions.length || 0,
  };

  // Prepare chart data
  const chartData = altitudeData
    ? [
        { name: '340-360 km', value: altitudeData.altitude_bands['340-360'], color: COLORS[0] },
        { name: '500-570 km', value: altitudeData.altitude_bands['500-570'], color: COLORS[1] },
        { name: '1100-1325 km', value: altitudeData.altitude_bands['1100-1325'], color: COLORS[2] },
        { name: 'Other', value: altitudeData.altitude_bands['other'], color: COLORS[3] },
      ]
    : [];

  return (
    <div className="absolute bottom-0 left-0 right-0 bg-space-800 border-t border-space-700 animate-fade-in">
      <div className="h-96 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-space-700">
          <div className="flex items-center space-x-4">
            <h2 className="text-lg font-semibold text-white">Analytics Dashboard</h2>
            
            {/* Tabs */}
            <div className="flex space-x-2">
              <button
                onClick={() => setActiveTab('overview')}
                className={`px-4 py-1 rounded text-sm ${
                  activeTab === 'overview'
                    ? 'bg-accent-cyan text-space-900 font-medium'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Overview
              </button>
              <button
                onClick={() => setActiveTab('congestion')}
                className={`px-4 py-1 rounded text-sm ${
                  activeTab === 'congestion'
                    ? 'bg-accent-cyan text-space-900 font-medium'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Congestion
              </button>
              <button
                onClick={() => setActiveTab('eo')}
                className={`px-4 py-1 rounded text-sm ${
                  activeTab === 'eo'
                    ? 'bg-accent-cyan text-space-900 font-medium'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                EO Analysis
              </button>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'overview' && (
            <div className="grid grid-cols-3 gap-6">
              {/* Stats Cards */}
              <div className="bg-space-700 rounded-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <Activity className="w-5 h-5 text-accent-cyan" />
                  <span className="text-xs text-gray-400">TOTAL</span>
                </div>
                <div className="text-3xl font-bold text-white font-mono">
                  {stats.total.toLocaleString()}
                </div>
                <div className="text-sm text-gray-400 mt-1">Active Satellites</div>
              </div>

              <div className="bg-space-700 rounded-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <TrendingUp className="w-5 h-5 text-accent-green" />
                  <span className="text-xs text-gray-400">AVERAGE</span>
                </div>
                <div className="text-3xl font-bold text-white font-mono">
                  {stats.avgAltitude.toFixed(0)}
                </div>
                <div className="text-sm text-gray-400 mt-1">Altitude (km)</div>
              </div>

              <div className="bg-space-700 rounded-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <AlertTriangle className="w-5 h-5 text-accent-yellow" />
                  <span className="text-xs text-gray-400">VELOCITY</span>
                </div>
                <div className="text-3xl font-bold text-white font-mono">
                  {stats.avgVelocity.toFixed(2)}
                </div>
                <div className="text-sm text-gray-400 mt-1">Speed (km/s)</div>
              </div>

              {/* Charts */}
              {chartData.length > 0 && (
                <>
                  <div className="col-span-2 bg-space-700 rounded-lg p-6">
                    <h3 className="text-sm font-medium text-gray-300 mb-4">
                      Altitude Distribution
                    </h3>
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#303746" />
                        <XAxis dataKey="name" stroke="#8b92a3" fontSize={12} />
                        <YAxis stroke="#8b92a3" fontSize={12} />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#1a1f2e',
                            border: '1px solid #303746',
                            borderRadius: '8px',
                            color: '#e6e8eb',
                          }}
                        />
                        <Bar dataKey="value" fill="#00d9ff" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="bg-space-700 rounded-lg p-6">
                    <h3 className="text-sm font-medium text-gray-300 mb-4">
                      Distribution
                    </h3>
                    <ResponsiveContainer width="100%" height={200}>
                      <PieChart>
                        <Pie
                          data={chartData}
                          cx="50%"
                          cy="50%"
                          innerRadius={40}
                          outerRadius={80}
                          paddingAngle={2}
                          dataKey="value"
                        >
                          {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#1a1f2e',
                            border: '1px solid #303746',
                            borderRadius: '8px',
                            color: '#e6e8eb',
                          }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </>
              )}
            </div>
          )}

          {activeTab === 'congestion' && (
            <div className="text-center text-gray-400 py-12">
              <AlertTriangle className="w-12 h-12 mx-auto mb-4 text-accent-yellow" />
              <p>Congestion analysis coming soon</p>
              <p className="text-sm mt-2">
                Select a region on the globe to analyze orbital traffic
              </p>
            </div>
          )}

          {activeTab === 'eo' && (
            <div className="text-center text-gray-400 py-12">
              <Activity className="w-12 h-12 mx-auto mb-4 text-accent-cyan" />
              <p>EO interference analysis coming soon</p>
              <p className="text-sm mt-2">
                Run analysis to see when Starlink satellites interfere with imaging
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;


