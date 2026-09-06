/**
 * EO Interference Analyzer Component
 * Runs the backend field-of-view analysis and presents its results
 */
import { useState } from 'react';
import { Satellite, Calendar, Download, Loader2 } from 'lucide-react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { eoApi } from '../services/api';
import type { EOAnalysisRequest, EOAnalysisResult } from '../types';

interface EOAnalyzerProps {
  onClose: () => void;
}

const inputClass =
  'w-full bg-space-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-cyan';

function EOAnalyzer({ onClose }: EOAnalyzerProps) {
  const [preset, setPreset] = useState('sentinel-2a');
  const [durationHours, setDurationHours] = useState(24);
  const [useRegion, setUseRegion] = useState(true);
  const [targetRegion, setTargetRegion] = useState({ lat: 40.7128, lon: -74.006, radius_km: 100 });

  const { data: presets } = useQuery({
    queryKey: ['eo-presets'],
    queryFn: () => eoApi.getPresets(),
  });

  const analysisMutation = useMutation({
    mutationFn: (request: EOAnalysisRequest) => eoApi.analyze(request),
  });

  const handleAnalyze = () => {
    analysisMutation.mutate({
      eo_preset: preset,
      duration_hours: durationHours,
      target_region: useRegion ? targetRegion : undefined,
    });
  };

  const handleExportCSV = (result: EOAnalysisResult) => {
    const rows = [
      ['Start', 'End', 'Status', 'Duration (min)', 'Interfering satellites', 'Closest angle off nadir (deg)'],
      ...result.clean_windows.map((w) => [w.start, w.end, 'Clean', w.duration_minutes, '', '']),
      ...result.interference_events.map((e) => [
        e.start,
        e.end,
        'Interfered',
        e.duration_minutes,
        e.interfering_satellites.map((s) => s.name).join('; '),
        Math.min(...e.interfering_satellites.map((s) => s.min_angle_deg)).toFixed(2),
      ]),
    ];
    const csv = rows.map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `eo-analysis-${new Date().toISOString()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const result = analysisMutation.data;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fade-in">
      <div className="bg-space-800 rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto m-4">
        <div className="sticky top-0 bg-space-800 border-b border-space-700 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Satellite className="w-6 h-6 text-accent-cyan" />
            <h2 className="text-xl font-semibold text-white">EO Interference Analyzer</h2>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors" aria-label="Close">
            ✕
          </button>
        </div>

        <div className="p-6 space-y-6">
          <p className="text-sm text-gray-400">
            Flags imaging passes during which a Starlink satellite sits inside the EO sensor's nadir-pointed
            field-of-view cone. Purely geometric: side-looking instruments are approximated as nadir cones.
          </p>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">EO Satellite</label>
            <select value={preset} onChange={(e) => setPreset(e.target.value)} className={inputClass}>
              {presets &&
                Object.entries(presets.presets).map(([key, value]) => (
                  <option key={key} value={key}>
                    {value.name} (FOV {value.fov_degrees}°)
                  </option>
                ))}
            </select>
            {presets?.presets[preset]?.note && (
              <p className="text-xs text-gray-500 mt-1">{presets.presets[preset].note}</p>
            )}
          </div>

          <label className="flex items-center space-x-2 text-sm text-gray-300">
            <input type="checkbox" checked={useRegion} onChange={(e) => setUseRegion(e.target.checked)} />
            <span>Restrict to passes over a target region (otherwise every orbit counts as a pass)</span>
          </label>

          {useRegion && (
            <div className="grid grid-cols-3 gap-4">
              {(
                [
                  ['lat', 'Latitude', '0.001'],
                  ['lon', 'Longitude', '0.001'],
                  ['radius_km', 'Radius (km)', '1'],
                ] as const
              ).map(([key, label, step]) => (
                <div key={key}>
                  <label className="block text-sm font-medium text-gray-300 mb-2">{label}</label>
                  <input
                    type="number"
                    step={step}
                    value={targetRegion[key]}
                    onChange={(e) => setTargetRegion({ ...targetRegion, [key]: parseFloat(e.target.value) })}
                    className={inputClass}
                  />
                </div>
              ))}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Analysis Duration (hours, max 72)</label>
            <input
              type="number"
              min="1"
              max="72"
              value={durationHours}
              onChange={(e) => setDurationHours(Math.min(72, Math.max(1, parseInt(e.target.value) || 1)))}
              className={inputClass}
            />
          </div>

          <button
            onClick={handleAnalyze}
            disabled={analysisMutation.isPending}
            className="w-full bg-accent-cyan text-space-900 px-6 py-3 rounded-lg hover:bg-cyan-400 transition-colors font-medium flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {analysisMutation.isPending ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Propagating the constellation...</span>
              </>
            ) : (
              <>
                <Calendar className="w-5 h-5" />
                <span>Run Analysis</span>
              </>
            )}
          </button>

          {result && (
            <div className="bg-space-700 rounded-lg p-6 space-y-4 animate-fade-in">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-white">Results for {result.eo_satellite}</h3>
                  <p className="text-xs text-gray-400">
                    Elements: {result.eo_tle_source === 'celestrak' ? 'live from CelesTrak' : result.eo_tle_source} · FOV{' '}
                    {result.fov_degrees}° · sampled every {result.sample_seconds} s
                  </p>
                </div>
                <button
                  onClick={() => handleExportCSV(result)}
                  className="flex items-center space-x-2 text-accent-cyan hover:text-cyan-400 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  <span className="text-sm">Export CSV</span>
                </button>
              </div>

              <div className="grid grid-cols-4 gap-4">
                <Stat label="Total Passes" value={result.total_passes} color="text-white" />
                <Stat label="Clean Passes" value={result.clean_passes} color="text-accent-green" />
                <Stat label="Interfered" value={result.interfered_passes} color="text-accent-red" />
                <Stat label="Interference" value={`${result.interference_percentage}%`} color="text-accent-yellow" />
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-300 mb-2">Clean Imaging Windows ({result.clean_windows.length})</h4>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {result.clean_windows.map((window, idx) => (
                    <div key={idx} className="bg-space-800 rounded p-3 flex items-center justify-between">
                      <div>
                        <div className="text-sm text-white font-mono">{new Date(window.start).toLocaleString()}</div>
                        <div className="text-xs text-gray-400">
                          Duration: {window.duration_minutes} minutes
                          {window.max_elevation != null && ` · max elevation ${window.max_elevation.toFixed(0)}°`}
                        </div>
                      </div>
                      <div className="px-3 py-1 bg-accent-green text-white rounded text-xs font-medium">CLEAN</div>
                    </div>
                  ))}
                </div>
              </div>

              {result.interference_events.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-gray-300 mb-2">
                    Interference Events ({result.interference_events.length})
                  </h4>
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {result.interference_events.map((event, idx) => (
                      <div key={idx} className="bg-space-800 rounded p-3">
                        <div className="flex items-center justify-between mb-2">
                          <div className="text-sm text-white font-mono">{new Date(event.start).toLocaleString()}</div>
                          <div className="px-3 py-1 bg-accent-red text-white rounded text-xs font-medium">
                            {event.severity} IN VIEW
                          </div>
                        </div>
                        <div className="text-xs text-gray-400 space-y-0.5">
                          {event.interfering_satellites.slice(0, 5).map((s) => (
                            <div key={s.norad_id}>
                              {s.name}: {s.min_angle_deg.toFixed(2)}° off nadir at {s.range_km.toFixed(0)} km
                            </div>
                          ))}
                          {event.interfering_satellites.length > 5 && (
                            <div>and {event.interfering_satellites.length - 5} more</div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {analysisMutation.isError && (
            <div className="bg-accent-red bg-opacity-10 border border-accent-red rounded-lg p-4 text-accent-red">
              <p className="font-medium">Analysis Failed</p>
              <p className="text-sm mt-1">
                {analysisMutation.error instanceof Error ? analysisMutation.error.message : 'Unknown error occurred'}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value, color }: { label: string; value: string | number; color: string }) {
  return (
    <div className="bg-space-800 rounded p-3">
      <div className="text-xs text-gray-400">{label}</div>
      <div className={`text-2xl font-bold font-mono ${color}`}>{value}</div>
    </div>
  );
}

export default EOAnalyzer;
