/**
 * Type definitions for Orbital Traffic Analyzer
 */

export interface Satellite {
  norad_id: number;
  name: string;
  constellation: string;
  last_updated: string | null;
}

export interface SatellitePosition {
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

export interface CongestionRequest {
  lat: number;
  lon: number;
  radius_km?: number;
  alt_min?: number;
  alt_max?: number;
  time?: string;
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
    other: number;
  };
  total: number;
  timestamp: string;
}

export interface EOPreset {
  name: string;
  norad_id: number;
  fov_degrees: number;
  note: string;
}

export interface EOPresets {
  presets: Record<string, EOPreset>;
  count: number;
}

export interface EOAnalysisRequest {
  eo_satellite_tle?: {
    line1: string;
    line2: string;
    name?: string;
    norad_id?: number;
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
  sample_seconds?: number;
}

export interface PassWindow {
  start: string;
  end: string;
  duration_minutes: number;
  max_elevation?: number | null;
}

export interface InterferingSatellite {
  norad_id: number;
  name: string;
  min_angle_deg: number;
  range_km: number;
  at: string;
}

export interface InterferenceEvent extends PassWindow {
  time: string;
  interfering_satellites: InterferingSatellite[];
  severity: number;
}

export interface EOAnalysisResult {
  eo_satellite: string;
  eo_tle_source: 'celestrak' | 'fallback' | 'custom';
  fov_degrees: number;
  model: string;
  sample_seconds: number;
  analysis_period: {
    start: string;
    end: string;
    duration_hours: number;
  };
  target_region?: {
    lat: number;
    lon: number;
    radius_km: number;
  } | null;
  total_passes: number;
  interfered_passes: number;
  clean_passes: number;
  clean_windows: PassWindow[];
  interference_events: InterferenceEvent[];
  interference_percentage: number;
}

export interface HistoricalSnapshot {
  snapshot_date: string;
  total_satellites: number;
  altitude_band_340_360: number;
  altitude_band_500_570: number;
  altitude_band_1100_1325: number;
}

export interface WebSocketMessage {
  type: 'positions' | 'update' | 'error';
  data?: SatellitePosition[];
  timestamp?: string;
  message?: string;
}
