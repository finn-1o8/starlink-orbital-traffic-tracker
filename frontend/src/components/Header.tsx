/**
 * Header Component
 * Top navigation bar with logo, stats, and controls
 */
import { Satellite, Activity, BarChart3, ArrowLeft } from 'lucide-react';

interface HeaderProps {
  satelliteCount: number;
  wsConnected: boolean;
  onToggleDashboard: () => void;
}

// Optional link back to a landing page when the tracker is embedded in a larger site.
const landingUrl = import.meta.env.VITE_LANDING_URL;

function Header({ satelliteCount, wsConnected, onToggleDashboard }: HeaderProps) {
  return (
    <header className="backdrop-blur-xl bg-black/20 border-b border-white/10 px-5 py-3 shadow-xl">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          {landingUrl && (
            <a
              href={landingUrl}
              className="flex items-center space-x-2 backdrop-blur-xl bg-black/20 hover:bg-black/30 text-gray-300 hover:text-cyan-400 px-4 py-2 rounded-lg border border-white/10 transition-all"
            >
              <ArrowLeft className="w-4 h-4" />
              <span className="text-sm">Back</span>
            </a>
          )}

          <div className="flex items-center space-x-2.5">
            <Satellite className="w-6 h-6 text-cyan-400" />
            <div>
              <h1 className="text-base font-semibold text-white">Orbital Traffic Impact Analyzer</h1>
              <p className="text-[10px] text-gray-400">Real-time Starlink Constellation Tracking</p>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-white/5 backdrop-blur-sm px-3 py-1.5 rounded-lg border border-white/10">
            <Activity className="w-4 h-4 text-cyan-400" />
            <div>
              <div className="text-[9px] text-gray-400 uppercase tracking-wide">Tracking</div>
              <div className="text-sm font-semibold text-white font-mono">{satelliteCount.toLocaleString()}</div>
            </div>
          </div>

          <div className="flex items-center space-x-2 bg-white/5 backdrop-blur-sm px-3 py-1.5 rounded-lg border border-white/10">
            <div className={`w-1.5 h-1.5 rounded-full ${wsConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
            <div>
              <div className="text-[9px] text-gray-400 uppercase tracking-wide">Status</div>
              <div className="text-xs font-medium text-white">{wsConnected ? 'Live' : 'Offline'}</div>
            </div>
          </div>

          <button
            onClick={onToggleDashboard}
            className="flex items-center space-x-1.5 bg-cyan-400/20 text-cyan-300 px-3 py-1.5 rounded-lg hover:bg-cyan-400/30 transition-all font-medium border border-cyan-400/30 backdrop-blur-sm text-sm"
          >
            <BarChart3 className="w-4 h-4" />
            <span>Analytics</span>
          </button>
        </div>
      </div>
    </header>
  );
}

export default Header;
