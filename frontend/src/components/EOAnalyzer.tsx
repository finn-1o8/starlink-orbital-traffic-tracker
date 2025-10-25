/**
 * EO Interference Analyzer Component
 * Allows users to analyze when Starlink satellites interfere with EO imaging
 */
import { useState } from 'react';
import { Satellite, MapPin, Calendar, Download, Loader2 } from 'lucide-react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { eoApi } from '../services/api';
import type { EOAnalysisRequest, EOAnalysisResult } from '../types';

interface EOAnalyzerProps {
  onClose: () => void;
}

function EOAnalyzer({ onClose }: EOAnalyzerProps) {
  const [formData, setFormData] = useState<EOAnalysisRequest>({
    eo_preset: 'sentinel-2a',
    duration_hours: 24,
    fov_angle_degrees: 5.0,
  });
  
  const [targetRegion, setTargetRegion] = useState({
    lat: 40.7128,
    lon: -74.0060,
    radius_km: 100,
  });

  // Fetch available presets
  const { data: presets } = useQuery({
    queryKey: ['eo-presets'],
    queryFn: () => eoApi.getPresets(),
  });

  // Analysis mutation
  const analysisMutation = useMutation({
    mutationFn: (request: EOAnalysisRequest) => eoApi.analyze(request),
  });

  const handleAnalyze = () => {
    const request: EOAnalysisRequest = {
      ...formData,
      target_region: targetRegion,
    };
    analysisMutation.mutate(request);
  };

  const handleExportCSV = (result: EOAnalysisResult) => {
    const rows = [
      ['Time', 'Status', 'Duration (min)', 'Interfering Satellites', 'Max Elevation'],
      ...result.clean_windows.map(w => [
        w.start,
        'Clean',
        w.duration_minutes,
        '0',
        w.max_elevation || 'N/A',
      ]),
      ...result.interference_events.map(e => [
        e.time,
        'Interfered',
        e.duration_minutes,
        e.interfering_satellites.map(s => s.name).join('; '),
        e.max_elevation || 'N/A',
      ]),
    ];

    const csv = rows.map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `eo-analysis-${new Date().toISOString()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fade-in">
      <div className="bg-space-800 rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto m-4">
        {/* Header */}
        <div className="sticky top-0 bg-space-800 border-b border-space-700 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Satellite className="w-6 h-6 text-accent-cyan" />
            <h2 className="text-xl font-semibold text-white">
              EO Interference Analyzer
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Form */}
        <div className="p-6 space-y-6">
          {/* EO Satellite Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              EO Satellite
            </label>
            <select
              value={formData.eo_preset}
              onChange={e => setFormData({ ...formData, eo_preset: e.target.value })}
              className="w-full bg-space-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-cyan"
            >
              {presets?.presets && Object.entries(presets.presets).map(([key, value]: [string, any]) => (
                <option key={key} value={key}>
                  {value.name} (FOV: {value.fov_degrees}°)
                </option>
              ))}
            </select>
          </div>

          {/* Target Region */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Latitude
              </label>
              <input
                type="number"
                step="0.001"
                value={targetRegion.lat}
                onChange={e => setTargetRegion({ ...targetRegion, lat: parseFloat(e.target.value) })}
                className="w-full bg-space-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-cyan"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Longitude
              </label>
              <input
                type="number"
                step="0.001"
                value={targetRegion.lon}
                onChange={e => setTargetRegion({ ...targetRegion, lon: parseFloat(e.target.value) })}
                className="w-full bg-space-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-cyan"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Radius (km)
              </label>
              <input
                type="number"
                value={targetRegion.radius_km}
                onChange={e => setTargetRegion({ ...targetRegion, radius_km: parseFloat(e.target.value) })}
                className="w-full bg-space-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-cyan"
              />
            </div>
          </div>

          {/* Duration */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Analysis Duration (hours)
            </label>
            <input
              type="number"
              min="1"
              max="168"
              value={formData.duration_hours}
              onChange={e => setFormData({ ...formData, duration_hours: parseInt(e.target.value) })}
              className="w-full bg-space-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-cyan"
            />
          </div>

          {/* Analyze Button */}
          <button
            onClick={handleAnalyze}
            disabled={analysisMutation.isPending}
            className="w-full bg-accent-cyan text-space-900 px-6 py-3 rounded-lg hover:bg-cyan-400 transition-colors font-medium flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {analysisMutation.isPending ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Calendar className="w-5 h-5" />
                <span>Run Analysis</span>
              </>
            )}
          </button>

          {/* Results */}
          {analysisMutation.isSuccess && analysisMutation.data && (
            <div className="bg-space-700 rounded-lg p-6 space-y-4 animate-fade-in">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white">Analysis Results</h3>
                <button
                  onClick={() => handleExportCSV(analysisMutation.data)}
                  className="flex items-center space-x-2 text-accent-cyan hover:text-cyan-400 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  <span className="text-sm">Export CSV</span>
                </button>
              </div>

              {/* Summary Stats */}
              <div className="grid grid-cols-4 gap-4">
                <div className="bg-space-800 rounded p-3">
                  <div className="text-xs text-gray-400">Total Passes</div>
                  <div className="text-2xl font-bold text-white font-mono">
                    {analysisMutation.data.total_passes}
                  </div>
                </div>
                <div className="bg-space-800 rounded p-3">
                  <div className="text-xs text-gray-400">Clean Passes</div>
                  <div className="text-2xl font-bold text-accent-green font-mono">
                    {analysisMutation.data.clean_passes}
                  </div>
                </div>
                <div className="bg-space-800 rounded p-3">
                  <div className="text-xs text-gray-400">Interfered</div>
                  <div className="text-2xl font-bold text-accent-red font-mono">
                    {analysisMutation.data.interfered_passes}
                  </div>
                </div>
                <div className="bg-space-800 rounded p-3">
                  <div className="text-xs text-gray-400">Interference</div>
                  <div className="text-2xl font-bold text-accent-yellow font-mono">
                    {analysisMutation.data.interference_percentage}%
                  </div>
                </div>
              </div>

              {/* Clean Windows */}
              <div>
                <h4 className="text-sm font-medium text-gray-300 mb-2">
                  Clean Imaging Windows ({analysisMutation.data.clean_windows.length})
                </h4>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {analysisMutation.data.clean_windows.map((window, idx) => (
                    <div key={idx} className="bg-space-800 rounded p-3 flex items-center justify-between">
                      <div>
                        <div className="text-sm text-white font-mono">
                          {new Date(window.start).toLocaleString()}
                        </div>
                        <div className="text-xs text-gray-400">
                          Duration: {window.duration_minutes} minutes
                        </div>
                      </div>
                      <div className="px-3 py-1 bg-accent-green text-white rounded text-xs font-medium">
                        CLEAN
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Interference Events */}
              {analysisMutation.data.interference_events.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-300 mb-2">
                    Interference Events ({analysisMutation.data.interference_events.length})
                  </h4>
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {analysisMutation.data.interference_events.map((event, idx) => (
                      <div key={idx} className="bg-space-800 rounded p-3">
                        <div className="flex items-center justify-between mb-2">
                          <div className="text-sm text-white font-mono">
                            {new Date(event.time).toLocaleString()}
                          </div>
                          <div className="px-3 py-1 bg-accent-red text-white rounded text-xs font-medium">
                            BLOCKED
                          </div>
                        </div>
                        <div className="text-xs text-gray-400">
                          {event.interfering_satellites.length} interfering satellites
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Error */}
          {analysisMutation.isError && (
            <div className="bg-accent-red bg-opacity-10 border border-accent-red rounded-lg p-4 text-accent-red">
              <p className="font-medium">Analysis Failed</p>
              <p className="text-sm mt-1">
                {analysisMutation.error instanceof Error
                  ? analysisMutation.error.message
                  : 'Unknown error occurred'}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default EOAnalyzer;

