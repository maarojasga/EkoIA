from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# ========================================
# PREDICCIÓN DE CO2
# ========================================

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


# ========================================
# ESTADÍSTICAS GENERALES
# ========================================

class GeneralStatsResponse(BaseModel):
    """Modelo para estadísticas generales"""
    total_records: int
    total_columns: int
    columns: List[str]
    date_range: Dict[str, Optional[float]]
    co2_stats: Dict[str, Optional[float]]
    missing_values: Dict[str, Any]
    filters_applied: Optional[Dict[str, Any]] = None


class CategorySummaryResponse(BaseModel):
    """Modelo para resumen de categorías de emisión"""
    aire_emisiones: Dict[str, Any]
    bosque_captura: Dict[str, Any]
    causas_factores: Dict[str, Any]


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
    category_type: Optional[str] = None


class TopEmittersResponse(BaseModel):
    """Modelo para mayores emisores"""
    top_emitters: List[Dict[str, Any]]
    by: str
    n: int


class EmissionsByUnitResponse(BaseModel):
    """Modelo para emisiones por tipo de unidad"""
    emissions: List[Dict[str, Any]]
    region: Optional[str] = None
    year: Optional[int] = None
    category_type: str


# ========================================
# DASHBOARD
# ========================================

class DashboardDataResponse(BaseModel):
    """Modelo para datos consolidados de dashboard"""
    general_stats: Dict[str, Any]
    category_summary: Dict[str, Any]
    region_stats: List[Dict[str, Any]]
    category_stats: List[Dict[str, Any]]
    time_series: List[Dict[str, Any]]
    top_emitters: List[Dict[str, Any]]
    emissions_by_unit: List[Dict[str, Any]]
    available_filters: Dict[str, Any]


# ========================================
# MODELO ML
# ========================================

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
    years: List[int]
    category_types: List[str]


# ========================================
# LAND USE MODEL
# ========================================

class LandUsePredictionInput(BaseModel):
    """Entrada para predicción con datos de uso de suelo"""
    ANO: float = Field(..., description="Año")
    REGION: str = Field(..., description="Región")
    CATEGORIA: Optional[str] = Field(None, description="Categoría")
    S: Optional[float] = Field(None, description="Sector")
    SB1: Optional[float] = Field(None, description="Subsector")
    land_use_data: Dict[str, float] = Field(..., description="Datos de uso de suelo por tipo")


class LandUsePredictionOutput(BaseModel):
    """Salida para predicción con uso de suelo"""
    predicted_co2: float
    input_data: Dict[str, Any]
    model_metrics: Optional[Dict[str, float]] = None


class LandUseAnalysisResponse(BaseModel):
    """Respuesta de análisis de impacto de uso de suelo"""
    correlations: Dict[str, float]
    top_positive_impact: List[Dict[str, Any]]
    top_negative_impact: List[Dict[str, Any]]


class MergeDatasetRequest(BaseModel):
    """Request para merge de datasets"""
    co2_data_path: Optional[str] = None
    land_use_data_path: Optional[str] = None
    merge_columns: List[str] = Field(default=['ANO', 'REGION'], description="Columnas para merge")


class LandUseModelTrainRequest(BaseModel):
    """Request para entrenar modelo de uso de suelo"""
    co2_column: str = Field(default='VALOR_F', description="Columna de emisiones CO2")
    land_use_columns: Optional[List[str]] = None
    model_type: str = Field(default='random_forest', description="Tipo de modelo")
    test_size: float = Field(default=0.2, description="Proporción de datos de prueba")
    n_estimators: Optional[int] = Field(default=100, description="Número de estimadores (para RF/GB)")


class LandUseModelTrainResponse(BaseModel):
    """Respuesta de entrenamiento del modelo de uso de suelo"""
    message: str
    metrics: Dict[str, float]
    feature_importance: Optional[List[Dict[str, Any]]] = None
    model_saved: Optional[str] = None