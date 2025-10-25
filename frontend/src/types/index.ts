/**
 * Type definitions for Orbital Traffic Analyzer
 */

export interface Satellite {
  norad_id: number;
  name: string;
  constellation: string;
  last_updated: string;
}

export interface SatellitePosition {
  satellite_id: number;
  norad_id: number;
  name: string;
  lat: number;
  lon: number;
  alt_km: number;
  velocity_km_s: number;
  timestamp: string;
}

export interface OrbitPoint {
  lat: number;
  lon: number;
  alt_km: number;
  timestamp: string;
}

export interface OrbitPath {
  norad_id: number;
  name: string;
  orbit_points: OrbitPoint[];
  duration_minutes: number;
}

export interface CongestionMetrics {
  total_satellites: number;
  density_per_1000km3: number;
  mean_spacing_km: number;
  closest_approach_km: number;
  region?: {
    lat: number;
    lon: number;
    radius_km: number;
  };
  altitude_band?: {
    min_km: number;
    max_km: number;
  };
  timestamp: string;
}

export interface AltitudeDistribution {
  altitude_bands: {
    '340-360': number;
    '500-570': number;
    '1100-1325': number;
    'other': number;
  };
  total: number;
  timestamp: string;
}

export interface EOAnalysisRequest {
  eo_satellite_tle?: {
    line1: string;
    line2: string;
    name: string;
    fov_degrees?: number;
  };
  eo_preset?: string;
  target_region?: {
    lat: number;
    lon: number;
    radius_km: number;
  };
  start_time?: string;
  duration_hours?: number;
  fov_angle_degrees?: number;
}

export interface CleanWindow {
  start: string;
  end: string;
  duration_minutes: number;
  max_elevation?: number;
}

export interface InterferenceEvent {
  time: string;
  duration_minutes: number;
  interfering_satellites: Array<{
    norad_id: number;
    name: string;
  }>;
  severity: number;
  max_elevation?: number;
}

export interface EOAnalysisResult {
  eo_satellite: string;
  analysis_period: {
    start: string;
    end: string;
    duration_hours: number;
  };
  target_region?: {
    lat: number;
    lon: number;
    radius_km: number;
  };
  total_passes: number;
  interfered_passes: number;
  clean_passes: number;
  clean_windows: CleanWindow[];
  interference_events: InterferenceEvent[];
  interference_percentage: number;
}

export interface WebSocketMessage {
  type: 'positions' | 'update' | 'error';
  data?: SatellitePosition[];
  timestamp?: string;
  message?: string;
}


