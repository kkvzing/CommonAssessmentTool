"""
Router module for client-related endpoints.
Handles all HTTP requests for client operations including create, read, update, and delete.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.clients.service.client_service import ClientService
from app.clients.schema import (
    ClientResponse,
    ClientUpdate,
    ClientListResponse,
    ServiceResponse,
    ServiceUpdate
)

# Pydantic model to handle query parameters
from pydantic import BaseModel

class ClientSearchCriteria(BaseModel):
    employment_status: Optional[bool] = None
    education_level: Optional[int] = None
    age_min: Optional[int] = None
    gender: Optional[int] = None
    work_experience: Optional[int] = None
    canada_workex: Optional[int] = None
    dep_num: Optional[int] = None
    canada_born: Optional[bool] = None
    citizen_status: Optional[bool] = None
    fluent_english: Optional[bool] = None
    reading_english_scale: Optional[int] = None
    speaking_english_scale: Optional[int] = None
    writing_english_scale: Optional[int] = None
    numeracy_scale: Optional[int] = None
    computer_scale: Optional[int] = None
    transportation_bool: Optional[bool] = None
    caregiver_bool: Optional[bool] = None
    housing: Optional[int] = None
    income_source: Optional[int] = None
    felony_bool: Optional[bool] = None
    attending_school: Optional[bool] = None
    substance_use: Optional[bool] = None
    time_unemployed: Optional[int] = None
    need_mental_health_support_bool: Optional[bool] = None

router = APIRouter(prefix="/clients", tags=["clients"])

@router.get("/", response_model=ClientListResponse)
async def get_clients(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=50, ge=1, le=150, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """Get a paginated list of all clients"""
    return ClientService.get_clients(db, skip, limit)

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific client by ID"""
    return ClientService.get_client(db, client_id)

@router.get("/search/by-criteria", response_model=List[ClientResponse])
async def get_clients_by_criteria(
    criteria: ClientSearchCriteria = Depends(),
    db: Session = Depends(get_db)
):
    """Search clients by any combination of criteria"""
    return ClientService.get_clients_by_criteria(
        db,
        **criteria.dict(exclude_unset=True)  # Pass non-null fields
    )

@router.get("/search/by-services", response_model=List[ClientResponse])
async def get_clients_by_services(
    employment_assistance: Optional[bool] = None,
    life_stabilization: Optional[bool] = None,
    retention_services: Optional[bool] = None,
    specialized_services: Optional[bool] = None,
    employment_related_financial_supports: Optional[bool] = None,
    employer_financial_supports: Optional[bool] = None,
    enhanced_referrals: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get clients filtered by multiple service statuses"""
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

@router.get("/{client_id}/services", response_model=ServiceResponse)
async def get_client_services(
    client_id: int,
    db: Session = Depends(get_db)
):
    """Get all services and their status for a specific client"""
    return ClientService.get_client_services(db, client_id)

@router.get("/search/success-rate", response_model=List[ClientResponse])
async def get_clients_by_success_rate(
    min_rate: int = Query(70, ge=0, le=100, description="Minimum success rate percentage"),
    db: Session = Depends(get_db)
):
    """Get clients with success rate above specified threshold"""
    return ClientService.get_clients_by_success_rate(db, min_rate)

@router.get("/case-worker/{case_worker_id}", response_model=List[ClientResponse])
async def get_clients_by_case_worker(
    case_worker_id: int,
    db: Session = Depends(get_db)
):
    """Get all clients assigned to a specific case worker"""
    return ClientService.get_clients_by_case_worker(db, case_worker_id)

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_db)
):
    """Update a client's information"""
    return ClientService.update_client(db, client_id, client_data)

@router.put("/{client_id}/services", response_model=ServiceResponse)
async def update_client_services(
    client_id: int,
    service_update: ServiceUpdate,
    db: Session = Depends(get_db)
):
    """Update a client's services and outcome information"""
    return ClientService.update_client_services(db, client_id, service_update)

@router.put("/{client_id}/case-worker", response_model=ServiceResponse)
async def update_client_case_worker(
    client_id: int,
    case_worker_id: int = Query(..., description="ID of the new case worker"),
    db: Session = Depends(get_db)
):
    """Assign a client to a different case worker"""
    return ClientService.update_client_case_worker(db, client_id, case_worker_id)

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    """Delete a client"""
    ClientService.delete_client(db, client_id)
    return None
