from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.clients.router import router as clients_router

from app.database import engine
from app import models

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# Set API endpoints on router
app.include_router(clients_router)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_methods=["*"],  # Allows all methods, including OPTIONS
    allow_headers=["*"],  # Allows all headers
)


