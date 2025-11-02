import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import Globe from './Globe';
import Sidebar from './Sidebar';
import Header from './Header';
import Dashboard from './Dashboard';
import EOAnalyzer from './EOAnalyzer';
import ShareButton from './ShareButton';
import { satelliteApi, createWebSocket } from '../services/api';
import { decodeViewState } from '../utils/share';
import type { SatellitePosition } from '../types';
import { Satellite as SatelliteIcon } from 'lucide-react';

function StarlinkTracker() {
  const [positions, setPositions] = useState<SatellitePosition[]>([]);
  const [selectedSatellite, setSelectedSatellite] = useState<number | null>(null);
  const [showOrbit, setShowOrbit] = useState(false);
  const [dashboardOpen, setDashboardOpen] = useState(false);
  const [eoAnalyzerOpen, setEoAnalyzerOpen] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);

  // Load view state from URL
  useEffect(() => {
    const viewState = decodeViewState(window.location.search);
    if (viewState.selectedSatellite) {
      setSelectedSatellite(viewState.selectedSatellite);
      setShowOrbit(viewState.showOrbit || false);
    }
  }, []);

  // Fetch initial positions
  const { data: initialPositions, isLoading } = useQuery({
    queryKey: ['positions'],
    queryFn: () => satelliteApi.getPositions(),
    staleTime: 30000,
  });

  // Setup WebSocket for real-time updates
  useEffect(() => {
    const ws = createWebSocket(
      (message) => {
        if (message.type === 'positions' && message.data) {
          setPositions(message.data);
          setWsConnected(true);
        }
      },
      (error) => {
        console.error('WebSocket error:', error);
        setWsConnected(false);
      }
    );

    return () => {
      ws.close();
    };
  }, []);

  // Use initial positions until WebSocket provides updates
  useEffect(() => {
    if (initialPositions && positions.length === 0) {
      setPositions(initialPositions);
    }
  }, [initialPositions]);

  const handleSatelliteClick = (noradId: number) => {
    setSelectedSatellite(noradId);
    setShowOrbit(true);
  };

  return (
    <div className="w-screen h-screen flex flex-col bg-space-900">
      {/* Header */}
      <Header 
        satelliteCount={positions.length}
        wsConnected={wsConnected}
        onToggleDashboard={() => setDashboardOpen(!dashboardOpen)}
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          positions={positions}
          selectedSatellite={selectedSatellite}
          onSelectSatellite={handleSatelliteClick}
        />

        {/* Main Globe View */}
        <div className="flex-1 relative">
          {isLoading && positions.length === 0 ? (
            <div className="absolute inset-0 flex items-center justify-center bg-space-900">
              <div className="text-center">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-accent-cyan"></div>
                <p className="mt-4 text-lg">Loading satellites...</p>
              </div>
            </div>
          ) : (
            <Globe
              positions={positions}
              selectedSatellite={selectedSatellite}
              showOrbit={showOrbit}
              onSatelliteClick={handleSatelliteClick}
            />
          )}

          {/* Floating Action Buttons */}
          {positions.length > 0 && (
            <div className="absolute top-4 right-4 flex flex-col space-y-2">
              <ShareButton
                viewState={{
                  selectedSatellite: selectedSatellite || undefined,
                  showOrbit,
                }}
              />
              <button
                onClick={() => setEoAnalyzerOpen(true)}
                className="flex items-center space-x-1.5 bg-white/5 backdrop-blur-sm hover:bg-white/10 text-white px-3 py-1.5 rounded-lg transition-all border border-white/10 text-sm"
              >
                <SatelliteIcon className="w-3.5 h-3.5" />
                <span>EO Analysis</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Bottom Dashboard */}
      {dashboardOpen && (
        <Dashboard
          positions={positions}
          onClose={() => setDashboardOpen(false)}
        />
      )}

      {/* EO Analyzer Modal */}
      {eoAnalyzerOpen && (
        <EOAnalyzer onClose={() => setEoAnalyzerOpen(false)} />
      )}
    </div>
  );
}

export default StarlinkTracker;

