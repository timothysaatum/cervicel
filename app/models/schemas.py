from pydantic import BaseModel, Field
from typing import Optional, List
import datetime

class ReportParameters(BaseModel):
    age: int
    lmp_date: Optional[datetime.date] = None
    condition: Optional[str] = None

class ReportResponse(BaseModel):
    summary: str
    details: dict
