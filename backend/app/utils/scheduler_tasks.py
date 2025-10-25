"""
APScheduler background tasks
Automated TLE updates and position precomputation
"""
import logging
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import os
from dotenv import load_dotenv

from ..models.database import SessionLocal
from ..models.satellite import HistoricalSnapshot
from ..services.tle_fetcher import TLEFetcher
from ..services.satellite_tracker import SatelliteTracker
from ..utils.cache import invalidate_cache

load_dotenv()

logger = logging.getLogger(__name__)

TLE_UPDATE_INTERVAL_HOURS = int(os.getenv("TLE_UPDATE_INTERVAL_HOURS", 6))


def update_tle_data():
    """
    Scheduled task: Update TLE data from CelesTrak.
    Runs every 6 hours by default.
    """
    logger.info("Starting scheduled TLE update")
    db = SessionLocal()
    
    try:
        fetcher = TLEFetcher(db)
        success = fetcher.fetch_and_update()
        
        if success:
            logger.info("TLE update completed successfully")
            # Invalidate position cache since TLEs changed
            invalidate_cache()
            
            # Optionally precompute positions for next 24 hours
            # logger.info("Precomputing positions for next 24 hours")
            # tracker = SatelliteTracker(db)
            # tracker.precompute_positions(duration_hours=24, interval_minutes=10)
        else:
            logger.error("TLE update failed")
            
    except Exception as e:
        logger.error(f"Error in TLE update task: {e}")
    finally:
        db.close()


def create_daily_snapshot():
    """
    Scheduled task: Create daily snapshot of constellation statistics.
    Runs once per day at midnight UTC.
    """
    logger.info("Creating daily historical snapshot")
    db = SessionLocal()
    
    try:
        tracker = SatelliteTracker(db)
        
        # Get current positions
        positions = tracker.get_all_positions()
        
        # Count satellites per altitude band
        band_340_360 = sum(1 for p in positions if 340 <= p['alt_km'] <= 360)
        band_500_570 = sum(1 for p in positions if 500 <= p['alt_km'] <= 570)
        band_1100_1325 = sum(1 for p in positions if 1100 <= p['alt_km'] <= 1325)
        
        # Create snapshot
        snapshot = HistoricalSnapshot(
            snapshot_date=datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0),
            total_satellites=len(positions),
            altitude_band_340_360=band_340_360,
            altitude_band_500_570=band_500_570,
            altitude_band_1100_1325=band_1100_1325
        )
        
        db.add(snapshot)
        db.commit()
        
        logger.info(f"Daily snapshot created: {len(positions)} total satellites")
        
    except Exception as e:
        logger.error(f"Error creating daily snapshot: {e}")
        db.rollback()
    finally:
        db.close()


def setup_scheduler() -> BackgroundScheduler:
    """
    Setup and configure the background scheduler.
    
    Returns:
        Configured BackgroundScheduler instance
    """
    scheduler = BackgroundScheduler(timezone="UTC")
    
    # Task 1: Update TLE data every N hours
    scheduler.add_job(
        update_tle_data,
        trigger=IntervalTrigger(hours=TLE_UPDATE_INTERVAL_HOURS),
        id='tle_update',
        name='Update TLE data from CelesTrak',
        replace_existing=True,
        max_instances=1,
        next_run_time=datetime.now(timezone.utc)  # Run immediately on startup
    )
    logger.info(f"Scheduled TLE updates every {TLE_UPDATE_INTERVAL_HOURS} hours")
    
    # Task 2: Create daily snapshot at midnight UTC
    scheduler.add_job(
        create_daily_snapshot,
        trigger=CronTrigger(hour=0, minute=0, timezone='UTC'),
        id='daily_snapshot',
        name='Create daily historical snapshot',
        replace_existing=True,
        max_instances=1
    )
    logger.info("Scheduled daily snapshots at midnight UTC")
    
    return scheduler


