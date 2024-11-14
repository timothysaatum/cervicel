from fastapi import FastAPI
from api.endpoints import report
import torch
import torchvision.transforms as T
import torchvision


model_path = r"https://drive.google.com/file/d/1BXpnQ_njm-xFtIBHtd3YgSBQUEfCn50W/view"  # r"services\best2a_pap_combined_model.pth"

app = FastAPI()
device = torch.device("cuda") if torch.cuda.is_available() else "cpu"
class_names = [
    "background",
    "superficial",
    "intermediate",
    "parabasal",
    "koilocyte",
    "endocervical",
    "endometrial",
    "squamous metaplastic",
    "actinomyces",
]
model = torchvision.models.detection.maskrcnn_resnet50_fpn(
    pretrained=False, num_classes=len(class_names), weights=None
)
model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
model.to(device)
model.eval()

# Define image transformations
transform = T.Compose([T.ToTensor()])

# Include the report router
app.include_router(report.router, prefix="/generate-report")
