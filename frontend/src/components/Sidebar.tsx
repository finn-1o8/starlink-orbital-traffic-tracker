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
    <div className="w-64 backdrop-blur-xl bg-black/20 border-r border-white/10 flex flex-col shadow-2xl">
      {/* Search Bar */}
      <div className="p-3 border-b border-white/10">
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 transform -translate-y-1/2 w-3.5 h-3.5 text-cyan-400/70" />
          <input
            type="text"
            placeholder="Search satellites..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className="w-full bg-white/5 backdrop-blur-sm text-white text-sm pl-8 pr-3 py-1.5 rounded-lg border border-white/10 focus:outline-none focus:ring-1 focus:ring-cyan-400/50 focus:border-cyan-400/50 placeholder-gray-400"
          />
        </div>
      </div>

      {/* Altitude Filter */}
      <div className="p-3 border-b border-white/10">
        <div className="flex items-center space-x-1.5 mb-2">
          <Layers className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-xs font-medium text-gray-200">Altitude Bands</span>
        </div>
        <div className="space-y-1.5">
          <button
            onClick={() => setAltitudeFilter('all')}
            className={`w-full text-left px-2.5 py-1.5 rounded-md text-xs transition-all ${
              altitudeFilter === 'all'
                ? 'bg-cyan-400/20 text-cyan-300 font-medium border border-cyan-400/30 backdrop-blur-sm'
                : 'bg-white/5 text-gray-300 hover:bg-white/10 border border-white/5'
            }`}
          >
            All ({positions.length})
          </button>
          <button
            onClick={() => setAltitudeFilter('340-360')}
            className={`w-full text-left px-2.5 py-1.5 rounded-md text-xs transition-all ${
              altitudeFilter === '340-360'
                ? 'bg-red-500/20 text-red-300 font-medium border border-red-400/30 backdrop-blur-sm'
                : 'bg-white/5 text-gray-300 hover:bg-white/10 border border-white/5'
            }`}
          >
            340-360 km ({altitudeStats['340-360']})
          </button>
          <button
            onClick={() => setAltitudeFilter('500-570')}
            className={`w-full text-left px-2.5 py-1.5 rounded-md text-xs transition-all ${
              altitudeFilter === '500-570'
                ? 'bg-cyan-500/20 text-cyan-300 font-medium border border-cyan-400/30 backdrop-blur-sm'
                : 'bg-white/5 text-gray-300 hover:bg-white/10 border border-white/5'
            }`}
          >
            500-570 km ({altitudeStats['500-570']})
          </button>
          <button
            onClick={() => setAltitudeFilter('1100-1325')}
            className={`w-full text-left px-2.5 py-1.5 rounded-md text-xs transition-all ${
              altitudeFilter === '1100-1325'
                ? 'bg-yellow-500/20 text-yellow-300 font-medium border border-yellow-400/30 backdrop-blur-sm'
                : 'bg-white/5 text-gray-300 hover:bg-white/10 border border-white/5'
            }`}
          >
            1100-1325 km ({altitudeStats['1100-1325']})
          </button>
        </div>
      </div>

      {/* Satellite List */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-2">
          <div className="text-[10px] text-gray-400 px-2 py-1 font-medium">
            {filteredSatellites.length} satellites
          </div>
          {filteredSatellites.map(sat => (
            <button
              key={sat.norad_id}
              onClick={() => onSelectSatellite(sat.norad_id)}
              className={`w-full text-left px-2.5 py-1.5 rounded-md mb-1 transition-all ${
                selectedSatellite === sat.norad_id
                  ? 'bg-cyan-400/20 text-cyan-300 border border-cyan-400/30 backdrop-blur-sm'
                  : 'hover:bg-white/10 text-gray-300 border border-transparent'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-medium truncate">{sat.name}</div>
                  <div className="text-[10px] opacity-75 font-mono">
                    NORAD {sat.norad_id}
                  </div>
                </div>
                <div className="ml-2 text-right">
                  <div className="text-[10px] font-mono">{sat.alt_km.toFixed(0)} km</div>
                  <div className="text-[10px] opacity-75">{sat.velocity_km_s.toFixed(1)} km/s</div>
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


