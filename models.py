from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Float, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    department = Column(String(100))
    role = Column(String(20))  # admin, manager, employee
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    reviews_given = relationship('Review', back_populates='reviewer', foreign_keys='Review.reviewer_id')
    reviews_received = relationship('Review', back_populates='reviewee', foreign_keys='Review.reviewee_id')

class ReviewCycle(Base):
    __tablename__ = 'review_cycles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(20))  # draft, active, completed
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.now)
    
    reviews = relationship('Review', back_populates='review_cycle')

class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    review_cycle_id = Column(Integer, ForeignKey('review_cycles.id'))
    reviewer_id = Column(Integer, ForeignKey('users.id'))
    reviewee_id = Column(Integer, ForeignKey('users.id'))
    relationship_type = Column(String(20))  # peer, superior, subordinate, self
    
    # Performance metrics
    performance_score = Column(Float)
    leadership_score = Column(Float)
    teamwork_score = Column(Float)
    innovation_score = Column(Float)
    
    strengths = Column(Text)
    areas_for_improvement = Column(Text)
    training_recommendations = Column(Text)
    
    status = Column(String(20))  # pending, submitted, approved
    submitted_at = Column(DateTime)
    approved_at = Column(DateTime)
    
    # Relationships
    review_cycle = relationship('ReviewCycle', back_populates='reviews')
    reviewer = relationship('User', back_populates='reviews_given', foreign_keys=[reviewer_id])
    reviewee = relationship('User', back_populates='reviews_received', foreign_keys=[reviewee_id])

class ReviewAssignment(Base):
    __tablename__ = 'review_assignments'
    
    id = Column(Integer, primary_key=True)
    review_cycle_id = Column(Integer, ForeignKey('review_cycles.id'))
    reviewer_id = Column(Integer, ForeignKey('users.id'))
    reviewee_id = Column(Integer, ForeignKey('users.id'))
    relationship_type = Column(String(20))
    status = Column(String(20))  # pending, completed
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)

def init_db(database_url):
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine 