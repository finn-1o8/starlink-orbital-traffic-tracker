/**
 * Sidebar Component
 * Satellite list, filters, and search
 */
import { useState, useMemo } from 'react';
import { Search, MapPin, Layers } from 'lucide-react';
import type { SatellitePosition } from '../types';

interface SidebarProps {
  positions: SatellitePosition[];
  selectedSatellite: number | null;
  onSelectSatellite: (noradId: number) => void;
}

function Sidebar({ positions, selectedSatellite, onSelectSatellite }: SidebarProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [altitudeFilter, setAltitudeFilter] = useState<string>('all');

  // Filter satellites
  const filteredSatellites = useMemo(() => {
    let filtered = positions;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(
        sat =>
          sat.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          sat.norad_id.toString().includes(searchTerm)
      );
    }

    // Altitude filter
    if (altitudeFilter !== 'all') {
      filtered = filtered.filter(sat => {
        if (altitudeFilter === '340-360') return sat.alt_km >= 340 && sat.alt_km <= 360;
        if (altitudeFilter === '500-570') return sat.alt_km >= 500 && sat.alt_km <= 570;
        if (altitudeFilter === '1100-1325') return sat.alt_km >= 1100 && sat.alt_km <= 1325;
        return true;
      });
    }

    return filtered.sort((a, b) => a.name.localeCompare(b.name));
  }, [positions, searchTerm, altitudeFilter]);

  // Altitude band stats
  const altitudeStats = useMemo(() => {
    const stats = {
      '340-360': 0,
      '500-570': 0,
      '1100-1325': 0,
      other: 0,
    };

    positions.forEach(sat => {
      if (sat.alt_km >= 340 && sat.alt_km <= 360) stats['340-360']++;
      else if (sat.alt_km >= 500 && sat.alt_km <= 570) stats['500-570']++;
      else if (sat.alt_km >= 1100 && sat.alt_km <= 1325) stats['1100-1325']++;
      else stats.other++;
    });

    return stats;
  }, [positions]);

  return (
    <div className="w-80 bg-space-800 border-r border-space-700 flex flex-col">
      {/* Search Bar */}
      <div className="p-4 border-b border-space-700">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search satellites..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className="w-full bg-space-700 text-white pl-10 pr-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-cyan"
          />
        </div>
      </div>

      {/* Altitude Filter */}
      <div className="p-4 border-b border-space-700">
        <div className="flex items-center space-x-2 mb-3">
          <Layers className="w-4 h-4 text-accent-cyan" />
          <span className="text-sm font-medium text-gray-300">Altitude Bands</span>
        </div>
        <div className="space-y-2">
          <button
            onClick={() => setAltitudeFilter('all')}
            className={`w-full text-left px-3 py-2 rounded text-sm ${
              altitudeFilter === 'all'
                ? 'bg-accent-cyan text-space-900 font-medium'
                : 'bg-space-700 text-gray-300 hover:bg-space-600'
            }`}
          >
            All ({positions.length})
          </button>
          <button
            onClick={() => setAltitudeFilter('340-360')}
            className={`w-full text-left px-3 py-2 rounded text-sm ${
              altitudeFilter === '340-360'
                ? 'bg-red-500 text-white font-medium'
                : 'bg-space-700 text-gray-300 hover:bg-space-600'
            }`}
          >
            340-360 km ({altitudeStats['340-360']})
          </button>
          <button
            onClick={() => setAltitudeFilter('500-570')}
            className={`w-full text-left px-3 py-2 rounded text-sm ${
              altitudeFilter === '500-570'
                ? 'bg-cyan-500 text-white font-medium'
                : 'bg-space-700 text-gray-300 hover:bg-space-600'
            }`}
          >
            500-570 km ({altitudeStats['500-570']})
          </button>
          <button
            onClick={() => setAltitudeFilter('1100-1325')}
            className={`w-full text-left px-3 py-2 rounded text-sm ${
              altitudeFilter === '1100-1325'
                ? 'bg-yellow-500 text-space-900 font-medium'
                : 'bg-space-700 text-gray-300 hover:bg-space-600'
            }`}
          >
            1100-1325 km ({altitudeStats['1100-1325']})
          </button>
        </div>
      </div>

      {/* Satellite List */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-2">
          <div className="text-xs text-gray-400 px-2 py-1">
            {filteredSatellites.length} satellites
          </div>
          {filteredSatellites.map(sat => (
            <button
              key={sat.norad_id}
              onClick={() => onSelectSatellite(sat.norad_id)}
              className={`w-full text-left px-3 py-2 rounded mb-1 transition-colors ${
                selectedSatellite === sat.norad_id
                  ? 'bg-accent-cyan text-space-900'
                  : 'hover:bg-space-700 text-gray-300'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">{sat.name}</div>
                  <div className="text-xs opacity-75 font-mono">
                    NORAD {sat.norad_id}
                  </div>
                </div>
                <div className="ml-2 text-right">
                  <div className="text-xs font-mono">{sat.alt_km.toFixed(0)} km</div>
                  <div className="text-xs opacity-75">{sat.velocity_km_s.toFixed(1)} km/s</div>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Sidebar;


