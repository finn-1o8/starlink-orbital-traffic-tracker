"""
Satellite Position Calculation Engine
Uses Skyfield library for SGP4 propagation of satellite positions.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Tuple
from skyfield.api import load, EarthSatellite, wgs84
from sqlalchemy.orm import Session
import numpy as np

from ..models.satellite import Satellite, SatellitePosition

logger = logging.getLogger(__name__)


class SatelliteTracker:
    """
    Calculates satellite positions using SGP4 propagation via Skyfield.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.ts = load.timescale()
        self._satellite_cache = {}  # Cache EarthSatellite objects
        self._cache_timestamp = None
    
    def _get_earth_satellite(self, sat: Satellite) -> Optional[EarthSatellite]:
        """
        Create Skyfield EarthSatellite object from TLE.
        
        Args:
            sat: Satellite model with TLE data
            
        Returns:
            EarthSatellite object or None on error
        """
        try:
            # Check cache first
            cache_key = f"{sat.norad_id}_{sat.last_updated}"
            if cache_key in self._satellite_cache:
                return self._satellite_cache[cache_key]
            
            earth_sat = EarthSatellite(
                sat.tle_line1,
                sat.tle_line2,
                sat.name,
                self.ts
            )
            
            # Cache it
            self._satellite_cache[cache_key] = earth_sat
            return earth_sat
            
        except Exception as e:
            logger.error(f"Failed to create EarthSatellite for {sat.norad_id}: {e}")
            return None
    
    def propagate_position(
        self, 
        satellite_id: int, 
        time: Optional[datetime] = None
    ) -> Optional[Dict]:
        """
        Calculate satellite position at specific time.
        
        Args:
            satellite_id: Database ID of satellite
            time: Time to calculate position (default: now)
            
        Returns:
            Dictionary with {lat, lon, alt_km, velocity_km_s, timestamp}
        """
        if time is None:
            time = datetime.now(timezone.utc)
        
        # Ensure timezone aware
        if time.tzinfo is None:
            time = time.replace(tzinfo=timezone.utc)
        
        # Get satellite from database
        sat = self.db.query(Satellite).filter(Satellite.id == satellite_id).first()
        if not sat:
            logger.error(f"Satellite {satellite_id} not found in database")
            return None
        
        earth_sat = self._get_earth_satellite(sat)
        if not earth_sat:
            return None
        
        try:
            # Convert time to Skyfield time
            t = self.ts.from_datetime(time)
            
            # Calculate position
            geocentric = earth_sat.at(t)
            subpoint = wgs84.subpoint(geocentric)
            
            # Get velocity
            velocity_m_s = geocentric.velocity.km_per_s
            velocity_magnitude = np.sqrt(
                velocity_m_s[0]**2 + velocity_m_s[1]**2 + velocity_m_s[2]**2
            )
            
            return {
                'satellite_id': satellite_id,
                'norad_id': sat.norad_id,
                'name': sat.name,
                'lat': subpoint.latitude.degrees,
                'lon': subpoint.longitude.degrees,
                'alt_km': subpoint.elevation.km,
                'velocity_km_s': float(velocity_magnitude),
                'timestamp': time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to propagate position for satellite {satellite_id}: {e}")
            return None
    
    def get_all_positions(self, time: Optional[datetime] = None) -> List[Dict]:
        """
        Get positions for all satellites at given time.
        
        Args:
            time: Time to calculate positions (default: now)
            
        Returns:
            List of position dictionaries
        """
        if time is None:
            time = datetime.now(timezone.utc)
        
        # Ensure timezone aware
        if time.tzinfo is None:
            time = time.replace(tzinfo=timezone.utc)
        
        # Get all satellites
        satellites = self.db.query(Satellite).all()
        logger.info(f"Calculating positions for {len(satellites)} satellites at {time}")
        
        positions = []
        
        # Convert time once
        t = self.ts.from_datetime(time)
        
        for sat in satellites:
            try:
                earth_sat = self._get_earth_satellite(sat)
                if not earth_sat:
                    continue
                
                # Calculate position
                geocentric = earth_sat.at(t)
                subpoint = wgs84.subpoint(geocentric)
                
                # Get velocity
                velocity_m_s = geocentric.velocity.km_per_s
                velocity_magnitude = np.sqrt(
                    velocity_m_s[0]**2 + velocity_m_s[1]**2 + velocity_m_s[2]**2
                )
                
                # Validate position
                lat = subpoint.latitude.degrees
                lon = subpoint.longitude.degrees
                alt_km = subpoint.elevation.km
                
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180) or not (100 <= alt_km <= 2000):
                    logger.warning(f"Invalid position for {sat.norad_id}: lat={lat}, lon={lon}, alt={alt_km}")
                    continue
                
                positions.append({
                    'satellite_id': sat.id,
                    'norad_id': sat.norad_id,
                    'name': sat.name,
                    'lat': float(lat),
                    'lon': float(lon),
                    'alt_km': float(alt_km),
                    'velocity_km_s': float(velocity_magnitude),
                    'timestamp': time.isoformat()
                })
                
            except Exception as e:
                logger.error(f"Failed to calculate position for {sat.norad_id}: {e}")
                continue
        
        logger.info(f"Successfully calculated {len(positions)} positions")
        return positions
    
    def get_orbit_path(
        self, 
        norad_id: int, 
        duration_minutes: int = 90,
        interval_seconds: int = 60
    ) -> Optional[Dict]:
        """
        Calculate orbit path points for visualization.
        
        Args:
            norad_id: NORAD ID of satellite
            duration_minutes: Duration of orbit to calculate (default: 90 min)
            interval_seconds: Time between points (default: 60 sec)
            
        Returns:
            Dictionary with orbit points and metadata
        """
        # Get satellite
        sat = self.db.query(Satellite).filter(Satellite.norad_id == norad_id).first()
        if not sat:
            return None
        
        earth_sat = self._get_earth_satellite(sat)
        if not earth_sat:
            return None
        
        try:
            # Generate time points
            start_time = datetime.now(timezone.utc)
            num_points = (duration_minutes * 60) // interval_seconds
            
            orbit_points = []
            
            for i in range(num_points):
                time = start_time + timedelta(seconds=i * interval_seconds)
                t = self.ts.from_datetime(time)
                
                geocentric = earth_sat.at(t)
                subpoint = wgs84.subpoint(geocentric)
                
                orbit_points.append({
                    'lat': float(subpoint.latitude.degrees),
                    'lon': float(subpoint.longitude.degrees),
                    'alt_km': float(subpoint.elevation.km),
                    'timestamp': time.isoformat()
                })
            
            return {
                'norad_id': norad_id,
                'name': sat.name,
                'orbit_points': orbit_points,
                'duration_minutes': duration_minutes
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate orbit path for {norad_id}: {e}")
            return None
    
    def precompute_positions(
        self, 
        duration_hours: int = 24, 
        interval_minutes: int = 10
    ) -> int:
        """
        Precompute positions for next duration_hours at given intervals.
        Store in database for fast retrieval.
        
        Args:
            duration_hours: How many hours ahead to compute
            interval_minutes: Time between position calculations
            
        Returns:
            Number of positions computed and stored
        """
        logger.info(f"Precomputing positions for next {duration_hours} hours at {interval_minutes} min intervals")
        
        satellites = self.db.query(Satellite).all()
        start_time = datetime.now(timezone.utc)
        num_intervals = (duration_hours * 60) // interval_minutes
        
        total_computed = 0
        
        for i in range(num_intervals):
            time = start_time + timedelta(minutes=i * interval_minutes)
            t = self.ts.from_datetime(time)
            
            for sat in satellites:
                try:
                    earth_sat = self._get_earth_satellite(sat)
                    if not earth_sat:
                        continue
                    
                    geocentric = earth_sat.at(t)
                    subpoint = wgs84.subpoint(geocentric)
                    
                    velocity_m_s = geocentric.velocity.km_per_s
                    velocity_magnitude = np.sqrt(
                        velocity_m_s[0]**2 + velocity_m_s[1]**2 + velocity_m_s[2]**2
                    )
                    
                    # Create position record
                    position = SatellitePosition(
                        satellite_id=sat.id,
                        timestamp=time,
                        latitude=float(subpoint.latitude.degrees),
                        longitude=float(subpoint.longitude.degrees),
                        altitude_km=float(subpoint.elevation.km),
                        velocity_km_s=float(velocity_magnitude)
                    )
                    
                    self.db.add(position)
                    total_computed += 1
                    
                except Exception as e:
                    logger.error(f"Failed to precompute position for {sat.norad_id} at {time}: {e}")
                    continue
            
            # Commit every interval to avoid huge transactions
            if (i + 1) % 6 == 0:  # Commit every 6 intervals
                try:
                    self.db.commit()
                    logger.info(f"Progress: {i+1}/{num_intervals} intervals, {total_computed} positions computed")
                except Exception as e:
                    logger.error(f"Failed to commit positions: {e}")
                    self.db.rollback()
        
        # Final commit
        try:
            self.db.commit()
            logger.info(f"Precomputation complete: {total_computed} positions stored")
        except Exception as e:
            logger.error(f"Failed to commit final positions: {e}")
            self.db.rollback()
        
        return total_computed


