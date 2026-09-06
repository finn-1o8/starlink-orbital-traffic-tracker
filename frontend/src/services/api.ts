/**
 * API Service for backend communication
 */
import axios from 'axios';
import type {
  Satellite,
  SatellitePosition,
  OrbitPath,
  CongestionMetrics,
  CongestionRequest,
  AltitudeDistribution,
  EOAnalysisRequest,
  EOAnalysisResult,
  EOPresets,
  HistoricalSnapshot,
  WebSocketMessage,
} from '../types';

// In production the API is served under the same origin at /api; in development it is a
// separate process on port 8000. Both can be overridden through VITE_API_URL.
const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '/api' : 'http://localhost:8000/api');

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
});

if (import.meta.env.DEV) {
  api.interceptors.request.use((config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  });
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      console.error('[API] Response error:', error.response?.data || error.message);
      return Promise.reject(error);
    }
  );
}

/**
 * Satellite Endpoints
 */
export const satelliteApi = {
  getAll: async (constellation?: string): Promise<Satellite[]> => {
    const params = constellation ? { constellation } : {};
    const response = await api.get<Satellite[]>('/satellites', { params });
    return response.data;
  },

  getPositions: async (time?: string): Promise<SatellitePosition[]> => {
    const params = time ? { time } : {};
    const response = await api.get<SatellitePosition[]>('/satellites/positions', { params });
    return response.data;
  },

  getOrbit: async (noradId: number, duration: number = 90): Promise<OrbitPath> => {
    const response = await api.get<OrbitPath>(`/satellites/${noradId}/orbit`, { params: { duration } });
    return response.data;
  },

  getInfo: async (noradId: number) => {
    const response = await api.get(`/satellites/${noradId}`);
    return response.data;
  },
};

/**
 * Congestion Analysis Endpoints
 */
export const congestionApi = {
  analyze: async (params: CongestionRequest): Promise<CongestionMetrics> => {
    const response = await api.get<CongestionMetrics>('/congestion', { params });
    return response.data;
  },

  getHeatmap: async (params: { alt_min?: number; alt_max?: number; grid_size?: number }) => {
    const response = await api.get('/congestion/heatmap', { params });
    return response.data;
  },

  getAltitudeDistribution: async (): Promise<AltitudeDistribution> => {
    const response = await api.get<AltitudeDistribution>('/congestion/altitude-distribution');
    return response.data;
  },
};

/**
 * EO Analysis Endpoints
 */
export const eoApi = {
  analyze: async (request: EOAnalysisRequest): Promise<EOAnalysisResult> => {
    const response = await api.post<EOAnalysisResult>('/eo-analysis', request);
    return response.data;
  },

  getPresets: async (): Promise<EOPresets> => {
    const response = await api.get<EOPresets>('/eo-analysis/presets');
    return response.data;
  },
};

/**
 * Historical snapshots
 */
export const historyApi = {
  getSnapshots: async (days: number = 30): Promise<HistoricalSnapshot[]> => {
    const response = await api.get<HistoricalSnapshot[]>('/history/snapshots', { params: { days } });
    return response.data;
  },
};

function defaultWebSocketUrl(): string {
  if (import.meta.env.VITE_WS_URL) return import.meta.env.VITE_WS_URL;
  if (import.meta.env.PROD) {
    const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    return `${scheme}://${window.location.host}/api`;
  }
  return 'ws://localhost:8000/api';
}

/**
 * WebSocket connection for real-time updates with automatic reconnection
 */
export const createWebSocket = (
  onMessage: (data: WebSocketMessage) => void,
  onError?: (error: Event) => void,
  onConnect?: () => void
) => {
  const WS_URL = defaultWebSocketUrl();
  let ws: WebSocket | null = null;
  let reconnectAttempts = 0;
  let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
  let closedByUser = false;
  const maxReconnectAttempts = 5;
  const initialReconnectDelay = 1000;

  const connect = () => {
    try {
      ws = new WebSocket(`${WS_URL}/ws/positions`);

      ws.onopen = () => {
        reconnectAttempts = 0;
        if (onConnect) onConnect();
      };

      ws.onmessage = (event) => {
        try {
          onMessage(JSON.parse(event.data) as WebSocketMessage);
        } catch (error) {
          if (import.meta.env.DEV) console.error('[WebSocket] Failed to parse message:', error);
        }
      };

      ws.onerror = (error) => {
        if (onError) onError(error);
      };

      ws.onclose = (event) => {
        if (closedByUser || event.wasClean) return;
        if (reconnectAttempts < maxReconnectAttempts) {
          const delay = initialReconnectDelay * Math.pow(2, reconnectAttempts);
          reconnectAttempts++;
          reconnectTimeout = setTimeout(connect, delay);
        } else if (import.meta.env.DEV) {
          console.error('[WebSocket] Max reconnection attempts reached. Please refresh the page.');
        }
      };
    } catch (error) {
      if (import.meta.env.DEV) console.error('[WebSocket] Failed to create connection:', error);
      if (onError) onError(error as Event);
    }
  };

  connect();

  return {
    close: () => {
      closedByUser = true;
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
        reconnectTimeout = null;
      }
      if (ws) {
        ws.close();
        ws = null;
      }
    },
    get readyState() {
      return ws?.readyState ?? WebSocket.CLOSED;
    },
  };
};

export default api;
