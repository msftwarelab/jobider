"""
Database models for JobBider application
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class Job(Base):
    """Model for storing job listings"""
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    platform = Column(String(50), nullable=False)  # dice, indeed, etc.
    job_id = Column(String(255), unique=True, nullable=False)  # Platform-specific job ID
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255))
    job_type = Column(String(50))  # Full-time, Contract, etc.
    experience_level = Column(String(50))
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    description = Column(Text)
    requirements = Column(Text)
    url = Column(String(500), nullable=False)
    posted_date = Column(DateTime)
    discovered_date = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Job(title='{self.title}', company='{self.company}', platform='{self.platform}')>"


class Application(Base):
    """Model for tracking job applications"""
    __tablename__ = 'applications'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(String(255), nullable=False)  # References Job.job_id
    platform = Column(String(50), nullable=False)
    applied_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default='submitted')  # submitted, viewed, rejected, interview, etc.
    match_score = Column(Float)  # How well the job matched criteria (0-100)
    application_method = Column(String(50))  # automated, manual
    notes = Column(Text)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Application(job_id='{self.job_id}', status='{self.status}', date='{self.applied_date}')>"


class UserProfile(Base):
    """Model for storing user profile data"""
    __tablename__ = 'user_profile'
    
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(String(500))
    resume_path = Column(String(500))
    cover_letter_path = Column(String(500))
    linkedin_url = Column(String(500))
    portfolio_url = Column(String(500))
    
    # Work authorization
    work_authorization = Column(String(255))
    willing_to_relocate = Column(Boolean, default=False)
    expected_salary = Column(Float)
    notice_period = Column(String(100))
    
    # Skills
    skills = Column(Text)  # Comma-separated or JSON
    experience_years = Column(Integer)
    
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserProfile(name='{self.full_name}', email='{self.email}')>"


class SearchHistory(Base):
    """Model for tracking search history and performance"""
    __tablename__ = 'search_history'
    
    id = Column(Integer, primary_key=True)
    platform = Column(String(50), nullable=False)
    search_date = Column(DateTime, default=datetime.utcnow)
    keywords = Column(String(500))
    location = Column(String(255))
    jobs_found = Column(Integer, default=0)
    jobs_matched = Column(Integer, default=0)
    applications_submitted = Column(Integer, default=0)
    applications_failed = Column(Integer, default=0)
    execution_time_seconds = Column(Float)
    
    def __repr__(self):
        return f"<SearchHistory(platform='{self.platform}', date='{self.search_date}', jobs_found={self.jobs_found})>"


class Database:
    """Database manager class"""
    
    def __init__(self, db_url=None):
        if db_url is None:
            db_url = os.getenv('DATABASE_URL', 'sqlite:///jobider.db')
        
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        """Get a new database session"""
        return self.Session()
    
    def job_exists(self, job_id, platform):
        """Check if a job already exists in database"""
        session = self.get_session()
        try:
            job = session.query(Job).filter_by(job_id=job_id, platform=platform).first()
            return job is not None
        finally:
            session.close()
    
    def application_exists(self, job_id, platform):
        """Check if we've already applied to this job"""
        session = self.get_session()
        try:
            app = session.query(Application).filter_by(job_id=job_id, platform=platform).first()
            return app is not None
        finally:
            session.close()
    
    def save_job(self, job_data):
        """Save a job to the database"""
        session = self.get_session()
        try:
            job = Job(**job_data)
            session.add(job)
            session.commit()
            return job
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def save_application(self, app_data):
        """Save an application record"""
        session = self.get_session()
        try:
            app = Application(**app_data)
            session.add(app)
            session.commit()
            return app
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_applications_today(self):
        """Get count of applications submitted today"""
        session = self.get_session()
        try:
            today = datetime.utcnow().date()
            count = session.query(Application).filter(
                Application.applied_date >= today
            ).count()
            return count
        finally:
            session.close()
    
    def get_statistics(self):
        """Get application statistics"""
        session = self.get_session()
        try:
            total_jobs = session.query(Job).count()
            total_applications = session.query(Application).count()
            successful_applications = session.query(Application).filter_by(success=True).count()
            
            return {
                'total_jobs_discovered': total_jobs,
                'total_applications': total_applications,
                'successful_applications': successful_applications,
                'failed_applications': total_applications - successful_applications
            }
        finally:
            session.close()
