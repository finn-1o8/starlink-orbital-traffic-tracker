/**
 * Dashboard Component
 * Analytics panel: constellation overview, regional congestion and the EO analysis entry point
 */
import { useState } from 'react';
import { X, TrendingUp, Activity, AlertTriangle, Satellite as SatelliteIcon } from 'lucide-react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { congestionApi } from '../services/api';
import type { CongestionRequest, SatellitePosition } from '../types';

interface DashboardProps {
  positions: SatellitePosition[];
  onClose: () => void;
  onOpenEOAnalyzer: () => void;
}

const COLORS = ['#ef4444', '#00d9ff', '#facc15', '#6b7280'];
const inputClass =
  'w-full bg-space-800 text-white px-3 py-2 rounded-lg border border-white/10 focus:outline-none focus:ring-1 focus:ring-accent-cyan text-sm';

function CongestionPanel() {
  const [form, setForm] = useState<Required<Omit<CongestionRequest, 'time'>>>({
    lat: 51.5,
    lon: -0.12,
    radius_km: 1000,
    alt_min: 500,
    alt_max: 600,
  });

  const analysis = useMutation({
    mutationFn: (request: CongestionRequest) => congestionApi.analyze(request),
  });

  const update = (key: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [key]: parseFloat(e.target.value) });

  const fields: Array<[keyof typeof form, string]> = [
    ['lat', 'Latitude'],
    ['lon', 'Longitude'],
    ['radius_km', 'Radius (km)'],
    ['alt_min', 'Min altitude (km)'],
    ['alt_max', 'Max altitude (km)'],
  ];

  return (
    <div className="grid grid-cols-3 gap-6">
      <div className="bg-space-700 rounded-lg p-6 space-y-3">
        <h3 className="text-sm font-medium text-gray-300">Region and altitude band</h3>
        {fields.map(([key, label]) => (
          <label key={key} className="block text-xs text-gray-400">
            {label}
            <input type="number" step="any" value={form[key]} onChange={update(key)} className={inputClass} />
          </label>
        ))}
        <button
          onClick={() => analysis.mutate(form)}
          disabled={analysis.isPending || form.alt_min >= form.alt_max}
          className="w-full bg-accent-cyan text-space-900 px-4 py-2 rounded-lg hover:bg-cyan-400 transition-colors font-medium text-sm disabled:opacity-50"
        >
          {analysis.isPending ? 'Analyzing...' : 'Analyze region'}
        </button>
        {analysis.isError && (
          <p className="text-xs text-accent-red">
            {analysis.error instanceof Error ? analysis.error.message : 'Analysis failed'}
          </p>
        )}
      </div>

      <div className="col-span-2 bg-space-700 rounded-lg p-6">
        {analysis.data ? (
          <div className="grid grid-cols-2 gap-4">
            <Metric label="Satellites in region" value={analysis.data.total_satellites.toLocaleString()} />
            <Metric label="Density (per 1000 km³)" value={analysis.data.density_per_1000km3.toFixed(4)} />
            <Metric label="Mean spacing" value={`${analysis.data.mean_spacing_km.toFixed(1)} km`} />
            <Metric label="Closest approach" value={`${analysis.data.closest_approach_km.toFixed(1)} km`} />
            <p className="col-span-2 text-xs text-gray-500">
              Cylinder of radius {analysis.data.region?.radius_km} km between {analysis.data.altitude_band?.min_km} and{' '}
              {analysis.data.altitude_band?.max_km} km at {new Date(analysis.data.timestamp).toLocaleString()}.
            </p>
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-gray-400 text-sm">
            <AlertTriangle className="w-10 h-10 mb-3 text-accent-yellow" />
            <p>Choose a region and altitude band, then run the analysis.</p>
          </div>
        )}
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-space-800 rounded p-4">
      <div className="text-xs text-gray-400">{label}</div>
      <div className="text-2xl font-bold text-white font-mono">{value}</div>
    </div>
  );
}

function Dashboard({ positions, onClose, onOpenEOAnalyzer }: DashboardProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'congestion' | 'eo'>('overview');

  const { data: altitudeData } = useQuery({
    queryKey: ['altitude-distribution'],
    queryFn: () => congestionApi.getAltitudeDistribution(),
    refetchInterval: 60000,
  });

  const stats = {
    total: positions.length,
    avgAltitude: positions.reduce((sum, p) => sum + p.alt_km, 0) / positions.length || 0,
    avgVelocity: positions.reduce((sum, p) => sum + p.velocity_km_s, 0) / positions.length || 0,
  };

  const chartData = altitudeData
    ? [
        { name: '340-360 km', value: altitudeData.altitude_bands['340-360'], color: COLORS[0] },
        { name: '500-570 km', value: altitudeData.altitude_bands['500-570'], color: COLORS[1] },
        { name: '1100-1325 km', value: altitudeData.altitude_bands['1100-1325'], color: COLORS[2] },
        { name: 'Other', value: altitudeData.altitude_bands['other'], color: COLORS[3] },
      ]
    : [];

  const tabs: Array<['overview' | 'congestion' | 'eo', string]> = [
    ['overview', 'Overview'],
    ['congestion', 'Congestion'],
    ['eo', 'EO Analysis'],
  ];

  return (
    <div className="absolute bottom-0 left-0 right-0 bg-space-800 border-t border-space-700 animate-fade-in">
      <div className="h-96 flex flex-col">
        <div className="flex items-center justify-between px-6 py-4 border-b border-space-700">
          <div className="flex items-center space-x-4">
            <h2 className="text-lg font-semibold text-white">Analytics Dashboard</h2>
            <div className="flex space-x-2">
              {tabs.map(([key, label]) => (
                <button
                  key={key}
                  onClick={() => setActiveTab(key)}
                  className={`px-4 py-1 rounded text-sm ${
                    activeTab === key ? 'bg-accent-cyan text-space-900 font-medium' : 'text-gray-400 hover:text-white'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors" aria-label="Close">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'overview' && (
            <div className="grid grid-cols-3 gap-6">
              <div className="bg-space-700 rounded-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <Activity className="w-5 h-5 text-accent-cyan" />
                  <span className="text-xs text-gray-400">TOTAL</span>
                </div>
                <div className="text-3xl font-bold text-white font-mono">{stats.total.toLocaleString()}</div>
                <div className="text-sm text-gray-400 mt-1">Tracked Satellites</div>
              </div>

              <div className="bg-space-700 rounded-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <TrendingUp className="w-5 h-5 text-accent-green" />
                  <span className="text-xs text-gray-400">AVERAGE</span>
                </div>
                <div className="text-3xl font-bold text-white font-mono">{stats.avgAltitude.toFixed(0)}</div>
                <div className="text-sm text-gray-400 mt-1">Altitude (km)</div>
              </div>

              <div className="bg-space-700 rounded-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <AlertTriangle className="w-5 h-5 text-accent-yellow" />
                  <span className="text-xs text-gray-400">VELOCITY</span>
                </div>
                <div className="text-3xl font-bold text-white font-mono">{stats.avgVelocity.toFixed(2)}</div>
                <div className="text-sm text-gray-400 mt-1">Speed (km/s)</div>
              </div>

              {chartData.length > 0 && (
                <>
                  <div className="col-span-2 bg-space-700 rounded-lg p-6">
                    <h3 className="text-sm font-medium text-gray-300 mb-4">Altitude Distribution</h3>
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
                    <h3 className="text-sm font-medium text-gray-300 mb-4">Distribution</h3>
                    <ResponsiveContainer width="100%" height={200}>
                      <PieChart>
                        <Pie data={chartData} cx="50%" cy="50%" innerRadius={40} outerRadius={80} paddingAngle={2} dataKey="value">
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

          {activeTab === 'congestion' && <CongestionPanel />}

          {activeTab === 'eo' && (
            <div className="text-center text-gray-400 py-10">
              <SatelliteIcon className="w-12 h-12 mx-auto mb-4 text-accent-cyan" />
              <p className="text-white">Earth-observation interference analysis</p>
              <p className="text-sm mt-2 max-w-xl mx-auto">
                Propagates an EO satellite and the whole Starlink catalogue and flags the passes during which a Starlink
                satellite crosses the sensor's nadir-pointed field of view.
              </p>
              <button
                onClick={onOpenEOAnalyzer}
                className="mt-5 bg-accent-cyan text-space-900 px-5 py-2 rounded-lg hover:bg-cyan-400 transition-colors font-medium text-sm"
              >
                Open EO Analyzer
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
