"""Database models: the tracked catalogue and daily statistics snapshots."""
from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from .database import Base


class Satellite(Base):
    """One tracked object with its most recent TLE."""

    __tablename__ = "satellites"

    id = Column(Integer, primary_key=True)
    norad_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    constellation = Column(String(100), default="STARLINK", index=True)
    tle_line1 = Column(Text, nullable=False)
    tle_line2 = Column(Text, nullable=False)
    epoch = Column(DateTime(timezone=True))
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Satellite(norad_id={self.norad_id}, name={self.name!r})>"


class HistoricalSnapshot(Base):
    """Daily constellation statistics, written by the scheduler at midnight UTC."""

    __tablename__ = "historical_snapshots"

    id = Column(Integer, primary_key=True)
    snapshot_date = Column(DateTime(timezone=True), nullable=False, unique=True, index=True)
    total_satellites = Column(Integer, nullable=False)
    altitude_band_340_360 = Column(Integer, default=0)
    altitude_band_500_570 = Column(Integer, default=0)
    altitude_band_1100_1325 = Column(Integer, default=0)
    avg_congestion = Column(Float, nullable=True)
    max_density_region = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<HistoricalSnapshot(date={self.snapshot_date}, total={self.total_satellites})>"
