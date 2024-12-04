"""
Database models module defining SQLAlchemy ORM models for the Common Assessment Tool.
Contains the Client model for storing client information in the database.
"""
import enum
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, CheckConstraint, Enum
from sqlalchemy.orm import relationship
from app.database import Base

# pylint: disable=C0103, R0903, C0301, C0303, C0114
class UserRole(str, enum.Enum):
    """ Class for UserRole"""
    admin = "admin"
    case_worker = "case_worker"

class User(Base):
    """ Class for User"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role = Column(Enum(UserRole), nullable=False)

    cases = relationship("ClientCase", back_populates="user")
    
class Client(Base):
    """
    Client model representing client data in the database.
    """
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    age = Column(Integer, CheckConstraint('age >= 18'))
    gender = Column(Integer, CheckConstraint("gender = 1 OR gender = 2"))
    work_experience = Column(Integer, CheckConstraint('work_experience >= 0'))
    canada_workex = Column(Integer, CheckConstraint('canada_workex >= 0'))
    dep_num = Column(Integer, CheckConstraint('dep_num >= 0'))
    canada_born = Column(Boolean)
    citizen_status = Column(Boolean)
    level_of_schooling = Column(Integer, CheckConstraint(
        'level_of_schooling >= 1 AND level_of_schooling <= 14'))
    fluent_english = Column(Boolean)
    reading_english_scale = Column(Integer, CheckConstraint(
        'reading_english_scale >= 0 AND reading_english_scale <= 10'))
    speaking_english_scale = Column(Integer, CheckConstraint(
        'speaking_english_scale >= 0 AND speaking_english_scale <= 10'))
    writing_english_scale = Column(Integer, CheckConstraint(
        'writing_english_scale >= 0 AND writing_english_scale <= 10'))
    numeracy_scale = Column(Integer, CheckConstraint(
        'numeracy_scale >= 0 AND numeracy_scale <= 10'))
    computer_scale = Column(Integer, CheckConstraint(
        'computer_scale >= 0 AND computer_scale <= 10'))
    transportation_bool = Column(Boolean)
    caregiver_bool = Column(Boolean)
    housing = Column(Integer, CheckConstraint('housing >= 1 AND housing <= 10'))
    income_source = Column(Integer, CheckConstraint(
        'income_source >= 1 AND income_source <= 11'))
    felony_bool = Column(Boolean)
    attending_school = Column(Boolean)
    currently_employed = Column(Boolean)
    substance_use = Column(Boolean)
    time_unemployed = Column(Integer, CheckConstraint('time_unemployed >= 0'))
    need_mental_health_support_bool = Column(Boolean)
    cases = relationship("ClientCase", back_populates="client")
    
class ClientCase(Base):
    """ Class for ClientBase"""
    __tablename__ = "client_cases"

    client_id = Column(Integer, ForeignKey("clients.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    employment_assistance = Column(Boolean)
    life_stabilization = Column(Boolean)
    retention_services = Column(Boolean)
    specialized_services = Column(Boolean)
    employment_related_financial_supports = Column(Boolean)
    employer_financial_supports = Column(Boolean)
    enhanced_referrals = Column(Boolean)
    success_rate = Column(Integer, CheckConstraint(
        'success_rate >= 0 AND success_rate <= 100'))

    client = relationship("Client", back_populates="cases")
    user = relationship("User", back_populates="cases")
