from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class PredictionInput(BaseModel):
    """Modelo de entrada para predicción"""
    ANO: float = Field(..., description="Año", example=2023.0)
    S: float = Field(..., description="Sector S", example=1.0)
    SB1: float = Field(..., description="Subsector SB1", example=1.0)
    REGION: str = Field(..., description="Región", example="AMAZONIA")
    CATEGORIA: str = Field(..., description="Categoría", example="4.B. Tierras de cultivo")


class PredictionOutput(BaseModel):
    """Modelo de salida para predicción"""
    predicted_co2: float = Field(..., description="Concentración de CO2 predicha en kg CO2/TJ")
    input_data: PredictionInput
    model_metrics: Optional[Dict[str, float]] = None


class BatchPredictionInput(BaseModel):
    """Modelo para predicción por lotes"""
    predictions: List[PredictionInput]


class BatchPredictionOutput(BaseModel):
    """Modelo de salida para predicción por lotes"""
    results: List[Dict[str, Any]]
    total_predictions: int


class GeneralStatsResponse(BaseModel):
    """Modelo para estadísticas generales"""
    total_records: int
    total_columns: int
    columns: List[str]
    date_range: Dict[str, Optional[float]]
    co2_stats: Dict[str, Optional[float]]
    missing_values: Dict[str, Any]


class RegionStatsResponse(BaseModel):
    """Modelo para estadísticas por región"""
    stats: List[Dict[str, Any]]


class CategoryStatsResponse(BaseModel):
    """Modelo para estadísticas por categoría"""
    stats: List[Dict[str, Any]]


class TimeSeriesResponse(BaseModel):
    """Modelo para series temporales"""
    time_series: List[Dict[str, Any]]
    region: Optional[str] = None


class TopEmittersResponse(BaseModel):
    """Modelo para mayores emisores"""
    top_emitters: List[Dict[str, Any]]
    by: str
    n: int


class ModelInfoResponse(BaseModel):
    """Modelo para información del modelo"""
    status: str
    model_type: Optional[str] = None
    n_estimators: Optional[int] = None
    metrics: Optional[Dict[str, float]] = None
    n_features: Optional[int] = None
    feature_names: Optional[List[str]] = None


class FeatureImportanceResponse(BaseModel):
    """Modelo para importancia de características"""
    feature_importance: List[Dict[str, Any]]
    top_n: int


class AvailableOptionsResponse(BaseModel):
    """Modelo para opciones disponibles"""
    regions: List[str]
    categories: List[str]