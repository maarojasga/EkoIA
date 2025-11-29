import pytest
import numpy as np
from models.prediction_model import PredictionModel
import os

@pytest.fixture
def model():
    # Use a temporary file for testing
    model = PredictionModel(model_path="test_model.joblib")
    yield model
    # Cleanup
    if os.path.exists("test_model.joblib"):
        os.remove("test_model.joblib")

def test_model_initialization(model):
    assert model.model is not None
    assert model.is_trained == False

def test_model_training(model):
    X = [[1, 1], [2, 2], [3, 3], [4, 4], [5, 5]]
    y = [2, 4, 6, 8, 10]
    
    metrics = model.train(X, y)
    
    assert model.is_trained == True
    assert "mse" in metrics
    assert "r2_score" in metrics
    assert metrics["r2_score"] > 0.9  # Should be perfect linear relationship

def test_model_prediction(model):
    X = [[1, 1], [2, 2], [3, 3], [4, 4], [5, 5]]
    y = [2, 4, 6, 8, 10]
    model.train(X, y)
    
    preds = model.predict([[6, 6]])
    assert len(preds) == 1
    assert abs(preds[0] - 12) < 0.001

def test_predict_without_training(model):
    with pytest.raises(ValueError):
        model.predict([[1, 1]])
