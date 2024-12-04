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

router = APIRouter(prefix="/auth", tags=["authentication"])

class Auth:
    """
    This class handles authentication-related routes and user management.
    It includes user registration, login, token generation, and user validation.

    Endpoints:
    - POST /auth/token: Authenticates a user and returns an access token.
    - POST /auth/users: Registers a new user with specified role (admin or case_worker).
    """

    # Configuration
    SECRET_KEY = "your-secret-key-here"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

    class UserCreate(BaseModel):
        """
        Schema for creating a new user. This includes fields for username, email, password, and role.
        """
        username: str = Field(..., min_length=3, max_length=50)
        email: str
        password: str
        role: UserRole

        @validator('role')
        def validate_role(self, v):
            """
            Validates that the user's role is either 'admin' or 'case_worker'.
            """
            if v not in [UserRole.admin, UserRole.case_worker]:
                raise ValueError('Role must be either admin or case_worker')
            return v

    class UserResponse(BaseModel):
        """
        Response schema for user details. Used when returning user information after registration or login.
        """
        username: str
        email: str
        role: UserRole

        class Config:
            from_attributes = True

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifies if a plain password matches the hashed password.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """
        Hashes a plain password using bcrypt.
        """
        return self.pwd_context.hash(password)

    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """
        Authenticates a user by verifying their username and password.
        """
        user = db.query(User).filter(User.username == username).first()
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """
        Creates an access token with a specified expiration time.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
        """
        Retrieves the current user based on the provided JWT token.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise credentials_exception
        return user

    def get_admin_user(self, current_user: User = Depends(get_current_user)):
        """
        Ensures that the current user has an 'admin' role.
        """
        if current_user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin users can perform this operation"
            )
        return current_user

    @router.post("/token")
    async def login_for_access_token(self, form_data: OAuth2PasswordRequestForm = Depends(),
                                     db: Session = Depends(get_db)):
        """
        Logs in a user and returns an access token.
        """
        user = self.authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    @router.post("/users", response_model=UserResponse)
    async def create_user(self, user_data: UserCreate, db: Session = Depends(get_db)):
        """
        Creates a new user (admin only).
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
            hashed_password=self.get_password_hash(user_data.password),
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
            )
