# pylint: disable=missing-module-docstring, pointless-string-statement, no-self-argument, too-few-public-methods, missing-final-newline
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel, Field, validator

from app.database import get_db
from app.models import User, UserRole

# Module Docstring
"""
This module provides authentication functionalities, including user login, token generation,
and user creation, along with user role validation. It also includes utility functions for
password management and access control.
"""

# Router Configuration
router = APIRouter(prefix="/auth", tags=["authentication"])

# Configuration Constants
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

class UserCreate(BaseModel):
    """
    Pydantic model for creating a new user.

    Attributes:
    - username (str): The username of the user.
    - email (str): The email address of the user.
    - password (str): The password of the user.
    - role (UserRole): The role of the user (either admin or case_worker).
    """

    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str
    role: UserRole

    @validator('role')
    def validate_role(cls, v):
        """
        Validates that the role is either admin or case_worker.

        Args:
        - v: The role value to be validated.

        Returns:
        - str: The validated role value.

        Raises:
        - ValueError: If the role is neither admin nor case_worker.
        """
        if v not in [UserRole.admin, UserRole.case_worker]:
            raise ValueError('Role must be either admin or case_worker')
        return v

class UserResponse(BaseModel):
    """
    Pydantic model for user response, used to send user information back in API responses.

    Attributes:
    - username (str): The username of the user.
    - email (str): The email address of the user.
    - role (UserRole): The role of the user (admin or case_worker).
    """

    username: str
    email: str
    role: UserRole

    class Config:
        from_attributes = True

# Helper Functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if the plain password matches the hashed password.

    Args:
    - plain_password (str): The password input by the user.
    - hashed_password (str): The stored hashed password.

    Returns:
    - bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generates a hashed password.

    Args:
    - password (str): The plain password.

    Returns:
    - str: The hashed password.
    """
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticates the user by verifying the username and password.

    Args:
    - db (Session): The database session.
    - username (str): The username of the user.
    - password (str): The plain password.

    Returns:
    - User: The authenticated user if valid, None otherwise.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Creates an access token for the user.

    Args:
    - data (dict): The data to encode in the JWT token.
    - expires_delta (Optional[timedelta]): The expiration time for the token.

    Returns:
    - str: The encoded JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Retrieves the current user based on the access token.

    Args:
    - token (str): The JWT token.
    - db (Session): The database session.

    Returns:
    - User: The user corresponding to the token's username.

    Raises:
    - HTTPException: If credentials are invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def get_admin_user(current_user: User = Depends(get_current_user)):
    """
    Ensures that the current user is an admin.

    Args:
    - current_user (User): The current authenticated user.

    Returns:
    - User: The current admin user.

    Raises:
    - HTTPException: If the user is not an admin.
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can perform this operation"
        )
    return current_user

# Routes
@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Logs the user in and generates an access token.

    Args:
    - form_data (OAuth2PasswordRequestForm): The username and password provided by the user.

    Returns:
    - dict: Contains the access token and its type.
    
    Raises:
    - HTTPException: If the username or password is incorrect.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Creates a new user (admin only).

    Args:
    - user_data (UserCreate): The data for the new user.
    - current_user (User): The currently authenticated admin user.
    - db (Session): The database session.

    Returns:
    - UserResponse: The newly created user.

    Raises:
    - HTTPException: If the username or email already exists, or if the current user is not an admin.
    """
    # Check if username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e
