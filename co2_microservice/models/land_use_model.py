import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pickle


class LandUseCO2Model:
    """
    Modelo ML para cruzar datos de emisiones CO2 con uso de suelo
    Permite predecir emisiones basadas en región, año y tipo de uso de suelo
    """
    
    def __init__(self):
        """Inicializa el modelo"""
        self.model = None
        self.ohe = None
        self.scaler = None
        self.feature_columns = None
        self.metrics = {}
        self.land_use_mapping = {}
    
    def merge_datasets(self, 
                      co2_df: pd.DataFrame, 
                      land_use_df: pd.DataFrame,
                      on: List[str] = ['ANO', 'REGION']) -> pd.DataFrame:
        """
        Cruza datasets de CO2 y uso de suelo
        
        Args:
            co2_df: DataFrame de emisiones CO2
            land_use_df: DataFrame de uso de suelo
            on: Columnas para hacer el merge
        
        Returns:
            DataFrame combinado
        """
        # Verificar que las columnas de merge existan
        for col in on:
            if col not in co2_df.columns:
                raise ValueError(f"Columna '{col}' no encontrada en DataFrame de CO2")
            if col not in land_use_df.columns:
                raise ValueError(f"Columna '{col}' no encontrada en DataFrame de uso de suelo")
        
        # Realizar merge
        merged_df = pd.merge(
            co2_df, 
            land_use_df, 
            on=on, 
            how='inner',
            suffixes=('_co2', '_land')
        )
        
        print(f"✓ Datasets combinados: {len(merged_df)} registros")
        print(f"  - CO2 original: {len(co2_df)} registros")
        print(f"  - Uso de suelo original: {len(land_use_df)} registros")
        
        return merged_df
    
    def prepare_features(self, 
                        df: pd.DataFrame,
                        co2_column: str = 'VALOR_F',
                        land_use_columns: List[str] = None,
                        categorical_columns: List[str] = None,
                        numeric_columns: List[str] = None) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepara features para entrenamiento
        
        Args:
            df: DataFrame combinado
            co2_column: Nombre de la columna objetivo (emisiones CO2)
            land_use_columns: Columnas de uso de suelo a incluir
            categorical_columns: Columnas categóricas adicionales
            numeric_columns: Columnas numéricas adicionales
        
        Returns:
            Tupla (X, y) con features y target
        """
        df_clean = df.copy()
        
        # Features por defecto
        if land_use_columns is None:
            # Buscar columnas que contengan información de uso de suelo
            land_use_columns = [col for col in df.columns 
                              if any(keyword in col.lower() 
                                   for keyword in ['uso', 'suelo', 'land', 'use', 'hectarea', 'area'])]
        
        if categorical_columns is None:
            categorical_columns = ['REGION', 'CATEGORIA']
        
        if numeric_columns is None:
            numeric_columns = ['ANO', 'S', 'SB1']
        
        # Filtrar columnas que existen
        land_use_columns = [col for col in land_use_columns if col in df_clean.columns]
        categorical_columns = [col for col in categorical_columns if col in df_clean.columns]
        numeric_columns = [col for col in numeric_columns if col in df_clean.columns]
        
        # Eliminar filas con valores nulos en columnas clave
        required_cols = categorical_columns + [co2_column]
        df_clean = df_clean.dropna(subset=required_cols)
        
        # Separar features y target
        y = df_clean[co2_column].values
        
        # Preparar features
        feature_dfs = []
        
        # Features numéricas
        if numeric_columns:
            numeric_features = df_clean[numeric_columns].fillna(0)
            feature_dfs.append(numeric_features)
        
        # Features de uso de suelo (numéricas)
        if land_use_columns:
            land_use_features = df_clean[land_use_columns].fillna(0)
            feature_dfs.append(land_use_features)
        
        # Features categóricas (one-hot encoding)
        if categorical_columns:
            if self.ohe is None:
                self.ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
                encoded_features = self.ohe.fit_transform(df_clean[categorical_columns])
            else:
                encoded_features = self.ohe.transform(df_clean[categorical_columns])
            
            encoded_df = pd.DataFrame(
                encoded_features,
                columns=self.ohe.get_feature_names_out(categorical_columns),
                index=df_clean.index
            )
            feature_dfs.append(encoded_df)
        
        # Combinar todas las features
        X = pd.concat(feature_dfs, axis=1).reset_index(drop=True)
        
        # Guardar nombres de columnas
        self.feature_columns = X.columns.tolist()
        
        return X, y
    
    def train(self,
             merged_df: pd.DataFrame,
             co2_column: str = 'VALOR_F',
             land_use_columns: List[str] = None,
             model_type: str = 'random_forest',
             test_size: float = 0.2,
             random_state: int = 42,
             **model_params) -> Dict[str, float]:
        """
        Entrena el modelo de predicción
        
        Args:
            merged_df: DataFrame con datos combinados
            co2_column: Columna objetivo
            land_use_columns: Columnas de uso de suelo
            model_type: Tipo de modelo ('random_forest', 'gradient_boosting', 'linear')
            test_size: Proporción de test
            random_state: Semilla aleatoria
            **model_params: Parámetros del modelo
        
        Returns:
            Diccionario con métricas
        """
        # Preparar datos
        X, y = self.prepare_features(
            merged_df, 
            co2_column=co2_column,
            land_use_columns=land_use_columns
        )
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Escalar features numéricas
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Seleccionar y entrenar modelo
        if model_type == 'random_forest':
            if not model_params:
                model_params = {'n_estimators': 100, 'random_state': random_state, 'n_jobs': -1}
            self.model = RandomForestRegressor(**model_params)
        elif model_type == 'gradient_boosting':
            if not model_params:
                model_params = {'n_estimators': 100, 'random_state': random_state}
            self.model = GradientBoostingRegressor(**model_params)
        elif model_type == 'linear':
            self.model = LinearRegression(**model_params)
        else:
            raise ValueError(f"Modelo '{model_type}' no soportado")
        
        # Entrenar
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluar
        y_pred_train = self.model.predict(X_train_scaled)
        y_pred_test = self.model.predict(X_test_scaled)
        
        # Calcular métricas
        self.metrics = {
            'train_mae': float(mean_absolute_error(y_train, y_pred_train)),
            'test_mae': float(mean_absolute_error(y_test, y_pred_test)),
            'train_rmse': float(np.sqrt(mean_squared_error(y_train, y_pred_train))),
            'test_rmse': float(np.sqrt(mean_squared_error(y_test, y_pred_test))),
            'train_r2': float(r2_score(y_train, y_pred_train)),
            'test_r2': float(r2_score(y_test, y_pred_test)),
            'train_samples': int(len(X_train)),
            'test_samples': int(len(X_test)),
            'n_features': int(X.shape[1]),
            'model_type': model_type
        }
        
        # Cross-validation score
        try:
            cv_scores = cross_val_score(
                self.model, X_train_scaled, y_train, 
                cv=5, scoring='r2', n_jobs=-1
            )
            self.metrics['cv_r2_mean'] = float(cv_scores.mean())
            self.metrics['cv_r2_std'] = float(cv_scores.std())
        except:
            pass
        
        return self.metrics
    
    def predict(self, input_data: Dict[str, Any]) -> float:
        """
        Realiza predicción para nuevos datos
        
        Args:
            input_data: Diccionario con datos de entrada
                Debe incluir: ANO, REGION, CATEGORIA, y campos de uso de suelo
        
        Returns:
            Predicción de emisión CO2
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado")
        
        # Crear DataFrame temporal
        sample_df = pd.DataFrame([input_data])
        
        # Preparar features (similar al entrenamiento)
        feature_dfs = []
        
        # Numéricas básicas
        numeric_cols = [col for col in ['ANO', 'S', 'SB1'] if col in sample_df.columns]
        if numeric_cols:
            feature_dfs.append(sample_df[numeric_cols].fillna(0))
        
        # Uso de suelo (todas las columnas numéricas restantes)
        land_cols = [col for col in sample_df.columns 
                    if col not in ['ANO', 'S', 'SB1', 'REGION', 'CATEGORIA'] 
                    and pd.api.types.is_numeric_dtype(sample_df[col])]
        if land_cols:
            feature_dfs.append(sample_df[land_cols].fillna(0))
        
        # Categóricas
        cat_cols = [col for col in ['REGION', 'CATEGORIA'] if col in sample_df.columns]
        if cat_cols and self.ohe is not None:
            encoded = self.ohe.transform(sample_df[cat_cols])
            encoded_df = pd.DataFrame(
                encoded,
                columns=self.ohe.get_feature_names_out(cat_cols)
            )
            feature_dfs.append(encoded_df)
        
        # Combinar
        sample_features = pd.concat(feature_dfs, axis=1).reset_index(drop=True)
        
        # Asegurar que tenga todas las columnas necesarias
        missing_cols = set(self.feature_columns) - set(sample_features.columns)
        for col in missing_cols:
            sample_features[col] = 0
        
        sample_features = sample_features[self.feature_columns]
        
        # Escalar
        sample_scaled = self.scaler.transform(sample_features)
        
        # Predecir
        prediction = self.model.predict(sample_scaled)
        
        return float(prediction[0])
    
    def get_feature_importance(self, top_n: int = 15) -> List[Dict[str, Any]]:
        """
        Obtiene importancia de features (solo para modelos basados en árboles)
        
        Args:
            top_n: Número de features más importantes
        
        Returns:
            Lista con importancia de features
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado")
        
        if not hasattr(self.model, 'feature_importances_'):
            return []
        
        importance = self.model.feature_importances_
        feature_importance = [
            {'feature': col, 'importance': float(imp)}
            for col, imp in zip(self.feature_columns, importance)
        ]
        
        feature_importance.sort(key=lambda x: x['importance'], reverse=True)
        
        return feature_importance[:top_n]
    
    def analyze_land_use_impact(self, 
                                merged_df: pd.DataFrame,
                                land_use_columns: List[str],
                                co2_column: str = 'VALOR_F') -> Dict[str, Any]:
        """
        Analiza el impacto de diferentes tipos de uso de suelo en emisiones CO2
        
        Args:
            merged_df: DataFrame combinado
            land_use_columns: Columnas de uso de suelo
            co2_column: Columna de emisiones CO2
        
        Returns:
            Análisis de correlaciones e impacto
        """
        df_clean = merged_df.dropna(subset=[co2_column])
        
        correlations = {}
        for col in land_use_columns:
            if col in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean[col]):
                corr = df_clean[col].corr(df_clean[co2_column])
                if not np.isnan(corr):
                    correlations[col] = float(corr)
        
        # Ordenar por correlación absoluta
        sorted_correlations = sorted(
            correlations.items(), 
            key=lambda x: abs(x[1]), 
            reverse=True
        )
        
        return {
            'correlations': dict(sorted_correlations),
            'top_positive_impact': [
                {'feature': k, 'correlation': v} 
                for k, v in sorted_correlations[:5] if v > 0
            ],
            'top_negative_impact': [
                {'feature': k, 'correlation': v} 
                for k, v in sorted(correlations.items(), key=lambda x: x[1])[:5] if v < 0
            ]
        }
    
    def save_model(self, filepath: str):
        """Guarda el modelo entrenado"""
        if self.model is None:
            raise ValueError("No hay modelo para guardar")
        
        model_data = {
            'model': self.model,
            'ohe': self.ohe,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'metrics': self.metrics
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, filepath: str):
        """Carga un modelo guardado"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.ohe = model_data['ohe']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        self.metrics = model_data.get('metrics', {})