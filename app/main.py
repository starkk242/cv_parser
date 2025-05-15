import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.config import get_settings
from app.api.routes import router as api_router
from app.core.exceptions import add_exception_handlers

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def create_directories():
    """Create necessary directories for application."""
    settings = get_settings()
    for directory in [settings.UPLOAD_DIR, settings.PARSED_DIR, settings.JD_DIR]:
        Path(directory).mkdir(parents=True, exist_ok=True)
    logger.info("Application directories created")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add exception handlers
    add_exception_handlers(app)
    
    # Include API routes
    app.include_router(api_router)
    
    # Create directories
    create_directories()
    
    @app.get("/", tags=["Health"])
    def health_check():
        """Check if the API is running."""
        return {
            "message": f"{settings.APP_NAME} is running",
            "version": settings.APP_VERSION,
            "status": "healthy"
        }
    
    return app


app = create_application()

if __name__ == "__main__":
    # For development only - use uvicorn to run in production
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)