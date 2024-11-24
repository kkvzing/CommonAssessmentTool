"""
Main application module for the Common Assessment Tool.
This module initializes the FastAPI application and includes all routers.
Handles database initialization and CORS middleware configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Local application imports
from app.clients.router import router as clients_router
from app.database import engine
from app import models

# Initialize database tables
models.Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title="Case Management API",
    description="API for managing client cases and predictions",
    version="1.0.0"
)

# Include routers
app.include_router(clients_router)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # Allows all origins
    allow_methods=["*"],     # Allows all methods
    allow_headers=["*"],     # Allows all headers
    allow_credentials=True,
)
