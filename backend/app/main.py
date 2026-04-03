"""FastAPI main application"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import time

from app.config import settings
from app.database import close_db
from app.api.v1 import health, projects, scans, findings, websocket, auth

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info("Starting up eidosSec backend...")
    settings.validate_secrets()
    yield
    # Shutdown
    logger.info("Shutting down...")
    await close_db()

# Create FastAPI application
app = FastAPI(
    title="eidosSec API",
    version="0.1.0",
    description="AI-powered security scanner with validated baseline profiles and staged stabilization tools",
    lifespan=lifespan
)

# Simple In-memory rate limiting
rate_limit_storage = {}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Only limit /api/v1 endpoints
    if request.url.path.startswith("/api/v1") and not request.url.path.endswith("/health"):
        client_ip = request.client.host
        current_time = time.time()
        
        # Initialize storage for IP
        if client_ip not in rate_limit_storage:
            rate_limit_storage[client_ip] = []
            
        # Clean up old requests (older than 60 seconds)
        rate_limit_storage[client_ip] = [t for t in rate_limit_storage[client_ip] if current_time - t < 60]
        
        # Check limit
        if len(rate_limit_storage[client_ip]) >= settings.RATE_LIMIT_PER_MINUTE:
            raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
            
        # Add current request
        rate_limit_storage[client_ip].append(current_time)
        
    response = await call_next(request)
    return response

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT != "production" else [
        "http://localhost:3000",
        "http://localhost:3009",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(scans.router, prefix="/api/v1")
app.include_router(findings.router, prefix="/api/v1")
app.include_router(websocket.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to eidosSec API",
        "docs": "/docs",
        "version": "0.1.0"
    }

@app.get("/health")
async def root_health():
    """Root health check (redirects to /api/v1/health)"""
    return {"status": "healthy", "message": "Use /api/v1/health for detailed status"}
