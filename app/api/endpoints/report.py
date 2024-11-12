from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from typing import List
from app.models.schemas import ReportParameters, ReportResponse
from app.services.report_generator import generate_report

router = APIRouter()

@router.post("/", response_model=ReportResponse)
async def generate_report_endpoint(
    params: ReportParameters = Depends(),
    images: List[UploadFile] = File(...)
):
    if len(images) >= 10:
        raise HTTPException(status_code=400, detail="Exactly 10 or less images are required.")
    
    image_data = [await image.read() for image in images]
    
    report = generate_report(
        image_data=image_data,
        age=params.age,
        lmp_date=params.lmp_date,
        condition=params.condition
    )

    return report
