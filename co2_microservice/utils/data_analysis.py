import pandas as pd
import numpy as np
import unicodedata
from typing import Dict, List, Any, Optional


class CO2DataAnalyzer:
    """Clase para realizar análisis estadísticos de datos de CO2"""
    
    # Categorías de unidades según el análisis del notebook
    UNIDADES_AIRE_EMISIONES = ['GefCO2', 'GefCH4', 'GefN2O', 'GefNOx', 'GefCO']
    UNIDADES_BOSQUE_CAPTURA = ['CF', 'toneladas de masa seca por hectárea', 'MB', 'Cf', 'toneladas de materia seca']
    UNIDADES_CAUSAS_FACTORES = ['toneladas de leña/habitante/año']
    
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa el analizador con un DataFrame
        
        Args:
            df: DataFrame con datos de emisiones CO2
        """
        self.df = df.copy()
        self._preprocess_data()
        self._create_category_dataframes()
    
    def _preprocess_data(self):
        """Preprocesa los datos para análisis"""
        # Limpiar columna ANO (remover puntos finales y convertir a numérico)
        if 'ANO' in self.df.columns:
            self.df['ANO'] = self.df['ANO'].astype(str).str.rstrip('.').replace('nan', pd.NA)
            self.df['ANO'] = pd.to_numeric(self.df['ANO'], errors='coerce')
        
        # Limpiar VALOR_F (remover comas de miles)
        if 'VALOR_F' in self.df.columns:
            self.df['VALOR_F'] = self.df['VALOR_F'].astype(str).str.replace(',', '').astype(float)
        
        # Normalizar REGION (mayúsculas, sin tildes, sin espacios extra)
        if 'REGION' in self.df.columns:
            # Función para remover acentos
            def remove_accents(input_str):
                if not isinstance(input_str, str):
                    return str(input_str)
                nfkd_form = unicodedata.normalize('NFKD', input_str)
                return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

            # Aplicar normalización
            self.df['REGION'] = self.df['REGION'].astype(str).apply(remove_accents).str.upper().str.strip()

            # Filtrar filas donde REGION está vacío o contiene 'COLOMBIA' (ahora en mayúsculas)
            self.df = self.df[~((self.df['REGION'] == 'NAN') | 
                               (self.df['REGION'] == 'NONE') |
                               (self.df['REGION'].str.contains('COLOMBIA', na=False)))]
    
    def _create_category_dataframes(self):
        """Crea DataFrames separados por categoría de emisión"""
        if 'UNIDAD_F' in self.df.columns:
            self.df_aire_emisiones = self.df[self.df['UNIDAD_F'].isin(self.UNIDADES_AIRE_EMISIONES)]
            self.df_bosque_captura = self.df[self.df['UNIDAD_F'].isin(self.UNIDADES_BOSQUE_CAPTURA)]
            self.df_causas_factores = self.df[self.df['UNIDAD_F'].isin(self.UNIDADES_CAUSAS_FACTORES)]
        else:
            self.df_aire_emisiones = pd.DataFrame()
            self.df_bosque_captura = pd.DataFrame()
            self.df_causas_factores = pd.DataFrame()
    
    def filter_data(self, 
                   year: Optional[int] = None, 
                   region: Optional[str] = None,
                   start_year: Optional[int] = None,
                   end_year: Optional[int] = None,
                   category_type: Optional[str] = None) -> pd.DataFrame:
        """
        Filtra datos por año, región y tipo de categoría
        
        Args:
            year: Año específico
            region: Región específica
            start_year: Año inicial del rango
            end_year: Año final del rango
            category_type: Tipo de categoría ('aire_emisiones', 'bosque_captura', 'causas_factores')
        
        Returns:
            DataFrame filtrado
        """
        # Seleccionar DataFrame base según categoría
        if category_type == 'aire_emisiones':
            df_filtered = self.df_aire_emisiones.copy()
        elif category_type == 'bosque_captura':
            df_filtered = self.df_bosque_captura.copy()
        elif category_type == 'causas_factores':
            df_filtered = self.df_causas_factores.copy()
        else:
            df_filtered = self.df.copy()
        
        # Filtrar por año específico o rango
        if year is not None and 'ANO' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['ANO'] == year]
        elif start_year is not None or end_year is not None:
            if 'ANO' in df_filtered.columns:
                if start_year is not None:
                    df_filtered = df_filtered[df_filtered['ANO'] >= start_year]
                if end_year is not None:
                    df_filtered = df_filtered[df_filtered['ANO'] <= end_year]
        
        # Filtrar por región
        if region is not None and 'REGION' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['REGION'] == region]
        
        return df_filtered
    
    def get_general_stats(self, 
                         year: Optional[int] = None, 
                         region: Optional[str] = None,
                         category_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales del dataset con filtros opcionales
        
        Args:
            year: Año específico para filtrar
            region: Región específica para filtrar
            category_type: Tipo de categoría para filtrar
        
        Returns:
            Diccionario con estadísticas descriptivas
        """
        df_filtered = self.filter_data(year=year, region=region, category_type=category_type)
        
        stats = {
            "total_records": int(len(df_filtered)),
            "total_columns": int(len(df_filtered.columns)),
            "columns": list(df_filtered.columns),
            "date_range": {
                "min_year": float(df_filtered['ANO'].min()) if 'ANO' in df_filtered.columns and not df_filtered.empty else None,
                "max_year": float(df_filtered['ANO'].max()) if 'ANO' in df_filtered.columns and not df_filtered.empty else None
            },
            "co2_stats": {
                "mean": float(df_filtered['VALOR_F'].mean()) if 'VALOR_F' in df_filtered.columns and not df_filtered.empty else None,
                "median": float(df_filtered['VALOR_F'].median()) if 'VALOR_F' in df_filtered.columns and not df_filtered.empty else None,
                "std": float(df_filtered['VALOR_F'].std()) if 'VALOR_F' in df_filtered.columns and not df_filtered.empty else None,
                "min": float(df_filtered['VALOR_F'].min()) if 'VALOR_F' in df_filtered.columns and not df_filtered.empty else None,
                "max": float(df_filtered['VALOR_F'].max()) if 'VALOR_F' in df_filtered.columns and not df_filtered.empty else None,
                "total": float(df_filtered['VALOR_F'].sum()) if 'VALOR_F' in df_filtered.columns and not df_filtered.empty else None
            },
            "missing_values": df_filtered.isnull().sum().to_dict(),
            "filters_applied": {
                "year": year,
                "region": region,
                "category_type": category_type
            }
        }
        return stats
    
    def get_category_summary(self) -> Dict[str, Any]:
        """
        Obtiene resumen de cada categoría de emisión
        
        Returns:
            Diccionario con estadísticas por categoría
        """
        return {
            "aire_emisiones": {
                "total_records": len(self.df_aire_emisiones),
                "total_emissions": float(self.df_aire_emisiones['VALOR_F'].sum()) if not self.df_aire_emisiones.empty else 0,
                "units": self.UNIDADES_AIRE_EMISIONES
            },
            "bosque_captura": {
                "total_records": len(self.df_bosque_captura),
                "total_capture": float(self.df_bosque_captura['VALOR_F'].sum()) if not self.df_bosque_captura.empty else 0,
                "units": self.UNIDADES_BOSQUE_CAPTURA
            },
            "causas_factores": {
                "total_records": len(self.df_causas_factores),
                "total_value": float(self.df_causas_factores['VALOR_F'].sum()) if not self.df_causas_factores.empty else 0,
                "units": self.UNIDADES_CAUSAS_FACTORES
            }
        }
    
    def get_stats_by_region(self, 
                           year: Optional[int] = None,
                           category_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Calcula estadísticas de CO2 por región con filtros opcionales
        
        Args:
            year: Año específico para filtrar
            category_type: Tipo de categoría para filtrar
        
        Returns:
            Lista de diccionarios con estadísticas por región
        """
        df_filtered = self.filter_data(year=year, category_type=category_type)
        
        if 'REGION' not in df_filtered.columns or 'VALOR_F' not in df_filtered.columns or df_filtered.empty:
            return []
        
        # Filtrar valores no nulos
        df_clean = df_filtered.dropna(subset=['REGION', 'VALOR_F'])
        
        region_stats = df_clean.groupby('REGION')['VALOR_F'].agg([
            ('count', 'count'),
            ('total', 'sum'),
            ('mean', 'mean'),
            ('median', 'median'),
            ('std', 'std'),
            ('min', 'min'),
            ('max', 'max')
        ]).reset_index()
        
        return region_stats.to_dict('records')
    
    def get_stats_by_category(self, 
                             year: Optional[int] = None,
                             region: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Calcula estadísticas de CO2 por categoría con filtros opcionales
        
        Args:
            year: Año específico para filtrar
            region: Región específica para filtrar
        
        Returns:
            Lista de diccionarios con estadísticas por categoría
        """
        df_filtered = self.filter_data(year=year, region=region)
        
        if 'CATEGORIA' not in df_filtered.columns or 'VALOR_F' not in df_filtered.columns or df_filtered.empty:
            return []
        
        df_clean = df_filtered.dropna(subset=['CATEGORIA', 'VALOR_F'])
        
        category_stats = df_clean.groupby('CATEGORIA')['VALOR_F'].agg([
            ('count', 'count'),
            ('total', 'sum'),
            ('mean', 'mean'),
            ('median', 'median'),
            ('std', 'std'),
            ('min', 'min'),
            ('max', 'max')
        ]).reset_index()
        
        return category_stats.to_dict('records')
    
    def get_stats_by_region_category(self, 
                                     year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Calcula estadísticas de CO2 por combinación región-categoría
        
        Args:
            year: Año específico para filtrar
        
        Returns:
            Lista de diccionarios con estadísticas por región y categoría
        """
        df_filtered = self.filter_data(year=year)
        
        if not all(col in df_filtered.columns for col in ['REGION', 'CATEGORIA', 'VALOR_F']) or df_filtered.empty:
            return []
        
        df_clean = df_filtered.dropna(subset=['REGION', 'CATEGORIA', 'VALOR_F'])
        
        combined_stats = df_clean.groupby(['REGION', 'CATEGORIA'])['VALOR_F'].agg([
            ('count', 'count'),
            ('total', 'sum'),
            ('mean', 'mean'),
            ('median', 'median'),
            ('std', 'std'),
            ('min', 'min'),
            ('max', 'max')
        ]).reset_index()
        
        return combined_stats.to_dict('records')
    
    def get_emissions_by_unit_type(self, 
                                   region: Optional[str] = None,
                                   year: Optional[int] = None,
                                   category_type: str = 'aire_emisiones') -> List[Dict[str, Any]]:
        """
        Obtiene emisiones agrupadas por tipo de unidad y región
        
        Args:
            region: Región específica (opcional)
            year: Año específico (opcional)
            category_type: Tipo de categoría ('aire_emisiones', 'bosque_captura', 'causas_factores')
        
        Returns:
            Lista de diccionarios con emisiones por región y tipo de unidad
        """
        df_filtered = self.filter_data(year=year, region=region, category_type=category_type)
        
        if 'REGION' not in df_filtered.columns or 'UNIDAD_F' not in df_filtered.columns or df_filtered.empty:
            return []
        
        df_clean = df_filtered.dropna(subset=['REGION', 'UNIDAD_F', 'VALOR_F'])
        
        grouped = df_clean.groupby(['REGION', 'UNIDAD_F'])['VALOR_F'].agg([
            ('count', 'count'),
            ('total', 'sum'),
            ('mean', 'mean')
        ]).reset_index()
        
        return grouped.to_dict('records')
    
    def get_time_series_by_region(self, 
                                  region: Optional[str] = None,
                                  category_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtiene serie temporal de CO2 por región y categoría
        
        Args:
            region: Región específica (opcional)
            category_type: Tipo de categoría (opcional)
        
        Returns:
            Lista de diccionarios con series temporales
        """
        df_filtered = self.filter_data(region=region, category_type=category_type)
        
        if 'ANO' not in df_filtered.columns or 'VALOR_F' not in df_filtered.columns or df_filtered.empty:
            return []
        
        df_clean = df_filtered.dropna(subset=['ANO', 'VALOR_F'])
        
        time_series = df_clean.groupby('ANO')['VALOR_F'].agg([
            ('count', 'count'),
            ('total', 'sum'),
            ('mean', 'mean'),
            ('median', 'median')
        ]).reset_index()
        
        return time_series.to_dict('records')
    
    def get_top_emitters(self, 
                        n: int = 10, 
                        by: str = 'REGION',
                        year: Optional[int] = None,
                        category_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtiene los mayores emisores de CO2
        
        Args:
            n: Número de registros a retornar
            by: Agrupación ('REGION', 'CATEGORIA', 'CLASIFICACION1')
            year: Año específico (opcional)
            category_type: Tipo de categoría (opcional)
        
        Returns:
            Lista con los mayores emisores
        """
        df_filtered = self.filter_data(year=year, category_type=category_type)
        
        if by not in df_filtered.columns or 'VALOR_F' not in df_filtered.columns or df_filtered.empty:
            return []
        
        df_clean = df_filtered.dropna(subset=[by, 'VALOR_F'])
        
        top_emitters = df_clean.groupby(by)['VALOR_F'].agg([
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
    
    def get_available_years(self) -> List[int]:
        """Retorna lista de años disponibles"""
        if 'ANO' in self.df.columns:
            years = self.df['ANO'].dropna().unique()
            return sorted([int(y) for y in years])
        return []
    
    def get_dashboard_data(self,
                          year: Optional[int] = None,
                          region: Optional[str] = None,
                          category_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene datos consolidados para dashboard con filtros
        
        Args:
            year: Año específico
            region: Región específica
            category_type: Tipo de categoría
        
        Returns:
            Diccionario con datos para dashboard
        """
        return {
            "general_stats": self.get_general_stats(year=year, region=region, category_type=category_type),
            "category_summary": self.get_category_summary(),
            "region_stats": self.get_stats_by_region(year=year, category_type=category_type),
            "category_stats": self.get_stats_by_category(year=year, region=region),
            "time_series": self.get_time_series_by_region(region=region, category_type=category_type),
            "top_emitters": self.get_top_emitters(n=10, year=year, category_type=category_type),
            "emissions_by_unit": self.get_emissions_by_unit_type(region=region, year=year, category_type=category_type),
            "available_filters": {
                "regions": self.get_available_regions(),
                "categories": self.get_available_categories(),
                "years": self.get_available_years(),
                "category_types": ["aire_emisiones", "bosque_captura", "causas_factores"]
            }
        }