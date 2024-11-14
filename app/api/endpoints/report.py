from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from typing import List
from models.schemas import ReportParameters, ReportResponse
from services.pap_analytics import generate_report
from services.get_counts import get_counts_from_model


router = APIRouter()


@router.post("/", response_model=ReportResponse)
async def generate_report_endpoint(
    params: ReportParameters = Depends(), images: List[UploadFile] = File(...)
):
    if len(images) >= 10:
        raise HTTPException(status_code=400, detail="Exactly 10 or less images are required.")

    image_data = [await image.read() for image in images]
    counts = get_counts_from_model(image_data)
    report = generate_report(
        counts=counts,
        age_in_days=params.age,
        lmp_date=params.lmp_date,
        condition=params.condition,
    )

    return report
