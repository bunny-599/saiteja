from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.database import get_db
from backend.models import AnalysisJob
from backend.utils.pdf_generator import create_report_pdf

router = APIRouter(
    prefix="/api/export",
    tags=["export"]
)

@router.get("/pdf/{job_id}")
async def export_report_pdf(job_id: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieves the completed competitor intelligence dataset and
    streams a generated ReportLab PDF download.
    """
    stmt = select(AnalysisJob).where(AnalysisJob.id == job_id)
    result = await db.execute(stmt)
    job = result.scalars().first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Analysis job not found")
        
    if job.status != "complete":
        raise HTTPException(status_code=400, detail="Cannot export PDF. Analysis is not complete yet.")
        
    if not job.result:
        raise HTTPException(status_code=500, detail="No report data found in the completed job record.")
        
    try:
        # Generate the ReportLab PDF buffer
        pdf_buffer = create_report_pdf(job.result)
        
        # Clean company name for the filename
        filename_company = job.company_name.lower().replace(" ", "_")
        filename = f"competitor_report_{filename_company}_{job_id[:8]}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")
