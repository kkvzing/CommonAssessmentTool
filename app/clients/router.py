"""
Router module for client-related endpoints.
Handles all HTTP requests for client operations including create, read, update, and delete.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.router import get_current_user, get_admin_user
from app.models import User
from app.database import get_db
from app.clients.service.client_service import ClientService
from app.clients.schema import (
    ClientResponse,
    ClientUpdate,
    ClientListResponse,
    ServiceResponse,
    ServiceUpdate
)

router = APIRouter(prefix="/clients", tags=["clients"])

@router.get("/", response_model=ClientListResponse)
async def get_clients(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=50, ge=1, le=150, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """Retrieve a list of clients."""
    return ClientService.get_clients(db, skip, limit)

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific client by ID."""
    return ClientService.get_client(db, client_id)

@router.get("/search/by-criteria", response_model=List[ClientResponse])
async def get_clients_by_criteria(
    criteria: ClientSearchCriteria,  # Use Pydantic model for criteria
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Search clients by any combination of criteria."""
    return ClientService.get_clients_by_criteria(db, **criteria.dict())

@router.get("/search/by-services", response_model=List[ClientResponse])
async def get_clients_by_services(
    employment_assistance: Optional[bool] = None,
    life_stabilization: Optional[bool] = None,
    retention_services: Optional[bool] = None,
    specialized_services: Optional[bool] = None,
    employment_related_financial_supports: Optional[bool] = None,
    employer_financial_supports: Optional[bool] = None,
    enhanced_referrals: Optional[bool] = None,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get clients filtered by multiple service statuses."""
    return ClientService.get_clients_by_services(
        db,
        employment_assistance=employment_assistance,
        life_stabilization=life_stabilization,
        retention_services=retention_services,
        specialized_services=specialized_services,
        employment_related_financial_supports=employment_related_financial_supports,
        employer_financial_supports=employer_financial_supports,
        enhanced_referrals=enhanced_referrals
    )

@router.get("/{client_id}/services", response_model=List[ServiceResponse])
async def get_client_services(
    client_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all services and their status for a specific client, including case worker info."""
    return ClientService.get_client_services(db, client_id)

@router.get("/search/success-rate", response_model=List[ClientResponse])
async def get_clients_by_success_rate(
    min_rate: int = Query(70, ge=0, le=100, description="Minimum success rate percentage"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get clients with success rate above specified threshold."""
    return ClientService.get_clients_by_success_rate(db, min_rate)

@router.get("/case-worker/{case_worker_id}", response_model=List[ClientResponse])
async def get_clients_by_case_worker(
    case_worker_id: int,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Get all clients assigned to a specific case worker."""
    return ClientService.get_clients_by_case_worker(db, case_worker_id)

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update a client's information."""
    return ClientService.update_client(db, client_id, client_data)

@router.put("/{client_id}/services/{user_id}", response_model=ServiceResponse)
async def update_client_services(
    client_id: int,
    user_id: int,
    service_update: ServiceUpdate,
    current_user: User = Depends(get_current_user),  
    db: Session = Depends(get_db)
):
    """Update a client's service information."""
    return ClientService.update_client_services(db, client_id, user_id, service_update)

@router.post("/{client_id}/case-assignment", response_model=ServiceResponse)
async def create_case_assignment(
    client_id: int,
    case_worker_id: int = Query(..., description="Case worker ID to assign"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new case assignment for a client with a case worker."""
    return ClientService.create_case_assignment(db, client_id, case_worker_id)

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a client."""
    ClientService.delete_client(db, client_id)
    return None

# Pydantic model for client search criteria (to reduce function arguments)
from pydantic import BaseModel

class ClientSearchCriteria(BaseModel):
    employment_status: Optional[bool] = None
    education_level: Optional[int] = Query(None, ge=1, le=14)
    age_min: Optional[int] = Query(None, ge=18)
    gender: Optional[int] = Query(None, ge=1, le=2)
    work_experience: Optional[int] = Query(None, ge=0)
    canada_workex: Optional[int] = Query(None, ge=0)
    dep_num: Optional[int] = Query(None, ge=0)
    canada_born: Optional[bool] = None
    citizen_status: Optional[bool] = None
    fluent_english: Optional[bool] = None
    reading_english_scale: Optional[int] = Query(None, ge=0, le=10)
    speaking_english_scale: Optional[int] = Query(None, ge=0, le=10)
    writing_english_scale: Optional[int] = Query(None, ge=0, le=10)
    numeracy_scale: Optional[int] = Query(None, ge=0, le=10)
    computer_scale: Optional[int] = Query(None, ge=0, le=10)
    transportation_bool: Optional[bool] = None
    caregiver_bool: Optional[bool] = None
    housing: Optional[int] = Query(None, ge=1, le=10)
    income_source: Optional[int] = Query(None, ge=1, le=11)
    felony_bool: Optional[bool] = None
    attending_school: Optional[bool] = None
    substance_use: Optional[bool] = None
    time_unemployed: Optional[int] = Query(None, ge=0)
    need_mental_health_support_bool: Optional[bool] = None
