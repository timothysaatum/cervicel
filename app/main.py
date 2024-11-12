from fastapi import FastAPI
from app.api.endpoints import report

app = FastAPI()

# Include the report router
app.include_router(report.router, prefix="/generate-report")
