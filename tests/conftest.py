import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models import User, UserRole, Client, ClientCase
#from app.auth.router import get_password_hash

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def test_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        # Create test admin user
        admin_user = User(
            username="testadmin",
            email="testadmin@example.com",
            role=UserRole.admin
        )
        db.add(admin_user)

        # Create test case worker
        case_worker = User(
            username="testworker",
            email="worker@example.com",
            role=UserRole.case_worker
        )
        db.add(case_worker)

        # Create test clients
        client1 = Client(
            age=25,
            gender=1,
            work_experience=3,
            canada_workex=2,
            dep_num=1,
            canada_born=True,
            citizen_status=True,
            level_of_schooling=8,
            fluent_english=True,
            reading_english_scale=8,
            speaking_english_scale=7,
            writing_english_scale=7,
            numeracy_scale=8,
            computer_scale=9,
            transportation_bool=True,
            caregiver_bool=False,
            housing=5,
            income_source=3,
            felony_bool=False,
            attending_school=False,
            currently_employed=False,
            substance_use=False,
            time_unemployed=6,
            need_mental_health_support_bool=False
        )
        
        client2 = Client(
            age=30,
            gender=2,
            work_experience=5,
            canada_workex=3,
            dep_num=2,
            canada_born=False,
            citizen_status=True,
            level_of_schooling=10,
            fluent_english=True,
            reading_english_scale=9,
            speaking_english_scale=8,
            writing_english_scale=8,
            numeracy_scale=7,
            computer_scale=8,
            transportation_bool=True,
            caregiver_bool=True,
            housing=4,
            income_source=2,
            felony_bool=False,
            attending_school=True,
            currently_employed=True,
            substance_use=False,
            time_unemployed=0,
            need_mental_health_support_bool=False
        )
        
        db.add(client1)
        db.add(client2)
        db.commit()
        
        # Create test client cases
        client_case1 = ClientCase(
            client_id=1,
            user_id=1,  # Assigned to admin
            employment_assistance=True,
            life_stabilization=True,
            retention_services=False,
            specialized_services=False,
            employment_related_financial_supports=True,
            employer_financial_supports=False,
            enhanced_referrals=True,
            success_rate=75
        )
        
        client_case2 = ClientCase(
            client_id=2,
            user_id=2,  # Assigned to case worker
            employment_assistance=True,
            life_stabilization=False,
            retention_services=True,
            specialized_services=True,
            employment_related_financial_supports=False,
            employer_financial_supports=True,
            enhanced_referrals=False,
            success_rate=85
        )
        
        db.add(client_case1)
        db.add(client_case2)
        db.commit()
        
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def admin_token(client):
    response = client.post(
        "/auth/token",
        data={"username": "testadmin", "password": "testpass123"}
    )
    return response.json()["access_token"]

@pytest.fixture
def case_worker_token(client):
    response = client.post(
        "/auth/token",
        data={"username": "testworker", "password": "workerpass123"}
    )
    return response.json()["access_token"]

@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def case_worker_headers(case_worker_token):
    return {"Authorization": f"Bearer {case_worker_token}"}
    