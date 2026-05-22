import sys
import asyncio

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import engine
from backend.routers import analysis, export

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Full-stack AI-powered competitor intelligence scraping & analysis pipeline.",
    version="1.0.0"
)

# Configure CORS for local development (React dev server on port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include endpoint routers
app.include_router(analysis.router)
app.include_router(export.router)

@app.on_event("startup")
async def on_startup():
    """Initializes SQLite database tables on startup if they don't exist."""
    # Ensure tables are created asynchronously
    from backend.models import Base
    from sqlalchemy import text
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Handle schema evolution: add job_type column if missing
        try:
            await conn.execute(text("ALTER TABLE analysis_jobs ADD COLUMN job_type VARCHAR DEFAULT 'analyze'"))
            print("[MIGRATION] Added job_type column to analysis_jobs table.")
        except Exception:
            pass
    print("[OK] SQLite database tables initialized successfully.")

@app.get("/")
def read_root():
    return {
        "app": settings.PROJECT_NAME,
        "status": "online",
        "api_docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
