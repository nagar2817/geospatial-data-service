from fastapi import APIRouter
from api.routers import job

"""
Main API Router

This module combines all endpoint routers into a single main router.
Each functional area has its own router module for better organization.
"""

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include all sub-routers
api_router.include_router(job.router)
# api_router.include_router(alert.router)

# Health check endpoint
@api_router.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "geospatial-data-service",
        "version": "1.0.0"
    }