"""
Database models module defining SQLAlchemy ORM models for the Common Assessment Tool.
Contains the Client model for storing client information in the database.
"""
# Standard imports
import enum

# Third-party imports
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, CheckConstraint, Enum
from sqlalchemy.orm import relationship

# Local imports
from app.database import Base

class UserRole(str, enum.Enum):
    """
    Enum for user roles. Defines the roles that a user can have in the system.
    """
    ADMIN = "admin"
    CASE_WORKER = "case_worker"


class User(Base):
    """
    Represents a user in the system.

    Attributes:
        id: The unique identifier for the user.
        username: The username of the user.
        email: The email address of the user.
        hashed_password: The hashed password for the user.
        role: The role of the user (admin, case worker).
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role = Column(Enum(UserRole), nullable=False)

    cases = relationship("ClientCase", back_populates="user")

class Client(Base):
    """
    Represents a client in the system.

    Attributes:
        id: The unique identifier for the client.
        age: The age of the client.
        gender: The gender of the client (1 for male, 2 for female).
        work_experience: The years of work experience the client has.
        canada_workex: The years of work experience the client has in Canada.
        dep_num: The number of dependents the client has.
        canada_born: Whether the client was born in Canada.
        citizen_status: Whether the client is a citizen.
        level_of_schooling: The client's highest level of schooling (1-14).
        fluent_english: Whether the client is fluent in English.
        reading_english_scale: The client's reading ability on a scale of 0 to 10.
        speaking_english_scale: The client's speaking ability on a scale of 0 to 10.
        writing_english_scale: The client's writing ability on a scale of 0 to 10.
        numeracy_scale: The client's numeracy ability on a scale of 0 to 10.
        computer_scale: The client's computer literacy on a scale of 0 to 10.
        transportation_bool: Whether the client has access to transportation.
        caregiver_bool: Whether the client is a caregiver.
        housing: The client's housing situation on a scale of 1 to 10.
        income_source: The client's source of income (1-11).
        felony_bool: Whether the client has a felony record.
        attending_school: Whether the client is currently attending school.
        currently_employed: Whether the client is currently employed.
        substance_use: Whether the client is using substances.
        time_unemployed: The amount of time the client has been unemployed.
        need_mental_health_support_bool: Whether the client needs mental health support.
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
    level_of_schooling = Column(Integer, CheckConstraint('level_of_schooling >= 1 AND level_of_schooling <= 14'))
    fluent_english = Column(Boolean)
    reading_english_scale = Column(Integer,
                                   CheckConstraint('reading_english_scale >= 0 AND reading_english_scale <= 10'))
    speaking_english_scale = Column(Integer,
                                    CheckConstraint('speaking_english_scale >= 0 AND speaking_english_scale <= 10'))
    writing_english_scale = Column(Integer,
                                   CheckConstraint('writing_english_scale >= 0 AND writing_english_scale <= 10'))
    numeracy_scale = Column(Integer, CheckConstraint('numeracy_scale >= 0 AND numeracy_scale <= 10'))
    computer_scale = Column(Integer, CheckConstraint('computer_scale >= 0 AND computer_scale <= 10'))
    transportation_bool = Column(Boolean)
    caregiver_bool = Column(Boolean)
    housing = Column(Integer, CheckConstraint('housing >= 1 AND housing <= 10'))
    income_source = Column(Integer, CheckConstraint('income_source >= 1 AND income_source <= 11'))
    felony_bool = Column(Boolean)
    attending_school = Column(Boolean)
    currently_employed = Column(Boolean)
    substance_use = Column(Boolean)
    time_unemployed = Column(Integer, CheckConstraint('time_unemployed >= 0'))
    need_mental_health_support_bool = Column(Boolean)

    cases = relationship("ClientCase", back_populates="client")

class ClientCase(Base):
    """
    Represents a case assigned to a client.

    Attributes:
        client_id: The unique identifier of the client for whom the case is assigned.
        user_id: The unique identifier of the user (e.g., a case worker) managing the case.
        employment_assistance: Whether the client is receiving employment assistance.
        life_stabilization: Whether the client is receiving life stabilization services.
        retention_services: Whether the client is receiving retention services.
        specialized_services: Whether the client is receiving specialized services.
        employment_related_financial_supports: Whether the client is receiving employment-related financial supports.
        employer_financial_supports: Whether the client is receiving employer financial supports.
        enhanced_referrals: Whether the client is receiving enhanced referrals.
        success_rate: The success rate of the client on a scale of 0 to 100.
    """
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
    success_rate = Column(Integer, CheckConstraint('success_rate >= 0 AND success_rate <= 100'))

    client = relationship("Client", back_populates="cases")
    user = relationship("User", back_populates="cases")
