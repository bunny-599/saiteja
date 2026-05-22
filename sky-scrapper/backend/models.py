import datetime
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text
from backend.database import Base

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(String, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    depth = Column(String, default="standard") # standard or deep
    job_type = Column(String, default="analyze") # analyze, marketing, future
    status = Column(String, default="pending") # pending, discovering, scraping, analyzing, complete, failed
    progress = Column(Integer, default=0)
    logs = Column(JSON, default=list) # List of dictionaries: {"time": "...", "message": "..."}
    error_log = Column(Text, default="")
    result = Column(JSON, nullable=True) # Full final JSON report
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class CompanyCache(Base):
    __tablename__ = "company_caches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String, index=True, nullable=False)
    domain = Column(String, index=True, nullable=False)
    data_type = Column(String, nullable=False) # e.g., "reviews", "website", "metrics", "social", "ads"
    scraped_data = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
