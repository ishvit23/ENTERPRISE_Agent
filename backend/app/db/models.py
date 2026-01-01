"""
SQLAlchemy models for users, queries, documents, and audit_logs.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    department = Column(String, nullable=False)
    role = Column(String, nullable=True)  # Role is now nullable, set on registration
    password_hash = Column(String, nullable=True)  # Hashed password for standard login

class Query(Base):
    __tablename__ = 'queries'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    question = Column(Text, nullable=False)
    answer = Column(Text)
    confidence = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    version = Column(String, nullable=False)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
