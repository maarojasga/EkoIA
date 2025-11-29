from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import sys
from typing import Optional

# Agregar paths
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.schemas import (
    PredictionInput, PredictionOutput, BatchPredictionInput, BatchPredictionOutput,
    GeneralStatsResponse, RegionStatsResponse, CategoryStatsResponse,
    TimeSeriesResponse, TopEmittersResponse, ModelInfoResponse,
    FeatureImportanceResponse, AvailableOptionsResponse
)
from models.prediction_model import CO2PredictionModel
from utils.data_analysis import CO2DataAnalyzer

# Inicializar FastAPI
app = FastAPI(
    title="CO2 Emissions Microservice",
    description="Microservicio para análisis y predicción de emisiones de CO2",
    version="1.0.0"
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
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "factores_limpios.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "co2_model.pkl")

analyzer = None
prediction_model = CO2PredictionModel()


@app.on_event("startup")
async def startup_event():
    """Inicializa el servicio al arrancar"""
    global analyzer, prediction_model
    
    # Cargar datos si existen
    if os.path.exists(DATA_PATH):
        try:
            df = pd.read_csv(DATA_PATH, low_memory=False)
            analyzer = CO2DataAnalyzer(df)
            print(f"✓ Datos cargados: {len(df)} registros")
        except Exception as e:
            print(f"⚠ Error cargando datos: {e}")
    
    # Cargar modelo si existe
    if os.path.exists(MODEL_PATH):
        try:
            prediction_model.load_model(MODEL_PATH)
            print(f"✓ Modelo cargado desde {MODEL_PATH}")
        except Exception as e:
            print(f"⚠ Error cargando modelo: {e}")


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "CO2 Emissions Microservice",
        "version": "1.0.0",
        "endpoints": {
            "stats": "/stats/*",
            "predictions": "/predict/*",
            "model": "/model/*",
            "docs": "/docs"
        }
    }


# ===============================
# ENDPOINTS DE ESTADÍSTICAS
# ===============================

@app.get("/stats/general", response_model=GeneralStatsResponse)
async def get_general_stats():
    """Obtiene estadísticas generales del dataset"""
    if analyzer is None:
        raise HTTPException(status_code=503, detail="Datos no cargados")
    
    try:
        stats = analyzer.get_general_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")


@app.get("/stats/regions", response_model=RegionStatsResponse)
async def get_region_stats():
    """Obtiene estadísticas de CO2 por región"""
    if analyzer is None:
        raise HTTPException(status_code=503, detail="Datos no cargados")
    
    try:
        stats = analyzer.get_stats_by_region()
        return {"stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")


@app.get("/stats/categories", response_model=CategoryStatsResponse)
async def get_category_stats():
    """Obtiene estadísticas de CO2 por categoría"""
    if analyzer is None:
        raise HTTPException(status_code=503, detail="Datos no cargados")
    
    try:
        stats = analyzer.get_stats_by_category()
        return {"stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")


@app.get("/stats/region-category")
async def get_region_category_stats():
    """Obtiene estadísticas por combinación región-categoría"""
    if analyzer is None:
        raise HTTPException(status_code=503, detail="Datos no cargados")
    
    try:
        stats = analyzer.get_stats_by_region_category()
        return {"stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")


@app.get("/stats/time-series", response_model=TimeSeriesResponse)
async def get_time_series(region: Optional[str] = None):
    """Obtiene serie temporal de CO2"""
    if analyzer is None:
        raise HTTPException(status_code=503, detail="Datos no cargados")
    
    try:
        time_series = analyzer.get_time_series_by_region(region)
        return {"time_series": time_series, "region": region}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo serie temporal: {str(e)}")


@app.get("/stats/top-emitters", response_model=TopEmittersResponse)
async def get_top_emitters(n: int = 10, by: str = "REGION"):
    """Obtiene los mayores emisores de CO2"""
    if analyzer is None:
        raise HTTPException(status_code=503, detail="Datos no cargados")
    
    try:
        top_emitters = analyzer.get_top_emitters(n=n, by=by)
        return {"top_emitters": top_emitters, "by": by, "n": n}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo emisores: {str(e)}")


@app.get("/stats/available-options", response_model=AvailableOptionsResponse)
async def get_available_options():
    """Obtiene regiones y categorías disponibles"""
    if analyzer is None:
        raise HTTPException(status_code=503, detail="Datos no cargados")
    
    try:
        regions = analyzer.get_available_regions()
        categories = analyzer.get_available_categories()
        return {"regions": regions, "categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo opciones: {str(e)}")


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
# ENDPOINTS DEL MODELO
# ===============================

@app.get("/model/info", response_model=ModelInfoResponse)
async def get_model_info():
    """Obtiene información del modelo"""
    try:
        info = prediction_model.get_model_info()
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo info del modelo: {str(e)}")


@app.get("/model/feature-importance", response_model=FeatureImportanceResponse)
async def get_feature_importance(top_n: int = 10):
    """Obtiene importancia de características"""
    if prediction_model.model is None:
        raise HTTPException(status_code=503, detail="Modelo no entrenado")
    
    try:
        importance = prediction_model.get_feature_importance(top_n=top_n)
        return {"feature_importance": importance, "top_n": top_n}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo importancia: {str(e)}")


@app.post("/model/train")
async def train_model(test_size: float = 0.2, n_estimators: int = 100):
    """Entrena el modelo con los datos cargados"""
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


@app.post("/data/upload")
async def upload_data(file: UploadFile = File(...)):
    """Sube y carga un nuevo archivo CSV de datos"""
    global analyzer
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV")
    
    try:
        # Guardar archivo
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        
        contents = await file.read()
        with open(DATA_PATH, 'wb') as f:
            f.write(contents)
        
        # Cargar datos
        df = pd.read_csv(DATA_PATH, low_memory=False)
        analyzer = CO2DataAnalyzer(df)
        
        return {
            "message": "Datos cargados exitosamente",
            "filename": file.filename,
            "records": len(df),
            "columns": len(df.columns)
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
        "model_loaded": prediction_model.model is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)