"""
Script para analizar emisiones de CO2 relacionadas con:
- Cultivos transitorios
- Cultivos permanentes
- Consumo de energía eléctrica

Uso:
    python scripts/analyze_agriculture_energy.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_analysis import CO2DataAnalyzer

def load_and_clean_electricity_data():
    """Carga y limpia datos de electricidad"""
    print("📊 Cargando datos de electricidad...")
    df = pd.read_excel('data/YearlyElectricityData.xlsx')
    
    # Filtrar solo Colombia
    df = df[df['Area'] == 'Colombia'].copy()
    
    # Renombrar columnas relevantes
    df = df.rename(columns={
        'Year': 'ANO',
        'Value': 'CONSUMO_ELECTRICO'
    })
    
    # Seleccionar columnas relevantes
    cols_to_keep = ['ANO', 'CONSUMO_ELECTRICO']
    df = df[cols_to_keep]
    
    print(f"✓ Datos de electricidad cargados: {len(df)} registros")
    return df

def load_and_clean_crop_data(filepath, crop_type):
    """Carga y limpia datos de cultivos"""
    print(f"🌾 Cargando datos de cultivos {crop_type}...")
    df = pd.read_excel(filepath)
    
    # Identificar columnas de años (las que son numéricas)
    year_cols = []
    for col in df.columns:
        try:
            year = int(col)
            if 1900 < year < 2100:
                year_cols.append(col)
        except:
            pass
    
    # Si hay columnas 'TIPO' o 'Tipo', usarla como nombre del cultivo
    crop_col = None
    for col in ['TIPO', 'Tipo', 'Cultivo', 'CULTIVO']:
        if col in df.columns:
            crop_col = col
            break
    
    if not crop_col:
        print(f"⚠ No se encontró columna de tipo de cultivo en {filepath}")
        return pd.DataFrame()
    
    # Transformar de formato wide a long
    id_vars = [crop_col, 'Departamento'] if 'Departamento' in df.columns else [crop_col]
    
    df_long = df.melt(
        id_vars=id_vars,
        value_vars=year_cols,
        var_name='ANO',
        value_name='AREA_HECTAREAS'
    )
    
    # Limpiar datos
    df_long['ANO'] = pd.to_numeric(df_long['ANO'], errors='coerce')
    df_long['AREA_HECTAREAS'] = pd.to_numeric(df_long['AREA_HECTAREAS'], errors='coerce')
    df_long = df_long.dropna(subset=['ANO', 'AREA_HECTAREAS'])
    
    # Renombrar columnas
    df_long = df_long.rename(columns={
        crop_col: 'CULTIVO',
        'Departamento': 'REGION'
    })
    
    # Normalizar REGION si existe
    if 'REGION' in df_long.columns:
        df_long['REGION'] = df_long['REGION'].str.upper().str.strip()
    
    # Añadir tipo de cultivo
    df_long['TIPO_CULTIVO'] = crop_type
    
    print(f"✓ Datos de cultivos {crop_type} cargados: {len(df_long)} registros")
    print(f"  Cultivos únicos: {df_long['CULTIVO'].nunique()}")
    
    return df_long

def merge_with_co2_data(crop_df, co2_analyzer):
    """Combina datos de cultivos con datos de CO2"""
    print("\n🔗 Combinando datos de cultivos con emisiones de CO2...")
    
    # Obtener datos de CO2
    co2_df = co2_analyzer.df.copy()
    
    # Asegurar que las columnas clave existan
    if 'REGION' not in crop_df.columns:
        print("⚠ No hay columna REGION en datos de cultivos, agregando datos a nivel nacional")
        # Agrupar por año y cultivo
        crop_summary = crop_df.groupby(['ANO', 'CULTIVO', 'TIPO_CULTIVO'])['AREA_HECTAREAS'].sum().reset_index()
        
        # Agrupar CO2 por año
        co2_summary = co2_df.groupby('ANO')['VALOR_F'].sum().reset_index()
        
        # Merge
        merged = crop_summary.merge(co2_summary, on='ANO', how='inner')
    else:
        # Agrupar cultivos por región y año
        crop_summary = crop_df.groupby(['ANO', 'REGION', 'CULTIVO', 'TIPO_CULTIVO'])['AREA_HECTAREAS'].sum().reset_index()
        
        # Agrupar CO2 por región y año
        co2_summary = co2_df.groupby(['ANO', 'REGION'])['VALOR_F'].sum().reset_index()
        
        # Merge
        merged = crop_summary.merge(co2_summary, on=['ANO', 'REGION'], how='inner')
    
    print(f"✓ Datos combinados: {len(merged)} registros")
    return merged

def analyze_top_polluting_crops(merged_df, n=10):
    """Analiza los cultivos más contaminantes"""
    print(f"\n🏭 Top {n} cultivos más contaminantes:")
    
    # Agrupar por cultivo y tipo
    crop_emissions = merged_df.groupby(['CULTIVO', 'TIPO_CULTIVO']).agg({
        'VALOR_F': 'sum',
        'AREA_HECTAREAS': 'sum'
    }).reset_index()
    
    # Calcular emisiones por hectárea
    crop_emissions['CO2_POR_HECTAREA'] = crop_emissions['VALOR_F'] / crop_emissions['AREA_HECTAREAS']
    
    # Ordenar por emisiones totales
    top_total = crop_emissions.nlargest(n, 'VALOR_F')[['CULTIVO', 'TIPO_CULTIVO', 'VALOR_F', 'AREA_HECTAREAS']]
    print("\n📊 Por emisiones totales:")
    print(top_total.to_string(index=False))
    
    # Ordenar por emisiones por hectárea
    top_per_hectare = crop_emissions.nlargest(n, 'CO2_POR_HECTAREA')[['CULTIVO', 'TIPO_CULTIVO', 'CO2_POR_HECTAREA', 'AREA_HECTAREAS']]
    print("\n📊 Por emisiones por hectárea:")
    print(top_per_hectare.to_string(index=False))
    
    return crop_emissions

def compare_crop_types(merged_df):
    """Compara cultivos transitorios vs permanentes"""
    print("\n🌱 Comparación: Cultivos Transitorios vs Permanentes")
    
    comparison = merged_df.groupby('TIPO_CULTIVO').agg({
        'VALOR_F': ['sum', 'mean'],
        'AREA_HECTAREAS': 'sum',
        'CULTIVO': 'nunique'
    }).round(2)
    
    print(comparison)
    
    return comparison

def main():
    """Función principal"""
    print("=" * 60)
    print("🌍 ANÁLISIS DE EMISIONES CO2")
    print("   Agricultura y Energía")
    print("=" * 60)
    
    # Cargar datos de CO2
    print("\n📂 Cargando datos de emisiones CO2...")
    co2_df = pd.read_excel('data/factores_limpios.xlsx')
    analyzer = CO2DataAnalyzer(co2_df)
    print(f"✓ Datos de CO2 cargados: {len(analyzer.df)} registros")
    
    # Cargar datos de electricidad
    electricity_df = load_and_clean_electricity_data()
    
    # Cargar datos de cultivos
    crops_trans = load_and_clean_crop_data('data/cultivos_transitorios.xlsx', 'TRANSITORIO')
    crops_perm = load_and_clean_crop_data('data/cultivos_permanentes.xlsx', 'PERMANENTE')
    
    # Combinar ambos tipos de cultivos
    all_crops = pd.concat([crops_trans, crops_perm], ignore_index=True)
    print(f"\n✓ Total de datos de cultivos: {len(all_crops)} registros")
    
    # Analizar
    if not all_crops.empty:
        merged_data = merge_with_co2_data(all_crops, analyzer)
        
        if not merged_data.empty:
            # Guardar datos combinados
            output_file = 'data/merged_crops_co2.csv'
            merged_data.to_csv(output_file, index=False)
            print(f"\n💾 Datos combinados guardados en: {output_file}")
            
            # Análisis
            crop_emissions = analyze_top_polluting_crops(merged_data)
            comparison = compare_crop_types(merged_data)
            
            # Guardar resultados
            crop_emissions.to_csv('data/crop_emissions_analysis.csv', index=False)
            comparison.to_csv('data/crop_type_comparison.csv')
            print("\n✓ Análisis guardados en data/")
    
    print("\n" + "=" * 60)
    print("✅ Análisis completado")
    print("=" * 60)

if __name__ == "__main__":
    main()
