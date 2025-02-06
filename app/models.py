from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String


Base = declarative_base()

class EDL(Base):
    __tablename__ = 'edls'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)  # Optional description
    created_by = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to entries
    entries = relationship('Entry', back_populates='edl', cascade='all, delete-orphan')

class Entry(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    edl_id = Column(Integer, ForeignKey('edls.id', ondelete='CASCADE'), nullable=False)
    value = Column(String, nullable=False)  # This can be an FQDN, IP, or URL
    description = Column(String, nullable=True)  # Optional description
    created_by = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to edls
    edl = relationship('EDL', back_populates='entries')

class User(Base, UserMixin):
    """User model for authentication."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)

