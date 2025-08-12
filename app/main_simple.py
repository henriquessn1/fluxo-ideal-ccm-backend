from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import async_engine
from app.models import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.APP_ENV == "production" else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application...")
    
    # Create database tables (if needed)
    # async with async_engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    # logger.info("Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")

# Create FastAPI app
app = FastAPI(
    title="Multi-Client Monitoring System",
    description="Sistema de monitoramento multi-cliente com health checks automatizados",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Multi-Client Monitoring System",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_simple:app",
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=settings.APP_ENV == "development"
    )