from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "CO2 Microservice is running"}

def test_add_data():
    data = {
        "timestamp": "2023-10-27T10:00:00",
        "co2_level": 500.0,
        "temperature": 25.0,
        "humidity": 40.0,
        "occupancy": 5
    }
    response = client.post("/data", json=data)
    assert response.status_code == 201
    assert response.json()["co2_level"] == 500.0

def test_get_stats_empty():
    # Clear data first
    client.delete("/data")
    response = client.get("/analysis/stats")
    assert response.status_code == 200
    assert response.json() == {}

def test_prediction_flow():
    # Add enough data for training
    for i in range(10):
        data = {
            "timestamp": "2023-10-27T10:00:00",
            "co2_level": 400.0 + i * 10,
            "temperature": 20.0 + i,
            "humidity": 40.0,
            "occupancy": i
        }
        client.post("/data", json=data)
    
    # Train
    train_resp = client.post("/model/train")
    assert train_resp.status_code == 200
    
    # Predict
    pred_req = {
        "features": [[25.0, 40.0, 5]]
    }
    pred_resp = client.post("/predict", json=pred_req)
    assert pred_resp.status_code == 200
    assert "predictions" in pred_resp.json()
