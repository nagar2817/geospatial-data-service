# import uuid
# from datetime import datetime
# from sqlalchemy import Column, String, DateTime, Float, Text, ForeignKey
# from sqlalchemy.dialects.postgresql import UUID, JSONB
# from sqlalchemy.orm import relationship
# from database.connection import Base

# class SatelliteData(Base):
#     """Satellite data and computed metrics storage."""
    
#     __tablename__ = "satellite_data"
    
#     id = Column(
#         UUID(as_uuid=True),
#         primary_key=True,
#         default=uuid.uuid4,
#         doc="Unique identifier for satellite data record"
#     )
    
#     job_run_id = Column(
#         UUID(as_uuid=True),
#         ForeignKey("carbonleap.job_runs.id", ondelete="CASCADE"),
#         nullable=False,
#         doc="Reference to the job run that generated this data"
#     )
    
#     satellite_type = Column(
#         String(50),
#         nullable=False,
#         doc="Satellite source: Sentinel-2, Landsat-8, etc."
#     )
    
#     acquisition_date = Column(
#         DateTime,
#         nullable=False,
#         doc="Date when satellite image was captured"
#     )
    
#     cloud_coverage = Column(
#         Float,
#         nullable=True,
#         doc="Cloud coverage percentage"
#     )
    
#     # Computed metrics
#     ndvi_mean = Column(Float, nullable=True, doc="Mean NDVI value")
#     ndvi_std = Column(Float, nullable=True, doc="NDVI standard deviation")
#     ndvi_min = Column(Float, nullable=True, doc="Minimum NDVI value")
#     ndvi_max = Column(Float, nullable=True, doc="Maximum NDVI value")
    
#     ndwi_mean = Column(Float, nullable=True, doc="Mean NDWI value")
#     ndwi_std = Column(Float, nullable=True, doc="NDWI standard deviation")
    
#     ndmi_mean = Column(Float, nullable=True, doc="Mean NDMI value")
#     ndmi_std = Column(Float, nullable=True, doc="NDMI standard deviation")
    
#     # Geometry and metadata
#     geometry_geojson = Column(
#         JSONB,
#         nullable=False,
#         doc="GeoJSON representation of the analyzed area"
#     )
    
#     satellite_metadata = Column(
#         JSONB,
#         nullable=True,
#         doc="Additional satellite metadata and processing parameters"
#     )
    
#     image_urls = Column(
#         JSONB,
#         nullable=True,
#         doc="URLs to processed images stored in S3 or other storage"
#     )
    
#     processing_status = Column(
#         String(20),
#         nullable=False,
#         default="processed",
#         doc="Processing status: processed, failed, partial"
#     )
    
#     created_at = Column(
#         DateTime,
#         nullable=False,
#         default=datetime.utcnow,
#         doc="Record creation timestamp"
#     )
    
#     # Relationship to job run
#     job_run = relationship("JobRun", backref="satellite_data")