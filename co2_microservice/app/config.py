"""
Configuración de la aplicación
"""
import os
from pathlib import Path

# Directorios base
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

# Rutas de archivos
DATA_FILE = DATA_DIR / "factores_limpios.csv"
MODEL_FILE = MODELS_DIR / "co2_model.pkl"

# Configuración del modelo
MODEL_CONFIG = {
    "n_estimators": 100,
    "random_state": 42,
    "test_size": 0.2,
}

# Configuración de la API
API_CONFIG = {
    "title": "CO2 Emissions Microservice",
    "description": "Microservicio para análisis y predicción de emisiones de CO2",
    "version": "1.0.0",
    "host": "0.0.0.0",
    "port": 8000,
}

# Características del modelo
NUMERIC_FEATURES = ["ANO", "S", "SB1"]
CATEGORICAL_FEATURES = ["REGION", "CATEGORIA"]
TARGET_COLUMN = "VALOR_F"

# Crear directorios si no existen
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)