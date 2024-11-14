from fastapi import FastAPI
from api.endpoints import report
import torch
from torchvision import transforms


model_path = r"services\best2a_pap_combined_model.pth"

app = FastAPI()


model = torch.load(model_path, map_location=torch.device("cpu"), weights_only=True)
model.eval()

# Define image transformations
transform = transforms.Compose(
    [
        transforms.Resize(
            (224, 224)
        ),  # Adjust size according to model's input requirements
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)

# Include the report router
app.include_router(report.router, prefix="/generate-report")
