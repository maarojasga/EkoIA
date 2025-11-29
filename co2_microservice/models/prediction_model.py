import pandas as pd
import numpy as np
import pickle
import os
from typing import Dict, Any, List, Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class CO2PredictionModel:
    """Modelo reutilizable para predicción de emisiones CO2"""
    
    def __init__(self, model_path: str = None):
        """
        Inicializa el modelo
        
        Args:
            model_path: Ruta al modelo guardado (opcional)
        """
        self.model = None
        self.ohe = None
        self.feature_columns = None
        self.metrics = {}
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocesa los datos
        
        Args:
            df: DataFrame original
        
        Returns:
            DataFrame preprocesado
        """
        df = df.copy()
        
        # Limpiar columna ANO
        if 'ANO' in df.columns:
            df['ANO'] = df['ANO'].astype(str).str.replace(',', '.').astype(float)
        
        # Limpiar VALOR_F
        if 'VALOR_F' in df.columns:
            df['VALOR_F'] = df['VALOR_F'].astype(str).str.replace(',', '').astype(float)
        
        # Eliminar columna CONTAMINANTE si existe
        if 'CONTAMINANTE' in df.columns:
            df = df.drop(columns=['CONTAMINANTE'])
        
        return df
    
    def train(
        self, 
        df: pd.DataFrame, 
        target_col: str = 'VALOR_F',
        test_size: float = 0.2,
        random_state: int = 42,
        **model_params
    ) -> Dict[str, float]:
        """
        Entrena el modelo con los datos proporcionados
        
        Args:
            df: DataFrame con datos de entrenamiento
            target_col: Nombre de la columna objetivo
            test_size: Proporción del conjunto de prueba
            random_state: Semilla aleatoria
            **model_params: Parámetros adicionales para RandomForestRegressor
        
        Returns:
            Diccionario con métricas de evaluación
        """
        # Preprocesar datos
        df_processed = self._preprocess_data(df)
        
        # Definir características categóricas y numéricas
        categorical_features = ['REGION', 'CATEGORIA']
        
        # Filtrar filas con valores no nulos en características categóricas
        df_filtered = df_processed.dropna(subset=categorical_features + [target_col])
        
        # One-hot encoding para características categóricas
        self.ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        encoded_features = self.ohe.fit_transform(df_filtered[categorical_features])
        encoded_df = pd.DataFrame(
            encoded_features, 
            columns=self.ohe.get_feature_names_out(categorical_features),
            index=df_filtered.index
        )
        
        # Preparar características numéricas
        numeric_features = ['ANO', 'S', 'SB1']
        numeric_features = [f for f in numeric_features if f in df_filtered.columns]
        
        # Combinar características
        X = pd.concat([
            df_filtered[numeric_features].reset_index(drop=True),
            encoded_df.reset_index(drop=True)
        ], axis=1)
        
        y = df_filtered[target_col].values
        
        # Guardar nombres de columnas
        self.feature_columns = X.columns.tolist()
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Entrenar modelo
        if not model_params:
            model_params = {'n_estimators': 100, 'random_state': random_state}
        
        self.model = RandomForestRegressor(**model_params)
        self.model.fit(X_train, y_train)
        
        # Evaluar modelo
        y_pred = self.model.predict(X_test)
        
        self.metrics = {
            'mae': float(mean_absolute_error(y_test, y_pred)),
            'mse': float(mean_squared_error(y_test, y_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
            'r2': float(r2_score(y_test, y_pred)),
            'train_samples': int(len(X_train)),
            'test_samples': int(len(X_test)),
            'n_features': int(X.shape[1])
        }
        
        return self.metrics
    
    def predict(self, input_data: Dict[str, Any]) -> float:
        """
        Realiza predicción para nuevos datos
        
        Args:
            input_data: Diccionario con datos de entrada
                Ejemplo: {
                    'ANO': 2023.0,
                    'S': 1.0,
                    'SB1': 1.0,
                    'REGION': 'AMAZONIA',
                    'CATEGORIA': '4.B. Tierras de cultivo'
                }
        
        Returns:
            Valor predicho de CO2
        """
        if self.model is None or self.ohe is None:
            raise ValueError("Modelo no entrenado. Ejecuta train() primero.")
        
        # Crear DataFrame con input
        sample_df = pd.DataFrame([input_data])
        
        # Separar características categóricas y numéricas
        categorical_features = ['REGION', 'CATEGORIA']
        
        # One-hot encode características categóricas
        encoded_features = self.ohe.transform(sample_df[categorical_features])
        encoded_df = pd.DataFrame(
            encoded_features,
            columns=self.ohe.get_feature_names_out(categorical_features)
        )
        
        # Preparar características numéricas
        numeric_features = ['ANO', 'S', 'SB1']
        numeric_features = [f for f in numeric_features if f in sample_df.columns]
        sample_numeric = sample_df[numeric_features]
        
        # Combinar características
        sample_final = pd.concat([
            sample_numeric.reset_index(drop=True),
            encoded_df.reset_index(drop=True)
        ], axis=1)
        
        # Asegurar que todas las columnas estén presentes
        missing_cols = set(self.feature_columns) - set(sample_final.columns)
        for col in missing_cols:
            sample_final[col] = 0
        
        # Reordenar columnas
        sample_final = sample_final[self.feature_columns]
        
        # Predecir
        prediction = self.model.predict(sample_final)
        
        return float(prediction[0])
    
    def predict_batch(self, input_data_list: List[Dict[str, Any]]) -> List[float]:
        """
        Realiza predicciones para múltiples entradas
        
        Args:
            input_data_list: Lista de diccionarios con datos de entrada
        
        Returns:
            Lista de valores predichos
        """
        return [self.predict(data) for data in input_data_list]
    
    def save_model(self, model_path: str):
        """
        Guarda el modelo entrenado
        
        Args:
            model_path: Ruta donde guardar el modelo
        """
        if self.model is None:
            raise ValueError("No hay modelo para guardar")
        
        model_data = {
            'model': self.model,
            'ohe': self.ohe,
            'feature_columns': self.feature_columns,
            'metrics': self.metrics
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, model_path: str):
        """
        Carga un modelo guardado
        
        Args:
            model_path: Ruta del modelo a cargar
        """
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.ohe = model_data['ohe']
        self.feature_columns = model_data['feature_columns']
        self.metrics = model_data.get('metrics', {})
    
    def get_feature_importance(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene la importancia de las características
        
        Args:
            top_n: Número de características más importantes a retornar
        
        Returns:
            Lista con importancia de características
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado")
        
        importance = self.model.feature_importances_
        feature_importance = [
            {'feature': col, 'importance': float(imp)}
            for col, imp in zip(self.feature_columns, importance)
        ]
        
        # Ordenar por importancia
        feature_importance.sort(key=lambda x: x['importance'], reverse=True)
        
        return feature_importance[:top_n]
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información del modelo
        
        Returns:
            Diccionario con información del modelo
        """
        if self.model is None:
            return {'status': 'not_trained'}
        
        return {
            'status': 'trained',
            'model_type': 'RandomForestRegressor',
            'n_estimators': self.model.n_estimators,
            'metrics': self.metrics,
            'n_features': len(self.feature_columns),
            'feature_names': self.feature_columns
        }