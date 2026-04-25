import logging
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import router
from config import settings

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(title="Resume Screener API")

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

app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=False)

# Initializes the FastAPI application with CORS middleware, registers the screening router under /api/v1, exposes a /health endpoint, and starts the uvicorn server when run directly.
