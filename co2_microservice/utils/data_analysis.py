import pandas as pd
import numpy as np
from typing import Dict, List, Any


class CO2DataAnalyzer:
    """Clase para realizar análisis estadísticos de datos de CO2"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa el analizador con un DataFrame
        
        Args:
            df: DataFrame con datos de emisiones CO2
        """
        self.df = df.copy()
        self._preprocess_data()
    
    def _preprocess_data(self):
        """Preprocesa los datos para análisis"""
        # Limpiar columna ANO (convertir comas a puntos)
        if 'ANO' in self.df.columns:
            self.df['ANO'] = self.df['ANO'].astype(str).str.replace(',', '.').astype(float)
        
        # Limpiar VALOR_F (remover comas de miles)
        if 'VALOR_F' in self.df.columns:
            self.df['VALOR_F'] = self.df['VALOR_F'].astype(str).str.replace(',', '').astype(float)
    
    def get_general_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales del dataset
        
        Returns:
            Diccionario con estadísticas descriptivas
        """
        stats = {
            "total_records": int(len(self.df)),
            "total_columns": int(len(self.df.columns)),
            "columns": list(self.df.columns),
            "date_range": {
                "min_year": float(self.df['ANO'].min()) if 'ANO' in self.df.columns else None,
                "max_year": float(self.df['ANO'].max()) if 'ANO' in self.df.columns else None
            },
            "co2_stats": {
                "mean": float(self.df['VALOR_F'].mean()) if 'VALOR_F' in self.df.columns else None,
                "median": float(self.df['VALOR_F'].median()) if 'VALOR_F' in self.df.columns else None,
                "std": float(self.df['VALOR_F'].std()) if 'VALOR_F' in self.df.columns else None,
                "min": float(self.df['VALOR_F'].min()) if 'VALOR_F' in self.df.columns else None,
                "max": float(self.df['VALOR_F'].max()) if 'VALOR_F' in self.df.columns else None
            },
            "missing_values": self.df.isnull().sum().to_dict()
        }
        return stats
    
    def get_stats_by_region(self) -> List[Dict[str, Any]]:
        """
        Calcula estadísticas de CO2 por región
        
        Returns:
            Lista de diccionarios con estadísticas por región
        """
        if 'REGION' not in self.df.columns or 'VALOR_F' not in self.df.columns:
            return []
        
        # Filtrar valores no nulos
        df_filtered = self.df.dropna(subset=['REGION', 'VALOR_F'])
        
        region_stats = df_filtered.groupby('REGION')['VALOR_F'].agg([
            ('count', 'count'),
            ('mean', 'mean'),
            ('median', 'median'),
            ('std', 'std'),
            ('min', 'min'),
            ('max', 'max')
        ]).reset_index()
        
        return region_stats.to_dict('records')
    
    def get_stats_by_category(self) -> List[Dict[str, Any]]:
        """
        Calcula estadísticas de CO2 por categoría
        
        Returns:
            Lista de diccionarios con estadísticas por categoría
        """
        if 'CATEGORIA' not in self.df.columns or 'VALOR_F' not in self.df.columns:
            return []
        
        df_filtered = self.df.dropna(subset=['CATEGORIA', 'VALOR_F'])
        
        category_stats = df_filtered.groupby('CATEGORIA')['VALOR_F'].agg([
            ('count', 'count'),
            ('mean', 'mean'),
            ('median', 'median'),
            ('std', 'std'),
            ('min', 'min'),
            ('max', 'max')
        ]).reset_index()
        
        return category_stats.to_dict('records')
    
    def get_stats_by_region_category(self) -> List[Dict[str, Any]]:
        """
        Calcula estadísticas de CO2 por combinación región-categoría
        
        Returns:
            Lista de diccionarios con estadísticas por región y categoría
        """
        if 'REGION' not in self.df.columns or 'CATEGORIA' not in self.df.columns or 'VALOR_F' not in self.df.columns:
            return []
        
        df_filtered = self.df.dropna(subset=['REGION', 'CATEGORIA', 'VALOR_F'])
        
        combined_stats = df_filtered.groupby(['REGION', 'CATEGORIA'])['VALOR_F'].agg([
            ('count', 'count'),
            ('mean', 'mean'),
            ('median', 'median'),
            ('std', 'std'),
            ('min', 'min'),
            ('max', 'max')
        ]).reset_index()
        
        return combined_stats.to_dict('records')
    
    def get_time_series_by_region(self, region: str = None) -> List[Dict[str, Any]]:
        """
        Obtiene serie temporal de CO2 por región
        
        Args:
            region: Región específica (opcional)
        
        Returns:
            Lista de diccionarios con series temporales
        """
        if 'ANO' not in self.df.columns or 'VALOR_F' not in self.df.columns:
            return []
        
        df_filtered = self.df.dropna(subset=['ANO', 'VALOR_F'])
        
        if region and 'REGION' in self.df.columns:
            df_filtered = df_filtered[df_filtered['REGION'] == region]
        
        time_series = df_filtered.groupby('ANO')['VALOR_F'].agg([
            ('count', 'count'),
            ('mean', 'mean'),
            ('median', 'median')
        ]).reset_index()
        
        return time_series.to_dict('records')
    
    def get_top_emitters(self, n: int = 10, by: str = 'region') -> List[Dict[str, Any]]:
        """
        Obtiene los mayores emisores de CO2
        
        Args:
            n: Número de registros a retornar
            by: Agrupación ('region', 'categoria', 'clasificacion1')
        
        Returns:
            Lista con los mayores emisores
        """
        if by not in self.df.columns or 'VALOR_F' not in self.df.columns:
            return []
        
        df_filtered = self.df.dropna(subset=[by, 'VALOR_F'])
        
        top_emitters = df_filtered.groupby(by)['VALOR_F'].agg([
            ('total_emissions', 'sum'),
            ('avg_emissions', 'mean'),
            ('count', 'count')
        ]).reset_index()
        
        top_emitters = top_emitters.sort_values('total_emissions', ascending=False).head(n)
        
        return top_emitters.to_dict('records')
    
    def get_available_regions(self) -> List[str]:
        """Retorna lista de regiones disponibles"""
        if 'REGION' in self.df.columns:
            return sorted(self.df['REGION'].dropna().unique().tolist())
        return []
    
    def get_available_categories(self) -> List[str]:
        """Retorna lista de categorías disponibles"""
        if 'CATEGORIA' in self.df.columns:
            return sorted(self.df['CATEGORIA'].dropna().unique().tolist())
        return []