from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(Text)
    location = Column(String(100))
    company = Column(String(100))
    skills_json = Column(Text, default="[]")

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True)
    resume_text = Column(Text)
    skills_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    score = Column(Float)
    matching_skills_json = Column(Text, default="[]")
    missing_skills_json = Column(Text, default="[]")
    explanation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Global engine and session maker
engine = create_engine("sqlite:///./app.db", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables on import
Base.metadata.create_all(bind=engine)