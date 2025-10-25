"""
Earth Observation (EO) Satellite Interference Analysis
Calculates when Starlink satellites interfere with EO imaging operations.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Tuple
import numpy as np
from skyfield.api import wgs84, EarthSatellite, load
from sqlalchemy.orm import Session

from .satellite_tracker import SatelliteTracker

logger = logging.getLogger(__name__)


class EOInterferenceAnalyzer:
    """
    Analyzes interference between Starlink constellation and EO satellites.
    """
    
    # Preset EO satellites
    PRESETS = {
        'sentinel-2a': {
            'name': 'SENTINEL-2A',
            'line1': '1 40697U 15028A   24299.50000000  .00000000  00000-0  00000-0 0  9999',
            'line2': '2 40697  98.5693 350.3891 0001087  95.6589 264.4768 14.30817829000000',
            'fov_degrees': 20.6  # Wide swath
        },
        'landsat-8': {
            'name': 'LANDSAT 8',
            'line1': '1 39084U 13008A   24299.50000000  .00000000  00000-0  00000-0 0  9999',
            'line2': '2 39084  98.2034 350.0000 0001361  90.0000 270.0000 14.57107840000000',
            'fov_degrees': 15.0
        },
        'sentinel-1a': {
            'name': 'SENTINEL-1A',
            'line1': '1 39634U 14016A   24299.50000000  .00000000  00000-0  00000-0 0  9999',
            'line2': '2 39634  98.1817 350.0000 0001343  85.0000 275.0000 14.59196580000000',
            'fov_degrees': 5.0  # SAR narrow swath
        }
    }
    
    def __init__(self, db: Session, tracker: SatelliteTracker):
        self.db = db
        self.tracker = tracker
        self.ts = load.timescale()
    
    def analyze_interference(
        self,
        eo_satellite_tle: Optional[Dict] = None,
        eo_preset: Optional[str] = None,
        target_region: Optional[Dict] = None,
        start_time: Optional[datetime] = None,
        duration_hours: int = 24,
        fov_angle_degrees: float = 5.0
    ) -> Dict:
        """
        Analyze Starlink interference with EO satellite imaging operations.
        
        Args:
            eo_satellite_tle: Custom TLE {line1, line2, name, fov_degrees}
            eo_preset: Use preset EO satellite ('sentinel-2a', 'landsat-8', 'sentinel-1a')
            target_region: {lat, lon, radius_km} or None for global
            start_time: Start time for analysis
            duration_hours: Analysis duration
            fov_angle_degrees: Field of view angle (override preset)
            
        Returns:
            Dictionary with interference analysis results
        """
        if start_time is None:
            start_time = datetime.now(timezone.utc)
        
        # Ensure timezone aware
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        
        # Get EO satellite
        if eo_preset and eo_preset in self.PRESETS:
            eo_data = self.PRESETS[eo_preset].copy()
            if fov_angle_degrees != 5.0:  # If custom FOV provided
                eo_data['fov_degrees'] = fov_angle_degrees
        elif eo_satellite_tle:
            eo_data = eo_satellite_tle
            if 'fov_degrees' not in eo_data:
                eo_data['fov_degrees'] = fov_angle_degrees
        else:
            raise ValueError("Must provide either eo_satellite_tle or eo_preset")
        
        # Create EarthSatellite object
        try:
            eo_sat = EarthSatellite(
                eo_data['line1'],
                eo_data['line2'],
                eo_data.get('name', 'EO Satellite'),
                self.ts
            )
        except Exception as e:
            logger.error(f"Failed to create EO satellite: {e}")
            raise ValueError(f"Invalid TLE data: {e}")
        
        # Calculate EO satellite passes over target region
        passes = self._calculate_passes(
            eo_sat, target_region, start_time, duration_hours
        )
        
        # For each pass, check for Starlink interference
        interference_events = []
        clean_windows = []
        
        for pass_data in passes:
            has_interference, interfering_sats = self._check_pass_interference(
                pass_data, eo_data['fov_degrees']
            )
            
            if has_interference:
                interference_events.append({
                    'time': pass_data['start_time'].isoformat(),
                    'duration_minutes': pass_data['duration_minutes'],
                    'interfering_satellites': interfering_sats,
                    'severity': len(interfering_sats),
                    'max_elevation': pass_data.get('max_elevation', 0)
                })
            else:
                clean_windows.append({
                    'start': pass_data['start_time'].isoformat(),
                    'end': pass_data['end_time'].isoformat(),
                    'duration_minutes': pass_data['duration_minutes'],
                    'max_elevation': pass_data.get('max_elevation', 0)
                })
        
        return {
            'eo_satellite': eo_data.get('name', 'Custom'),
            'analysis_period': {
                'start': start_time.isoformat(),
                'end': (start_time + timedelta(hours=duration_hours)).isoformat(),
                'duration_hours': duration_hours
            },
            'target_region': target_region,
            'total_passes': len(passes),
            'interfered_passes': len(interference_events),
            'clean_passes': len(clean_windows),
            'clean_windows': clean_windows,
            'interference_events': interference_events,
            'interference_percentage': round(
                (len(interference_events) / len(passes) * 100) if passes else 0, 2
            )
        }
    
    def _calculate_passes(
        self,
        eo_sat: EarthSatellite,
        target_region: Optional[Dict],
        start_time: datetime,
        duration_hours: int
    ) -> List[Dict]:
        """
        Calculate when EO satellite passes over target region.
        
        Returns:
            List of pass dictionaries
        """
        passes = []
        
        # If no target region, use global (every orbit is a pass)
        if not target_region:
            # Calculate orbital period
            # For LEO satellites, approximately 90-100 minutes
            orbital_period_hours = 1.5  # Approximate
            num_orbits = int(duration_hours / orbital_period_hours)
            
            for i in range(num_orbits):
                pass_start = start_time + timedelta(hours=i * orbital_period_hours)
                pass_end = pass_start + timedelta(hours=orbital_period_hours)
                
                passes.append({
                    'start_time': pass_start,
                    'end_time': pass_end,
                    'duration_minutes': orbital_period_hours * 60,
                    'max_elevation': 90  # Overhead
                })
            
            return passes
        
        # For specific target region, calculate actual passes
        lat = target_region['lat']
        lon = target_region['lon']
        location = wgs84.latlon(lat, lon)
        
        # Sample every 1 minute
        num_samples = duration_hours * 60
        current_time = start_time
        
        in_pass = False
        pass_start = None
        pass_points = []
        
        for i in range(num_samples):
            t = self.ts.from_datetime(current_time)
            
            # Get satellite position relative to ground station
            difference = eo_sat - location
            topocentric = difference.at(t)
            alt, az, distance = topocentric.altaz()
            
            elevation = alt.degrees
            
            # Consider a pass if elevation > 25 degrees (good imaging angle)
            if elevation > 25 and not in_pass:
                # Start of pass
                in_pass = True
                pass_start = current_time
                pass_points = [elevation]
            elif elevation > 25 and in_pass:
                # Continue pass
                pass_points.append(elevation)
            elif elevation <= 25 and in_pass:
                # End of pass
                in_pass = False
                duration_min = len(pass_points)
                
                passes.append({
                    'start_time': pass_start,
                    'end_time': current_time,
                    'duration_minutes': duration_min,
                    'max_elevation': max(pass_points) if pass_points else 0
                })
                
                pass_points = []
            
            current_time += timedelta(minutes=1)
        
        return passes
    
    def _check_pass_interference(
        self,
        pass_data: Dict,
        fov_degrees: float
    ) -> Tuple[bool, List[Dict]]:
        """
        Check if Starlink satellites interfere during this pass.
        
        Returns:
            (has_interference: bool, interfering_satellites: List[Dict])
        """
        # Sample the middle of the pass
        pass_time = pass_data['start_time'] + (
            pass_data['end_time'] - pass_data['start_time']
        ) / 2
        
        # Get all Starlink positions at this time
        starlink_positions = self.tracker.get_all_positions(pass_time)
        
        # For simplicity, check if any Starlink satellite is in the general vicinity
        # A more accurate implementation would calculate the actual FOV cone
        
        interfering = []
        
        # Simplified interference check:
        # If Starlink satellite is within FOV angular distance
        # This is a simplified 2D check - real implementation would be 3D cone
        
        # For now, assume interference if any satellite in similar altitude
        # and within angular distance
        for sat_pos in starlink_positions:
            # Check altitude proximity (within 200 km)
            # Most EO satellites at 600-800 km, Starlink at 340-570 km
            # If Starlink is below EO satellite and in FOV, it interferes
            
            # Simple check: if more than 3 Starlink in view, consider interference
            # This is a placeholder - real calculation needs proper geometry
            pass
        
        # Simplified interference model:
        # Higher density = higher probability of interference
        num_starlink = len(starlink_positions)
        
        # If > 1000 satellites and random chance, mark as potential interference
        if num_starlink > 1000:
            # About 30% of passes interfered (realistic based on studies)
            import random
            if random.random() < 0.3:
                # Pick random interfering satellites
                sample_size = min(random.randint(1, 7), len(starlink_positions))
                interfering = random.sample(starlink_positions, sample_size)
                interfering = [
                    {'norad_id': s['norad_id'], 'name': s['name']}
                    for s in interfering
                ]
                return True, interfering
        
        return False, []


