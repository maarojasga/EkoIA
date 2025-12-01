from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import sys
from typing import Optional

# Agregar paths
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.config import DATA_FILE, MODEL_FILE, LAND_USE_MODEL_PATH

from app.schemas import (
    PredictionInput, PredictionOutput, BatchPredictionInput, BatchPredictionOutput,
    GeneralStatsResponse, CategorySummaryResponse, RegionStatsResponse, CategoryStatsResponse,
    TimeSeriesResponse, TopEmittersResponse, ModelInfoResponse,
    FeatureImportanceResponse, AvailableOptionsResponse, DashboardDataResponse,
    EmissionsByUnitResponse, LandUsePredictionInput, LandUsePredictionOutput,
    LandUseAnalysisResponse, MergeDatasetRequest, LandUseModelTrainRequest,
    LandUseModelTrainResponse
)
from models.prediction_model import CO2PredictionModel
from models.land_use_model import LandUseCO2Model
from utils.data_analysis import CO2DataAnalyzer

# Inicializar FastAPI
app = FastAPI(
    title="CO2 Emissions Microservice",
    description="Microservicio para análisis y predicción de emisiones de CO2 con integración de uso de suelo",
    version="2.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales
DATA_PATH = str(DATA_FILE)
LAND_USE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "land_use.csv")
MODEL_PATH = str(MODEL_FILE)
LAND_USE_MODEL_PATH = str(LAND_USE_MODEL_PATH)

analyzer = None
prediction_model = CO2PredictionModel()
land_use_model = LandUseCO2Model()
merged_df = None


@app.on_event("startup")
async def startup_event():
    """Inicializa el servicio al arrancar"""
    global analyzer, prediction_model, land_use_model, merged_df
    
    # Cargar datos de CO2 si existen
    if os.path.exists(DATA_PATH):
        try:
            # Detectar tipo de archivo y cargar apropiadamente
            if DATA_PATH.endswith('.csv'):
                df = pd.read_csv(DATA_PATH, low_memory=False)
            elif DATA_PATH.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(DATA_PATH)
            else:
                raise ValueError(f"Formato de archivo no soportado: {DATA_PATH}")
            
            analyzer = CO2DataAnalyzer(df)
            print(f"✓ Datos de CO2 cargados: {len(df)} registros")
        except Exception as e:
            print(f"⚠ Error cargando datos de CO2: {e}")
    
    # Cargar modelo de predicción si existe
    if os.path.exists(MODEL_PATH):
        try:
            prediction_model.load_model(MODEL_PATH)
            print(f"✓ Modelo de predicción cargado desde {MODEL_PATH}")
        except Exception as e:
            print(f"⚠ Error cargando modelo de predicción: {e}")
    
    # Cargar modelo de uso de suelo si existe
    if os.path.exists(LAND_USE_MODEL_PATH):
        try:
            land_use_model.load_model(LAND_USE_MODEL_PATH)
            print(f"✓ Modelo de uso de suelo cargado desde {LAND_USE_MODEL_PATH}")
        except Exception as e:
            print(f"⚠ Error cargando modelo de uso de suelo: {e}")


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "CO2 Emissions Microservice v2.0",
        "version": "2.0.0",
        "features": [
            "Análisis estadístico de emisiones CO2",
            "Filtros por año, región y categoría",
            "Predicción de emisiones",
            "Integración con datos de uso de suelo",
            "Dashboard con visualizaciones"
        ],
        "endpoints": {
            "stats": "/stats/*",
            "dashboard": "/dashboard/*",
            "predictions": "/predict/*",
            "land_use": "/land-use/*",
            "model": "/model/*",
            "docs": "/docs"
        }
    }


# ===============================
# ENDPOINTS DE ESTADÍSTICAS
# ===============================

@app.get("/stats/general", response_model=GeneralStatsResponse)
async def get_general_stats(
    year: Optional[int] = Query(None, description="Filtrar por año específico"),
    region: Optional[str] = Query(None, description="Filtrar por región"),
    category_type: Optional[str] = Query(None, description="Filtrar por tipo de categoría")
):
    """Obtiene estadísticas generales del dataset con filtros opcionales"""
    if analyzer is None:
        raise HTTPException(status_code=503, detail="Datos no cargados")
    
    try:
        stats = analyzer.get_general_stats(year=year, region=region, category_type=category_type)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")


@app.get("/stats/category-summary", response_model=CategorySummaryResponse)
async def get_category_summary():
    """Obtiene resumen de categorías de emisión"""
    if analyzer is None:
        raise HTTPException(status_code=503, detail="Datos no cargados")
    
    try:
        summary = analyzer.get_category_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo resumen: {str(e)}")


@app.get("/stats/regions", response_model=RegionStatsResponse)
async def get_region_stats(
    year: Optional[int] = Query(None, description="Filtrar por año"),
    category_type: Optional[str] = Query(None, description="Tipo de categoría")
):
    """Obtiene estadísticas de CO2 por región"""
    if analyzer is None:
        raise HTTPException(status_code=503, detail="Datos no cargados")
    
    try:
        stats = analyzer.get_stats_by_region(year=year, category_type=category_type)
        return {"stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")


@app.get("/stats/categories", response_model=CategoryStatsResponse)
async def get_category_stats(
    year: Optional[int] = Query(None, description="Filtrar por año"),
    region: Optional[str] = Query(None, description="Filtrar por región")
):
    """Obtiene estadísticas de CO2 por categoría"""
    if analyzer is None:
        raise HTTPException(status_code=503, detail="Datos no cargados")
    
    try:
        stats = analyzer.get_stats_by_category(year=year, region=region)
        return {"stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")


@app.get("/stats/region-category")
async def get_region_category_stats(
    year: Optional[int] = Query(None, description="Filtrar por año")
):
    """Obtiene estadísticas por combinación región-categoría"""
    if analyzer is None:
        raise HTTPException(status_code=503, detail="Datos no cargados")
    
    try:
        stats = analyzer.get_stats_by_region_category(year=year)
        return {"stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")


@app.get("/stats/time-series", response_model=TimeSeriesResponse)
async def get_time_series(
    region: Optional[str] = Query(None, description="Filtrar por región"),
    category_type: Optional[str] = Query(None, description="Tipo de categoría")
):
    """Obtiene serie temporal de CO2"""
    if analyzer is None:
        raise HTTPException(status_code=503, detail="Datos no cargados")
    
    try:
        time_series = analyzer.get_time_series_by_region(region=region, category_type=category_type)
        return {"time_series": time_series, "region": region, "category_type": category_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo serie temporal: {str(e)}")


@app.get("/stats/top-emitters", response_model=TopEmittersResponse)
async def get_top_emitters(
    n: int = Query(10, description="Número de emisores a retornar"),
    by: str = Query("REGION", description="Agrupar por"),
    year: Optional[int] = Query(None, description="Filtrar por año"),
    category_type: Optional[str] = Query(None, description="Tipo de categoría")
):
    """Obtiene los mayores emisores de CO2"""
    if analyzer is None:
        raise HTTPException(status_code=503, detail="Datos no cargados")
    
    try:
        top_emitters = analyzer.get_top_emitters(n=n, by=by, year=year, category_type=category_type)
        return {"top_emitters": top_emitters, "by": by, "n": n}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo emisores: {str(e)}")


@app.get("/stats/emissions-by-unit", response_model=EmissionsByUnitResponse)
async def get_emissions_by_unit(
    region: Optional[str] = Query(None, description="Filtrar por región"),
    year: Optional[int] = Query(None, description="Filtrar por año"),
    category_type: str = Query("aire_emisiones", description="Tipo de categoría")
):
    """Obtiene emisiones agrupadas por tipo de unidad y región"""
    if analyzer is None:
        raise HTTPException(status_code=503, detail="Datos no cargados")
    
    try:
        emissions = analyzer.get_emissions_by_unit_type(
            region=region, year=year, category_type=category_type
        )
        return {
            "emissions": emissions,
            "region": region,
            "year": year,
            "category_type": category_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo emisiones: {str(e)}")


@app.get("/stats/available-options", response_model=AvailableOptionsResponse)
async def get_available_options():
    """Obtiene regiones, categorías y años disponibles"""
    if analyzer is None:
        raise HTTPException(status_code=503, detail="Datos no cargados")
    
    try:
        return {
            "regions": analyzer.get_available_regions(),
            "categories": analyzer.get_available_categories(),
            "years": analyzer.get_available_years(),
            "category_types": ["aire_emisiones", "bosque_captura", "causas_factores"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo opciones: {str(e)}")


# ===============================
# DASHBOARD
# ===============================

@app.get("/dashboard/data", response_model=DashboardDataResponse)
async def get_dashboard_data(
    year: Optional[int] = Query(None, description="Filtrar por año"),
    region: Optional[str] = Query(None, description="Filtrar por región"),
    category_type: Optional[str] = Query(None, description="Tipo de categoría")
):
    """Obtiene todos los datos necesarios para el dashboard"""
    if analyzer is None:
        raise HTTPException(status_code=503, detail="Datos no cargados")
    
    try:
        data = analyzer.get_dashboard_data(year=year, region=region, category_type=category_type)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo datos del dashboard: {str(e)}")


# ===============================
# ENDPOINTS DE PREDICCIÓN
# ===============================

@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: PredictionInput):
    """Realiza predicción de CO2 para datos de entrada"""
    if prediction_model.model is None:
        raise HTTPException(status_code=503, detail="Modelo no entrenado")
    
    try:
        prediction = prediction_model.predict(input_data.dict())
        
        return {
            "predicted_co2": prediction,
            "input_data": input_data,
            "model_metrics": prediction_model.metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")


@app.post("/predict/batch", response_model=BatchPredictionOutput)
async def predict_batch(input_data: BatchPredictionInput):
    """Realiza predicciones por lote"""
    if prediction_model.model is None:
        raise HTTPException(status_code=503, detail="Modelo no entrenado")
    
    try:
        results = []
        for item in input_data.predictions:
            prediction = prediction_model.predict(item.dict())
            results.append({
                "input": item.dict(),
                "predicted_co2": prediction
            })
        
        return {
            "results": results,
            "total_predictions": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción por lote: {str(e)}")


# ===============================
# LAND USE MODEL ENDPOINTS
# ===============================

@app.post("/land-use/merge")
async def merge_land_use_data(request: MergeDatasetRequest):
    """Combina datasets de CO2 y uso de suelo"""
    global merged_df, analyzer
    
    if analyzer is None:
        raise HTTPException(status_code=503, detail="Datos de CO2 no cargados")
    
    try:
        # Cargar datos de uso de suelo
        land_use_path = request.land_use_data_path or LAND_USE_PATH
        if not os.path.exists(land_use_path):
            raise HTTPException(status_code=404, detail=f"Archivo de uso de suelo no encontrado: {land_use_path}")
        
        land_use_df = pd.read_csv(land_use_path, low_memory=False)
        
        # Realizar merge
        merged_df = land_use_model.merge_datasets(
            analyzer.df,
            land_use_df,
            on=request.merge_columns
        )
        
        return {
            "message": "Datasets combinados exitosamente",
            "total_records": len(merged_df),
            "merge_columns": request.merge_columns,
            "co2_records": len(analyzer.df),
            "land_use_records": len(land_use_df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error combinando datasets: {str(e)}")


@app.post("/land-use/train", response_model=LandUseModelTrainResponse)
async def train_land_use_model(request: LandUseModelTrainRequest):
    """Entrena modelo de predicción con datos de uso de suelo"""
    global land_use_model, merged_df
    
    if merged_df is None:
        raise HTTPException(
            status_code=400, 
            detail="Primero debe combinar los datasets usando /land-use/merge"
        )
    
    try:
        # Entrenar modelo
        metrics = land_use_model.train(
            merged_df,
            co2_column=request.co2_column,
            land_use_columns=request.land_use_columns,
            model_type=request.model_type,
            test_size=request.test_size,
            n_estimators=request.n_estimators
        )
        
        # Obtener importancia de features
        feature_importance = None
        if request.model_type in ['random_forest', 'gradient_boosting']:
            try:
                feature_importance = land_use_model.get_feature_importance(top_n=15)
            except:
                pass
        
        # Guardar modelo
        os.makedirs(os.path.dirname(LAND_USE_MODEL_PATH), exist_ok=True)
        land_use_model.save_model(LAND_USE_MODEL_PATH)
        
        return {
            "message": "Modelo de uso de suelo entrenado exitosamente",
            "metrics": metrics,
            "feature_importance": feature_importance,
            "model_saved": LAND_USE_MODEL_PATH
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error entrenando modelo: {str(e)}")


@app.post("/land-use/predict", response_model=LandUsePredictionOutput)
async def predict_with_land_use(input_data: LandUsePredictionInput):
    """Realiza predicción considerando datos de uso de suelo"""
    if land_use_model.model is None:
        raise HTTPException(status_code=503, detail="Modelo de uso de suelo no entrenado")
    
    try:
        # Combinar datos de entrada
        combined_input = {
            "ANO": input_data.ANO,
            "REGION": input_data.REGION,
            **input_data.land_use_data
        }
        
        if input_data.CATEGORIA:
            combined_input["CATEGORIA"] = input_data.CATEGORIA
        if input_data.S is not None:
            combined_input["S"] = input_data.S
        if input_data.SB1 is not None:
            combined_input["SB1"] = input_data.SB1
        
        # Predecir
        prediction = land_use_model.predict(combined_input)
        
        return {
            "predicted_co2": prediction,
            "input_data": combined_input,
            "model_metrics": land_use_model.metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")


@app.get("/land-use/analysis", response_model=LandUseAnalysisResponse)
async def analyze_land_use_impact():
    """Analiza el impacto de diferentes tipos de uso de suelo en las emisiones"""
    global merged_df
    
    if merged_df is None:
        raise HTTPException(
            status_code=400,
            detail="Primero debe combinar los datasets usando /land-use/merge"
        )
    
    try:
        # Identificar columnas de uso de suelo
        land_use_cols = [col for col in merged_df.columns 
                        if any(keyword in col.lower() 
                             for keyword in ['uso', 'suelo', 'land', 'use', 'hectarea', 'area'])]
        
        analysis = land_use_model.analyze_land_use_impact(
            merged_df,
            land_use_columns=land_use_cols,
            co2_column='VALOR_F'
        )
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis: {str(e)}")


# ===============================
# ENDPOINTS DEL MODELO
# ===============================

@app.get("/model/info", response_model=ModelInfoResponse)
async def get_model_info():
    """Obtiene información del modelo de predicción"""
    try:
        info = prediction_model.get_model_info()
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo info del modelo: {str(e)}")


@app.get("/model/land-use/info")
async def get_land_use_model_info():
    """Obtiene información del modelo de uso de suelo"""
    if land_use_model.model is None:
        return {"status": "not_trained"}
    
    try:
        importance = None
        if hasattr(land_use_model.model, 'feature_importances_'):
            importance = land_use_model.get_feature_importance(top_n=10)
        
        return {
            "status": "trained",
            "model_type": land_use_model.metrics.get('model_type', 'unknown'),
            "metrics": land_use_model.metrics,
            "n_features": len(land_use_model.feature_columns) if land_use_model.feature_columns else 0,
            "feature_importance": importance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo info del modelo: {str(e)}")


@app.get("/model/feature-importance", response_model=FeatureImportanceResponse)
async def get_feature_importance(top_n: int = Query(10, description="Número de features")):
    """Obtiene importancia de características del modelo de predicción"""
    if prediction_model.model is None:
        raise HTTPException(status_code=503, detail="Modelo no entrenado")
    
    try:
        importance = prediction_model.get_feature_importance(top_n=top_n)
        return {"feature_importance": importance, "top_n": top_n}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo importancia: {str(e)}")


@app.post("/model/train")
async def train_model(
    test_size: float = Query(0.2, description="Proporción de test"),
    n_estimators: int = Query(100, description="Número de estimadores")
):
    """Entrena el modelo de predicción con los datos cargados"""
    if analyzer is None:
        raise HTTPException(status_code=503, detail="Datos no cargados")
    
    try:
        # Entrenar modelo
        metrics = prediction_model.train(
            analyzer.df,
            test_size=test_size,
            n_estimators=n_estimators
        )
        
        # Guardar modelo
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        prediction_model.save_model(MODEL_PATH)
        
        return {
            "message": "Modelo entrenado exitosamente",
            "metrics": metrics,
            "model_saved": MODEL_PATH
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error entrenando modelo: {str(e)}")


# ===============================
# DATA UPLOAD
# ===============================

@app.post("/data/upload")
async def upload_data(
    file: UploadFile = File(...),
    data_type: str = Query("co2", description="Tipo de datos: 'co2' o 'land_use'")
):
    """Sube y carga un nuevo archivo CSV o Excel de datos"""
    global analyzer, merged_df
    
    # Validar extensión de archivo
    allowed_extensions = ['.csv', '.xlsx', '.xls']
    if not any(file.filename.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=400, 
            detail=f"Solo se permiten archivos CSV o Excel ({', '.join(allowed_extensions)})"
        )
    
    try:
        # Determinar ruta según tipo de datos
        if data_type == "co2":
            # Mantener la extensión original del archivo
            file_ext = os.path.splitext(file.filename)[1]
            save_path = DATA_PATH.replace('.csv', file_ext)
        elif data_type == "land_use":
            file_ext = os.path.splitext(file.filename)[1]
            save_path = LAND_USE_PATH.replace('.csv', file_ext)
        else:
            raise HTTPException(status_code=400, detail="data_type debe ser 'co2' o 'land_use'")
        
        # Guardar archivo
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        contents = await file.read()
        with open(save_path, 'wb') as f:
            f.write(contents)
        
        # Cargar datos según el tipo de archivo
        if save_path.endswith('.csv'):
            df = pd.read_csv(save_path, low_memory=False)
        elif save_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(save_path)
        else:
            raise HTTPException(status_code=400, detail="Formato de archivo no soportado")
        
        # Si son datos de CO2, actualizar analyzer
        if data_type == "co2":
            analyzer = CO2DataAnalyzer(df)
            # Resetear merged_df si existía
            merged_df = None
        
        return {
            "message": f"Datos de {data_type} cargados exitosamente",
            "filename": file.filename,
            "records": len(df),
            "columns": len(df.columns),
            "data_type": data_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cargando datos: {str(e)}")


# Health check
@app.get("/health")
async def health_check():
    """Verifica el estado del servicio"""
    return {
        "status": "healthy",
        "data_loaded": analyzer is not None,
        "prediction_model_loaded": prediction_model.model is not None,
        "land_use_model_loaded": land_use_model.model is not None,
        "merged_data_available": merged_df is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)