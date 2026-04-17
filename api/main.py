import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import router
from config import settings

# Configure logging at root level
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(title="Resume Screener API")

# Configure CORS Middleware (allowing all origins for dev mode)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Resume Screener API started")

# Include business logic router cleanly prefixed
app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    # Start up the application utilizing uvicorn with module string for hot reloading
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
