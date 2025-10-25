/**
 * Header Component
 * Top navigation bar with logo, stats, and controls
 */
import { Satellite, Activity, BarChart3 } from 'lucide-react';

interface HeaderProps {
  satelliteCount: number;
  wsConnected: boolean;
  onToggleDashboard: () => void;
}

function Header({ satelliteCount, wsConnected, onToggleDashboard }: HeaderProps) {
  return (
    <header className="bg-space-800 border-b border-space-700 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Logo and Title */}
        <div className="flex items-center space-x-3">
          <Satellite className="w-8 h-8 text-accent-cyan" />
          <div>
            <h1 className="text-xl font-semibold text-white">
              Orbital Traffic Impact Analyzer
            </h1>
            <p className="text-sm text-gray-400">
              Real-time Starlink Constellation Tracking
            </p>
          </div>
        </div>

        {/* Stats and Controls */}
        <div className="flex items-center space-x-6">
          {/* Satellite Count */}
          <div className="flex items-center space-x-2 bg-space-700 px-4 py-2 rounded-lg">
            <Activity className="w-5 h-5 text-accent-cyan" />
            <div>
              <div className="text-xs text-gray-400">Tracking</div>
              <div className="text-lg font-semibold text-white font-mono">
                {satelliteCount.toLocaleString()}
              </div>
            </div>
          </div>

          {/* Connection Status */}
          <div className="flex items-center space-x-2 bg-space-700 px-4 py-2 rounded-lg">
            <div
              className={`w-2 h-2 rounded-full ${
                wsConnected ? 'bg-accent-green animate-pulse' : 'bg-accent-red'
              }`}
            />
            <div>
              <div className="text-xs text-gray-400">Status</div>
              <div className="text-sm font-medium text-white">
                {wsConnected ? 'Live' : 'Offline'}
              </div>
            </div>
          </div>

          {/* Dashboard Toggle */}
          <button
            onClick={onToggleDashboard}
            className="flex items-center space-x-2 bg-accent-cyan text-space-900 px-4 py-2 rounded-lg hover:bg-cyan-400 transition-colors font-medium"
          >
            <BarChart3 className="w-5 h-5" />
            <span>Analytics</span>
          </button>
        </div>
      </div>
    </header>
  );
}

export default Header;


