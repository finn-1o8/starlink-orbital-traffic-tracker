"""
Database models for satellites, positions, and historical data.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Index, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class Satellite(Base):
    """
    Satellite metadata and TLE data.
    """
    __tablename__ = "satellites"

    id = Column(Integer, primary_key=True, index=True)
    norad_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    constellation = Column(String(100), default="STARLINK", index=True)
    tle_line1 = Column(Text, nullable=False)
    tle_line2 = Column(Text, nullable=False)
    epoch = Column(DateTime(timezone=True))
    launch_date = Column(DateTime(timezone=True), nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship to positions
    positions = relationship("SatellitePosition", back_populates="satellite", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Satellite(norad_id={self.norad_id}, name='{self.name}')>"


class SatellitePosition(Base):
    """
    Time-series satellite position data.
    Uses TimescaleDB hypertable for optimal time-series queries.
    """
    __tablename__ = "satellite_positions"

    id = Column(BigInteger, primary_key=True, index=True)
    satellite_id = Column(Integer, ForeignKey("satellites.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude_km = Column(Float, nullable=False)
    velocity_km_s = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to satellite
    satellite = relationship("Satellite", back_populates="positions")
    
    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_sat_time', 'satellite_id', 'timestamp'),
        Index('idx_timestamp', 'timestamp'),
    )

    def __repr__(self):
        return f"<SatellitePosition(satellite_id={self.satellite_id}, time={self.timestamp})>"


class HistoricalSnapshot(Base):
    """
    Daily snapshots of constellation statistics for historical tracking.
    """
    __tablename__ = "historical_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_date = Column(DateTime(timezone=True), nullable=False, unique=True, index=True)
    total_satellites = Column(Integer, nullable=False)
    altitude_band_340_360 = Column(Integer, default=0)
    altitude_band_500_570 = Column(Integer, default=0)
    altitude_band_1100_1325 = Column(Integer, default=0)
    avg_congestion = Column(Float, nullable=True)
    max_density_region = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<HistoricalSnapshot(date={self.snapshot_date}, total={self.total_satellites})>"


