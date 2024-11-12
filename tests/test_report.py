from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_generate_report():
    params = {"age": 25, "lmp_date": "2023-09-01", "condition": "none"}
    files = [("images", ("image.jpg", b"dummy_image_data", "image/jpeg"))] * 10
    response = client.post("/report/", params=params, files=files)
    assert response.status_code == 200
    assert response.json()["summary"] == "Report based on image analysis"
