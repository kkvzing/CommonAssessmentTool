"""
Pydantic models for data validation and serialization.
Defines schemas for client data, predictions, and API responses.
"""

# Standard and third party imports
from enum import IntEnum
from typing import Optional, List
from pydantic import BaseModel, Field

# Enums for validation
class Gender(IntEnum):
    """
    Enum to represent gender with values:
    1 = Male, 2 = Female
    """
    MALE = 1
    FEMALE = 2

class PredictionInput(BaseModel):
    """
    Schema for prediction input data containing all client assessment fields.
    Used for making predictions about client outcomes.
    """
    age: int
    gender: str
    work_experience: int
    canada_workex: int
    dep_num: int
    canada_born: str
    citizen_status: str
    level_of_schooling: str
    fluent_english: str
    reading_english_scale: int
    speaking_english_scale: int
    writing_english_scale: int
    numeracy_scale: int
    computer_scale: int
    transportation_bool: str
    caregiver_bool: str
    housing: str
    income_source: str
    felony_bool: str
    attending_school: str
    currently_employed: str
    substance_use: str
    time_unemployed: int
    need_mental_health_support_bool: str

class ClientBase(BaseModel):
    """
    Base schema for client data that includes various attributes like age, gender, work experience, etc.
    This schema is used as a base class for other client-related schemas.
    """
    age: int = Field(ge=18, description="Age of client, must be 18 or older")
    gender: Gender = Field(description="Gender: 1 for male, 2 for female")
    work_experience: int = Field(ge=0, description="Years of work experience")
    canada_workex: int = Field(ge=0, description="Years of Canadian work experience")
    dep_num: int = Field(ge=0, description="Number of dependents")
    canada_born: bool = Field(description="Whether client was born in Canada")
    citizen_status: bool = Field(description="Client's citizenship status")
    level_of_schooling: int = Field(ge=1, le=14, description="Education level (1-14)")
    fluent_english: bool = Field(description="English fluency status")
    reading_english_scale: int = Field(ge=0, le=10, description="English reading level (0-10)")
    speaking_english_scale: int = Field(ge=0, le=10, description="English speaking level (0-10)")
    writing_english_scale: int = Field(ge=0, le=10, description="English writing level (0-10)")
    numeracy_scale: int = Field(ge=0, le=10, description="Numeracy skill level (0-10)")
    computer_scale: int = Field(ge=0, le=10, description="Computer skill level (0-10)")
    transportation_bool: bool = Field(description="Has transportation")
    caregiver_bool: bool = Field(description="Is a caregiver")
    housing: int = Field(ge=1, le=10, description="Housing situation (1-10)")
    income_source: int = Field(ge=1, le=11, description="Source of income (1-11)")
    felony_bool: bool = Field(description="Has felony record")
    attending_school: bool = Field(description="Currently attending school")
    currently_employed: bool = Field(description="Current employment status")
    substance_use: bool = Field(description="Substance use status")
    time_unemployed: int = Field(ge=0, description="Time unemployed in months")
    need_mental_health_support_bool: bool = Field(description="Needs mental health support")

    class Config:
        json_schema_extra = {
            "example": {
                "age": 25,
                "gender": 1,
                "work_experience": 3,
                "canada_workex": 2,
                "dep_num": 1,
                "canada_born": False,
                "citizen_status": True,
                "level_of_schooling": 8,
                "fluent_english": True,
                "reading_english_scale": 8,
                "speaking_english_scale": 7,
                "writing_english_scale": 7,
                "numeracy_scale": 8,
                "computer_scale": 9,
                "transportation_bool": True,
                "caregiver_bool": False,
                "housing": 5,
                "income_source": 3,
                "felony_bool": False,
                "attending_school": False,
                "currently_employed": False,
                "substance_use": False,
                "time_unemployed": 6,
                "need_mental_health_support_bool": False
            }
        }

class ClientResponse(ClientBase):
    """
    Client response schema that includes an `id` field.
    Inherits from `ClientBase` and adds an `id` field to uniquely identify a client.
    """
    id: int

    class Config:
        from_attributes = True  # Make sure this is relevant and necessary

class ClientUpdate(BaseModel):
    """
    Schema for client update request, allowing partial updates of client data.
    Fields are optional to allow for flexible updates.
    """
    age: Optional[int] = Field(None, ge=18)
    gender: Optional[Gender] = None
    work_experience: Optional[int] = Field(None, ge=0)
    canada_workex: Optional[int] = Field(None, ge=0)
    dep_num: Optional[int] = Field(None, ge=0)
    canada_born: Optional[bool] = None
    citizen_status: Optional[bool] = None
    level_of_schooling: Optional[int] = Field(None, ge=1, le=14)
    fluent_english: Optional[bool] = None
    reading_english_scale: Optional[int] = Field(None, ge=0, le=10)
    speaking_english_scale: Optional[int] = Field(None, ge=0, le=10)
    writing_english_scale: Optional[int] = Field(None, ge=0, le=10)
    numeracy_scale: Optional[int] = Field(None, ge=0, le=10)
    computer_scale: Optional[int] = Field(None, ge=0, le=10)
    transportation_bool: Optional[bool] = None
    caregiver_bool: Optional[bool] = None
    housing: Optional[int] = Field(None, ge=1, le=10)
    income_source: Optional[int] = Field(None, ge=1, le=11)
    felony_bool: Optional[bool] = None
    attending_school: Optional[bool] = None
    currently_employed: Optional[bool] = None
    substance_use: Optional[bool] = None
    time_unemployed: Optional[int] = Field(None, ge=0)
    need_mental_health_support_bool: Optional[bool] = None

class ServiceResponse(BaseModel):
    """
    Schema for service response, which indicates the services a client is eligible for.
    Includes boolean flags for various services and a success rate.
    """
    employment_assistance: bool
    life_stabilization: bool
    retention_services: bool
    specialized_services: bool
    employment_related_financial_supports: bool
    employer_financial_supports: bool
    enhanced_referrals: bool
    success_rate: int = Field(ge=0, le=100)

    class Config:
        from_attributes = True

class ServiceUpdate(BaseModel):
    """
    Schema for updating services, allowing partial updates to service attributes.
    """
    employment_assistance: Optional[bool] = None
    life_stabilization: Optional[bool] = None
    retention_services: Optional[bool] = None
    specialized_services: Optional[bool] = None
    employment_related_financial_supports: Optional[bool] = None
    employer_financial_supports: Optional[bool] = None
    enhanced_referrals: Optional[bool] = None
    success_rate: Optional[int] = Field(None, ge=0, le=100)

class ClientListResponse(BaseModel):
    """
    Schema for the response containing a list of clients.
    Includes the total number of clients and the list itself.
    """
    clients: List[ClientResponse]
    total: int
