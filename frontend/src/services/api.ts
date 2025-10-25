/**
 * API Service for backend communication
 */
import axios from 'axios';
import type {
  Satellite,
  SatellitePosition,
  OrbitPath,
  CongestionMetrics,
  AltitudeDistribution,
  EOAnalysisRequest,
  EOAnalysisResult,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`[API] Response from ${response.config.url}:`, response.status);
    return response;
  },
  (error) => {
    console.error('[API] Response error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/**
 * Satellite Endpoints
 */
export const satelliteApi = {
  /**
   * Get all satellites
   */
  getAll: async (constellation?: string): Promise<Satellite[]> => {
    const params = constellation ? { constellation } : {};
    const response = await api.get<Satellite[]>('/satellites', { params });
    return response.data;
  },

  /**
   * Get satellite positions
   */
  getPositions: async (time?: string): Promise<SatellitePosition[]> => {
    const params = time ? { time } : {};
    const response = await api.get<SatellitePosition[]>('/satellites/positions', { params });
    return response.data;
  },

  /**
   * Get satellite orbit path
   */
  getOrbit: async (noradId: number, duration: number = 90): Promise<OrbitPath> => {
    const response = await api.get<OrbitPath>(`/satellites/${noradId}/orbit`, {
      params: { duration },
    });
    return response.data;
  },

  /**
   * Get satellite info
   */
  getInfo: async (noradId: number) => {
    const response = await api.get(`/satellites/${noradId}`);
    return response.data;
  },
};

/**
 * Congestion Analysis Endpoints
 */
export const congestionApi = {
  /**
   * Analyze congestion for a region
   */
  analyze: async (params: {
    lat: number;
    lon: number;
    radius_km?: number;
    alt_min?: number;
    alt_max?: number;
    time?: string;
  }): Promise<CongestionMetrics> => {
    const response = await api.get<CongestionMetrics>('/congestion', { params });
    return response.data;
  },

  /**
   * Get density heatmap
   */
  getHeatmap: async (params: {
    alt_min?: number;
    alt_max?: number;
    grid_size?: number;
  }) => {
    const response = await api.get('/congestion/heatmap', { params });
    return response.data;
  },

  /**
   * Get altitude distribution
   */
  getAltitudeDistribution: async (): Promise<AltitudeDistribution> => {
    const response = await api.get<AltitudeDistribution>('/congestion/altitude-distribution');
    return response.data;
  },
};

/**
 * EO Analysis Endpoints
 */
export const eoApi = {
  /**
   * Analyze EO interference
   */
  analyze: async (request: EOAnalysisRequest): Promise<EOAnalysisResult> => {
    const response = await api.post<EOAnalysisResult>('/eo-analysis', request);
    return response.data;
  },

  /**
   * Get available EO presets
   */
  getPresets: async () => {
    const response = await api.get('/eo-analysis/presets');
    return response.data;
  },
};

/**
 * WebSocket connection for real-time updates
 */
export const createWebSocket = (onMessage: (data: any) => void, onError?: (error: Event) => void) => {
  const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api';
  const ws = new WebSocket(`${WS_URL}/ws/positions`);

  ws.onopen = () => {
    console.log('[WebSocket] Connected');
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (error) {
      console.error('[WebSocket] Failed to parse message:', error);
    }
  };

  ws.onerror = (error) => {
    console.error('[WebSocket] Error:', error);
    if (onError) onError(error);
  };

  ws.onclose = () => {
    console.log('[WebSocket] Disconnected');
  };

  return ws;
};

export default api;


