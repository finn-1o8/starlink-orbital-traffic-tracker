"""
TLE Data Fetching Service
Fetches Two-Line Element data from CelesTrak and updates the database.
"""
import requests
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from ..models.satellite import Satellite

logger = logging.getLogger(__name__)


class TLEFetcher:
    """
    Fetches and parses TLE data from CelesTrak.
    """
    
    CELESTRAK_STARLINK_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle"
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds
    
    def __init__(self, db: Session):
        self.db = db
    
    def fetch_starlink_tles(self) -> Optional[List[Dict]]:
        """
        Fetch Starlink TLE data from CelesTrak.
        
        Returns:
            List of dictionaries containing satellite TLE data, or None on failure.
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"Fetching Starlink TLEs from CelesTrak (attempt {attempt + 1}/{self.MAX_RETRIES})")
                
                response = requests.get(
                    self.CELESTRAK_STARLINK_URL,
                    timeout=30,
                    headers={'User-Agent': 'OrbitalTrafficAnalyzer/1.0'}
                )
                response.raise_for_status()
                
                tles = self._parse_tle_data(response.text)
                logger.info(f"Successfully fetched {len(tles)} Starlink TLEs")
                return tles
                
            except requests.RequestException as e:
                logger.error(f"Failed to fetch TLEs (attempt {attempt + 1}): {e}")
                if attempt < self.MAX_RETRIES - 1:
                    import time
                    time.sleep(self.RETRY_DELAY)
                else:
                    logger.error("Max retries reached. TLE fetch failed.")
                    return None
        
        return None
    
    def _parse_tle_data(self, tle_text: str) -> List[Dict]:
        """
        Parse TLE format data.
        TLE format: 3 lines per satellite (name, line1, line2)
        
        Args:
            tle_text: Raw TLE text data
            
        Returns:
            List of dictionaries with parsed TLE data
        """
        lines = [line.strip() for line in tle_text.strip().split('\n') if line.strip()]
        satellites = []
        
        # Process in groups of 3 lines
        for i in range(0, len(lines) - 2, 3):
            try:
                name = lines[i].strip()
                line1 = lines[i + 1].strip()
                line2 = lines[i + 2].strip()
                
                # Validate TLE format
                if not (line1.startswith('1 ') and line2.startswith('2 ')):
                    logger.warning(f"Invalid TLE format for {name}")
                    continue
                
                # Extract NORAD ID from line 1 (columns 3-7)
                norad_id = int(line1[2:7].strip())
                
                # Extract epoch from line 1 (columns 18-32)
                epoch_str = line1[18:32].strip()
                epoch = self._parse_tle_epoch(epoch_str)
                
                # Validate checksum (last digit of each line)
                if not self._validate_tle_checksum(line1) or not self._validate_tle_checksum(line2):
                    logger.warning(f"TLE checksum validation failed for {name} (NORAD {norad_id})")
                    # Continue anyway - checksums can sometimes be off but TLE is still usable
                
                satellites.append({
                    'name': name,
                    'norad_id': norad_id,
                    'line1': line1,
                    'line2': line2,
                    'epoch': epoch
                })
                
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse TLE at line {i}: {e}")
                continue
        
        return satellites
    
    def _parse_tle_epoch(self, epoch_str: str) -> datetime:
        """
        Parse TLE epoch format (YYDDD.DDDDDDDD).
        
        Args:
            epoch_str: TLE epoch string
            
        Returns:
            datetime object
        """
        try:
            year = int(epoch_str[:2])
            # Y2K correction
            year = year + 2000 if year < 57 else year + 1900
            
            day_of_year = float(epoch_str[2:])
            
            # Create datetime from year and day of year
            from datetime import timedelta
            epoch = datetime(year, 1, 1, tzinfo=timezone.utc) + timedelta(days=day_of_year - 1)
            return epoch
            
        except Exception as e:
            logger.error(f"Failed to parse epoch '{epoch_str}': {e}")
            return datetime.now(timezone.utc)
    
    def _validate_tle_checksum(self, line: str) -> bool:
        """
        Validate TLE checksum (modulo 10).
        
        Args:
            line: TLE line to validate
            
        Returns:
            True if checksum is valid
        """
        try:
            checksum = int(line[-1])
            calculated = 0
            
            for char in line[:-1]:
                if char.isdigit():
                    calculated += int(char)
                elif char == '-':
                    calculated += 1
            
            return (calculated % 10) == checksum
        except (ValueError, IndexError):
            return False
    
    def update_database(self, tles: List[Dict]) -> int:
        """
        Update database with fetched TLE data.
        Creates new satellites or updates existing ones.
        
        Args:
            tles: List of TLE dictionaries
            
        Returns:
            Number of satellites updated
        """
        updated_count = 0
        
        for tle in tles:
            try:
                # Check if satellite exists
                satellite = self.db.query(Satellite).filter(
                    Satellite.norad_id == tle['norad_id']
                ).first()
                
                if satellite:
                    # Update existing
                    satellite.name = tle['name']
                    satellite.tle_line1 = tle['line1']
                    satellite.tle_line2 = tle['line2']
                    satellite.epoch = tle['epoch']
                    satellite.last_updated = datetime.now(timezone.utc)
                else:
                    # Create new
                    satellite = Satellite(
                        norad_id=tle['norad_id'],
                        name=tle['name'],
                        constellation='STARLINK',
                        tle_line1=tle['line1'],
                        tle_line2=tle['line2'],
                        epoch=tle['epoch']
                    )
                    self.db.add(satellite)
                
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to update satellite {tle.get('norad_id')}: {e}")
                continue
        
        try:
            self.db.commit()
            logger.info(f"Successfully updated {updated_count} satellites in database")
        except Exception as e:
            logger.error(f"Database commit failed: {e}")
            self.db.rollback()
            return 0
        
        return updated_count
    
    def fetch_and_update(self) -> bool:
        """
        Main method: Fetch TLEs and update database.
        
        Returns:
            True if successful, False otherwise
        """
        tles = self.fetch_starlink_tles()
        
        if not tles:
            logger.error("Failed to fetch TLEs - using cached data")
            return False
        
        count = self.update_database(tles)
        return count > 0


