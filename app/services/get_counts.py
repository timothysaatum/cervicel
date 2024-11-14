from PIL import Image
from typing import List
import torch
from fastapi import UploadFile
from io import BytesIO


async def get_counts_from_model(images: List[UploadFile]):
    from main import model, transform

    aggregated_counts = {
        "SM": 0,
        "KC": 0,
        "EC": 0,
        "EM": 0,
        "AC": 0,
    }  # Initialize counts
    for image_file in images:
        # Read and preprocess the image
        image = Image.open(BytesIO(await image_file.read())).convert("RGB")
        image_tensor = transform(image).unsqueeze(0)  # Add batch dimension

        # Pass image to the model and get predictions
        with torch.no_grad():
            output = model(image_tensor)

        # Assuming model returns counts as a dictionary with keys matching cell types
        image_counts = {
            "SM": int(output[0].item()),  # Squamous Metaplastic Cells
            "KC": int(output[1].item()),  # Koilocytes
            "EC": int(output[2].item()),  # Endocervical Cells
            "EM": int(output[3].item()),  # Endometrial Cells
            "AC": int(output[4].item()),  # Atypical Cells
        }

        # Aggregate counts across images
        for key in aggregated_counts:
            aggregated_counts[key] += image_counts.get(key, 0)

    return aggregated_counts
