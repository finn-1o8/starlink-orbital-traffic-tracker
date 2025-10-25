"""
Orbital Congestion Analysis Service
Calculates satellite density, spacing, and congestion metrics.
"""
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple
import numpy as np
from sqlalchemy.orm import Session

from ..models.satellite import Satellite
from .satellite_tracker import SatelliteTracker

logger = logging.getLogger(__name__)


class CongestionAnalyzer:
    """
    Analyzes orbital congestion for specified regions and altitude bands.
    """
    
    def __init__(self, db: Session, tracker: SatelliteTracker):
        self.db = db
        self.tracker = tracker
    
    def analyze_region(
        self,
        lat: float,
        lon: float,
        radius_km: float,
        alt_min: float,
        alt_max: float,
        time: Optional[datetime] = None
    ) -> Dict:
        """
        Analyze orbital congestion for a specific region and altitude band.
        
        Args:
            lat: Latitude of region center
            lon: Longitude of region center
            radius_km: Radius of region in km
            alt_min: Minimum altitude in km
            alt_max: Maximum altitude in km
            time: Time for analysis (default: now)
            
        Returns:
            Dictionary with congestion metrics
        """
        if time is None:
            time = datetime.now(timezone.utc)
        
        # Get all satellite positions at this time
        positions = self.tracker.get_all_positions(time)
        
        # Filter by altitude band
        filtered_positions = [
            pos for pos in positions
            if alt_min <= pos['alt_km'] <= alt_max
        ]
        
        # Filter by region
        region_positions = []
        for pos in filtered_positions:
            distance = self._haversine_distance(
                lat, lon, 
                pos['lat'], pos['lon']
            )
            if distance <= radius_km:
                region_positions.append(pos)
        
        total_satellites = len(region_positions)
        
        if total_satellites == 0:
            return {
                'total_satellites': 0,
                'density_per_1000km3': 0.0,
                'mean_spacing_km': 0.0,
                'closest_approach_km': 0.0,
                'timestamp': time.isoformat()
            }
        
        # Calculate volume (cylinder approximation)
        altitude_thickness = alt_max - alt_min
        avg_altitude = (alt_min + alt_max) / 2
        earth_radius = 6371  # km
        
        # Volume of cylindrical shell
        volume_km3 = np.pi * radius_km**2 * altitude_thickness
        
        # Density
        density = (total_satellites / volume_km3) * 1000  # per 1000 km³
        
        # Mean spacing (simplified - assume uniform distribution)
        if total_satellites > 1:
            mean_spacing = (volume_km3 / total_satellites) ** (1/3)
        else:
            mean_spacing = 0.0
        
        # Closest approach
        closest_approach = self._calculate_closest_approach(region_positions)
        
        return {
            'total_satellites': total_satellites,
            'density_per_1000km3': round(density, 4),
            'mean_spacing_km': round(mean_spacing, 2),
            'closest_approach_km': round(closest_approach, 2),
            'region': {'lat': lat, 'lon': lon, 'radius_km': radius_km},
            'altitude_band': {'min_km': alt_min, 'max_km': alt_max},
            'timestamp': time.isoformat()
        }
    
    def get_global_density_map(
        self,
        alt_min: float,
        alt_max: float,
        grid_size: int = 5,
        time: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Calculate satellite density across a global grid.
        
        Args:
            alt_min: Minimum altitude in km
            alt_max: Maximum altitude in km
            grid_size: Grid cell size in degrees (default: 5°)
            time: Time for analysis
            
        Returns:
            List of grid cells with density values
        """
        if time is None:
            time = datetime.now(timezone.utc)
        
        positions = self.tracker.get_all_positions(time)
        
        # Filter by altitude
        filtered_positions = [
            pos for pos in positions
            if alt_min <= pos['alt_km'] <= alt_max
        ]
        
        # Create grid
        lat_bins = np.arange(-90, 90 + grid_size, grid_size)
        lon_bins = np.arange(-180, 180 + grid_size, grid_size)
        
        grid_cells = []
        
        for lat in lat_bins[:-1]:
            for lon in lon_bins[:-1]:
                # Count satellites in this cell
                count = sum(
                    1 for pos in filtered_positions
                    if lat <= pos['lat'] < lat + grid_size
                    and lon <= pos['lon'] < lon + grid_size
                )
                
                if count > 0:
                    grid_cells.append({
                        'lat': lat + grid_size / 2,
                        'lon': lon + grid_size / 2,
                        'count': count
                    })
        
        return grid_cells
    
    def get_altitude_distribution(self) -> Dict:
        """
        Get distribution of satellites across altitude bands.
        
        Returns:
            Dictionary with counts per altitude band
        """
        positions = self.tracker.get_all_positions()
        
        bands = {
            '340-360': 0,
            '500-570': 0,
            '1100-1325': 0,
            'other': 0
        }
        
        for pos in positions:
            alt = pos['alt_km']
            if 340 <= alt <= 360:
                bands['340-360'] += 1
            elif 500 <= alt <= 570:
                bands['500-570'] += 1
            elif 1100 <= alt <= 1325:
                bands['1100-1325'] += 1
            else:
                bands['other'] += 1
        
        return {
            'altitude_bands': bands,
            'total': len(positions),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def _haversine_distance(
        self, 
        lat1: float, lon1: float, 
        lat2: float, lon2: float
    ) -> float:
        """
        Calculate great circle distance between two points on Earth.
        
        Returns:
            Distance in kilometers
        """
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        # Earth radius
        r = 6371  # km
        
        return r * c
    
    def _calculate_closest_approach(self, positions: List[Dict]) -> float:
        """
        Calculate the closest distance between any two satellites.
        
        Args:
            positions: List of satellite positions
            
        Returns:
            Closest distance in km
        """
        if len(positions) < 2:
            return 0.0
        
        min_distance = float('inf')
        
        # Simple O(n²) approach - could optimize with spatial indexing
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i+1:]:
                # 3D Euclidean distance (approximation)
                # Convert to Cartesian coordinates
                r = 6371 + (pos1['alt_km'] + pos2['alt_km']) / 2  # avg radius
                
                distance = self._haversine_distance(
                    pos1['lat'], pos1['lon'],
                    pos2['lat'], pos2['lon']
                )
                
                # Add altitude difference
                alt_diff = abs(pos1['alt_km'] - pos2['alt_km'])
                distance_3d = np.sqrt(distance**2 + alt_diff**2)
                
                min_distance = min(min_distance, distance_3d)
        
        return min_distance if min_distance != float('inf') else 0.0


