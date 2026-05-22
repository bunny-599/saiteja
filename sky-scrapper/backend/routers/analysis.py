import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.database import get_db
from backend.models import AnalysisJob
from backend.services.orchestrator import Orchestrator

router = APIRouter(
    prefix="/api",
    tags=["analysis"]
)

# Instantiate orchestrator singleton
orchestrator = Orchestrator()

# Pydantic schemas for request validation
class AnalysisRequest(BaseModel):
    company_name: str = Field(..., example="Tesla", min_length=1)
    industry: str = Field(..., example="Electric Vehicles", min_length=1)
    depth: str = Field("standard", example="standard", description="standard or deep")

class StatusResponse(BaseModel):
    job_id: str
    company_name: str
    industry: str
    status: str
    progress: int
    logs: list
    error_log: str
    created_at: datetime.datetime
    job_type: str = "analyze"

async def submit_job(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    job_type: str,
    db: AsyncSession
):
    # 1. Validate inputs
    depth_val = request.depth.lower()
    if depth_val not in ["standard", "deep"]:
        depth_val = "standard"
        
    job_id = str(uuid.uuid4())
    
    # 2. Create the job record in DB
    new_job = AnalysisJob(
        id=job_id,
        company_name=request.company_name.strip(),
        industry=request.industry.strip(),
        depth=depth_val,
        job_type=job_type,
        status="pending",
        progress=0,
        logs=[],
        error_log=""
    )
    
    db.add(new_job)
    await db.commit()
    
    # 3. Queue the orchestrator background task
    background_tasks.add_task(orchestrator.run_analysis, job_id)
    
    return {"job_id": job_id, "status": "pending"}

@router.post("/analyze", status_code=202)
async def analyze_company(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Submits a new company SWOT & competitor analysis job.
    """
    return await submit_job(request, background_tasks, "analyze", db)

@router.post("/marketing", status_code=202)
async def marketing_company(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Submits a new marketing & advertising intelligence job.
    """
    return await submit_job(request, background_tasks, "marketing", db)

@router.post("/future", status_code=202)
async def future_company(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Submits a new future market gap & strategic opportunity job.
    """
    return await submit_job(request, background_tasks, "future", db)

@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_job_status(job_id: str, db: AsyncSession = Depends(get_db)):
    """
    Returns the current progress, state, and completed logs of the background task.
    Used for frontend progress tracking.
    """
    stmt = select(AnalysisJob).where(AnalysisJob.id == job_id)
    result = await db.execute(stmt)
    job = result.scalars().first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Analysis job not found")
        
    return {
        "job_id": job.id,
        "company_name": job.company_name,
        "industry": job.industry,
        "status": job.status,
        "progress": job.progress,
        "logs": job.logs or [],
        "error_log": job.error_log or "",
        "created_at": job.created_at,
        "job_type": getattr(job, "job_type", "analyze")
    }

@router.get("/report/{job_id}")
async def get_job_report(job_id: str, db: AsyncSession = Depends(get_db)):
    """
    Returns the complete structured JSON report if the analysis job succeeded.
    """
    stmt = select(AnalysisJob).where(AnalysisJob.id == job_id)
    result = await db.execute(stmt)
    job = result.scalars().first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Analysis job not found")
        
    if job.status == "failed":
        raise HTTPException(status_code=400, detail=f"Analysis job failed: {job.error_log}")
        
    if job.status != "complete":
        raise HTTPException(status_code=202, detail="Analysis is still in progress")
        
    return job.result
