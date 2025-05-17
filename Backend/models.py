"""
RLG Data Model Core - Enterprise Scrum Architecture
Version: 11.0.0
Features: Multi-Tenant Support, GDPR Compliance, AI Integration
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
import pytz
import geoip2.database
import json

Base = declarative_base()

class RLGBase:
    """Base model with common audit fields"""
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utc_now)
    updated_at = Column(DateTime, default=datetime.utc_now, onupdate=datetime.utc_now)
    is_active = Column(Boolean, default=True)
    
    @hybrid_property
    def time_since_update(self):
        return datetime.utcnow() - self.updated_at

class User(Base, RLGBase):
    __tablename__ = 'users'
    
    # Authentication
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    mfa_secret = Column(String(32))
    
    # Scrum Role
    roles = Column(JSON, default=['member'])  # PO, SM, Developer
    
    # Localization
    timezone = Column(String(50), default='UTC')
    preferred_language = Column(String(10), default='en')
    
    # GDPR Compliance
    consent_terms = Column(DateTime)
    consent_privacy = Column(DateTime)
    data_deletion_request = Column(DateTime)
    anonymized = Column(Boolean, default=False)
    
    # Security
    failed_login_attempts = Column(Integer, default=0)
    last_login = Column(DateTime)
    security_questions = Column(JSON)
    
    # Relationships
    teams = relationship('TeamMember', back_populates='user')
    owned_projects = relationship('Project', back_populates='owner')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='scrypt')
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Project(Base, RLGBase):
    __tablename__ = 'projects'
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(20), default='planning')  # planning, active, completed
    
    # Time Management
    start_date = Column(DateTime)
    target_end_date = Column(DateTime)
    
    # Localization
    default_language = Column(String(10), default='en')
    supported_timezones = Column(JSON, default=['UTC'])
    
    # AI Integration
    risk_profile = Column(JSON)
    ai_settings = Column(JSON)
    
    # Relationships
    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship('User', back_populates='owned_projects')
    sprints = relationship('Sprint', back_populates='project')
    backlog = relationship('BacklogItem', back_populates='project')
    teams = relationship('ProjectTeam', back_populates='project')

class Sprint(Base, RLGBase):
    __tablename__ = 'sprints'
    
    name = Column(String(100), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(20), default='planned')  # planned, active, completed
    
    # Metrics
    velocity = Column(Float)
    story_points_committed = Column(Integer)
    story_points_completed = Column(Integer)
    
    # AI Insights
    risk_assessment = Column(JSON)
    ai_recommendations = Column(JSON)
    
    # Relationships
    project_id = Column(Integer, ForeignKey('projects.id'))
    project = relationship('Project', back_populates='sprints')
    tasks = relationship('Task', back_populates='sprint')
    
    @hybrid_property
    def progress(self):
        if self.story_points_committed:
            return self.story_points_completed / self.story_points_committed
        return 0

class Task(Base, RLGBase):
    __tablename__ = 'tasks'
    
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(20), default='todo')  # todo, in_progress, blocked, done
    story_points = Column(Integer)
    priority = Column(String(20), default='medium')
    
    # AI Predictions
    complexity_score = Column(Float)
    predicted_duration = Column(Float)  # in hours
    
    # Relationships
    sprint_id = Column(Integer, ForeignKey('sprints.id'))
    sprint = relationship('Sprint', back_populates='tasks')
    assignee_id = Column(Integer, ForeignKey('users.id'))
    assignee = relationship('User')

class BacklogItem(Base, RLGBase):
    __tablename__ = 'backlog_items'
    
    title = Column(String(200), nullable=False)
    description = Column(Text)
    priority = Column(Integer, index=True)
    status = Column(String(20), default='proposed')  # proposed, approved, rejected
    
    # AI Prioritization
    business_value = Column(Float)
    technical_complexity = Column(Float)
    ai_priority_score = Column(Float)
    
    # Relationships
    project_id = Column(Integer, ForeignKey('projects.id'))
    project = relationship('Project', back_populates='backlog')

class Team(Base, RLGBase):
    __tablename__ = 'teams'
    
    name = Column(String(100), nullable=False)
    purpose = Column(Text)
    
    # Distributed Team Support
    timezones = Column(JSON)
    working_hours = Column(JSON)
    preferred_communication = Column(JSON)  # {slack: '#channel', email: 'group@'}
    
    # Relationships
    projects = relationship('ProjectTeam', back_populates='team')
    members = relationship('TeamMember', back_populates='team')

class ProjectTeam(Base):
    __tablename__ = 'project_teams'
    
    project_id = Column(Integer, ForeignKey('projects.id'), primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), primary_key=True)
    role = Column(String(20))  # dev, qa, design
    
    project = relationship('Project', back_populates='teams')
    team = relationship('Team', back_populates='projects')

class TeamMember(Base):
    __tablename__ = 'team_members'
    
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), primary_key=True)
    role = Column(String(20))  # member, lead
    
    user = relationship('User', back_populates='teams')
    team = relationship('Team', back_populates='members')

class ComplianceRecord(Base, RLGBase):
    __tablename__ = 'compliance_records'
    
    record_type = Column(String(50))  # GDPR, CCPA, HIPAA
    action = Column(String(50))  # consent, deletion, access
    user_id = Column(Integer, ForeignKey('users.id'))
    data_snapshot = Column(JSON)
    ip_address = Column(String(45))
    geo_data = Column(JSON)
    
    user = relationship('User')

class AIInteraction(Base, RLGBase):
    __tablename__ = 'ai_interactions'
    
    interaction_type = Column(String(50))  # recommendation, risk_assessment
    model_version = Column(String(50))
    input_data = Column(JSON)
    output_data = Column(JSON)
    confidence_score = Column(Float)
    user_feedback = Column(JSON)
    
    project_id = Column(Integer, ForeignKey('projects.id'))
    sprint_id = Column(Integer, ForeignKey('sprints.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    
    project = relationship('Project')
    sprint = relationship('Sprint')
    user = relationship('User')

# Utility Functions
def get_local_time(user):
    return datetime.now(pytz.timezone(user.timezone))

def anonymize_user(user):
    user.email = f"anon_{user.id}@deleted.com"
    user.password_hash = ""
    user.security_questions = {}
    user.anonymized = True
    return user