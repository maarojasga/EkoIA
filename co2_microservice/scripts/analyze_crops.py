"""
Análisis de cultivos y CO2 - Versión funcional
"""

import pandas as pd
import numpy as np

print("=" * 70)
print("🌍 ANÁLISIS DE EMISIONES CO2 CON CULTIVOS AGRÍCOLAS")
print("=" * 70)

# 1. Cargar CO2
print("\n📊 Cargando datos de emisiones CO2...")
co2_df = pd.read_excel('data/factores_limpios.xlsx')
print(f"   ✓ {len(co2_df):,} registros")

# 2. Cargar cultivos transitorios
print("\n🌾 Cargando cultivos transitorios...")
ct = pd.read_excel('data/cultivos_transitorios.xlsx')
print(f"   Forma: {ct.shape}")
print(f"   Columnas: {list(ct.columns[:10])}")

# Identificar años - buscar columnas que contengan 4 dígitos
year_cols_t = []
for col in ct.columns:
    col_str = str(col)
    # Buscar patrones como "1987", "Unnamed: 10", "Área sembrada 1987", etc.
    if col_str.isdigit() and len(col_str) == 4:
        try:
            year = int(col_str)
            if 1900 < year < 2100:
                year_cols_t.append(col)
        except:
            pass

print(f"   ✓ {len(year_cols_t)} columnas de años encontradas")

if len(year_cols_t) > 0:
    print(f"   Rango: {min([int(str(y)) for y in year_cols_t])} - {max([int(str(y)) for y in year_cols_t])}")
    
    # Transformar a formato largo
    id_cols = ['Tipo'] if 'Tipo' in ct.columns else (['TIPO'] if 'TIPO' in ct.columns else [])
    if 'Departamento' in ct.columns:
        id_cols.append('Departamento')
    
    ct_long = ct.melt(
        id_vars=id_cols,
        value_vars=year_cols_t,
        var_name='ANO',
        value_name='HECTAREAS'
    )
    
    ct_long['ANO'] = pd.to_numeric(ct_long['ANO'])
    ct_long['HECTAREAS'] = pd.to_numeric(ct_long['HECTAREAS'], errors='coerce')
    ct_long = ct_long.dropna(subset=['HECTAREAS'])
    ct_long['TIPO_CULTIVO'] = 'TRANSITORIO'
    
    # Renombrar columnas
    if 'Tipo' in ct_long.columns:
        ct_long = ct_long.rename(columns={'Tipo': 'CULTIVO'})
    elif 'TIPO' in ct_long.columns:
        ct_long = ct_long.rename(columns={'TIPO': 'CULTIVO'})
    
    print(f"   ✓ {len(ct_long):,} registros procesados")
    print(f"   ✓ {ct_long['CULTIVO'].nunique()} cultivos únicos")
else:
    print("   ⚠️  No se encontraron columnas de años")
    ct_long = pd.DataFrame()

# 3. Cargar cultivos permanentes
print("\n🌳 Cargando cultivos permanentes...")
cp = pd.read_excel('data/cultivos_permanentes.xlsx')
print(f"   Forma: {cp.shape}")

year_cols_p = []
for col in cp.columns:
    col_str = str(col)
    if col_str.isdigit() and len(col_str) == 4:
        try:
            year = int(col_str)
            if 1900 < year < 2100:
                year_cols_p.append(col)
        except:
            pass

print(f"   ✓ {len(year_cols_p)} columnas de años encontradas")

if len(year_cols_p) > 0:
    id_cols_p = ['Tipo'] if 'Tipo' in cp.columns else (['TIPO'] if 'TIPO' in cp.columns else [])
    if 'Departamento' in cp.columns:
        id_cols_p.append('Departamento')
    
    cp_long = cp.melt(
        id_vars=id_cols_p,
        value_vars=year_cols_p,
        var_name='ANO',
        value_name='HECTAREAS'
    )
    
    cp_long['ANO'] = pd.to_numeric(cp_long['ANO'])
    cp_long['HECTAREAS'] = pd.to_numeric(cp_long['HECTAREAS'], errors='coerce')
    cp_long = cp_long.dropna(subset=['HECTAREAS'])
    cp_long['TIPO_CULTIVO'] = 'PERMANENTE'
    
    if 'Tipo' in cp_long.columns:
        cp_long = cp_long.rename(columns={'Tipo': 'CULTIVO'})
    
    print(f"   ✓ {len(cp_long):,} registros procesados")
    print(f"   ✓ {cp_long['CULTIVO'].nunique()} cultivos únicos")
else:
    print("   ⚠️  No se encontraron columnas de años")
    cp_long = pd.DataFrame()

# 4. Combinar
print("\n🔗 Combinando datos...")
if not ct_long.empty and not cp_long.empty:
    all_crops = pd.concat([ct_long, cp_long], ignore_index=True)
    print(f"   ✓ {len(all_crops):,} registros totales")
    print(f"   ✓ {all_crops['CULTIVO'].nunique()} cultivos únicos")
    
    # 5. Agrupar CO2 por año (sin región ya que los cultivos no tienen región consistente)
    print("\n📈 Agrupando emisiones CO2 por año...")
    co2_yearly = co2_df.groupby('ANO')['VALOR_F'].sum().reset_index()
    print(f"   ✓ {len(co2_yearly)} años con datos de CO2")
    
    # 6. Agrupar cultivos por año
    print("\n🌾 Agrupando cultivos por año...")
    crops_yearly = all_crops.groupby(['ANO', 'CULTIVO', 'TIPO_CULTIVO'])['HECTAREAS'].sum().reset_index()
    print(f"   ✓ {len(crops_yearly)} combinaciones año-cultivo")
    
    # 7. Merge
    print("\n🔀 Combinando datasets...")
    merged = crops_yearly.merge(co2_yearly, on='ANO', how='inner')
    print(f"   ✓ {len(merged):,} registros combinados")
    print(f"   Años: {int(merged['ANO'].min())} - {int(merged['ANO'].max())}")
    
    if len(merged) > 0:
        # 8. Análisis
        print("\n" + "=" * 70)
        print("📊 RESULTADOS DEL ANÁLISIS")
        print("=" * 70)
        
        crop_stats = merged.groupby(['CULTIVO', 'TIPO_CULTIVO']).agg({
            'VALOR_F': 'sum',
            'HECTAREAS': 'sum'
        }).reset_index()
        
        crop_stats['CO2_POR_HA'] = crop_stats['VALOR_F'] / crop_stats['HECTAREAS']
        
        print("\n🏆 TOP 15 CULTIVOS (por emisiones totales asociadas):")
        print("-" * 70)
        top15 = crop_stats.nlargest(15, 'VALOR_F')
        print(top15[['CULTIVO', 'TIPO_CULTIVO', 'VALOR_F', 'HECTAREAS']].to_string(index=False))
        
        print("\n\n🌡️  TOP 15 CULTIVOS (por emisiones por hectárea):")
        print("-" * 70)
        top15_ha = crop_stats.nlargest(15, 'CO2_POR_HA')
        print(top15_ha[['CULTIVO', 'TIPO_CULTIVO', 'CO2_POR_HA', 'HECTAREAS']].to_string(index=False))
        
        print("\n\n⚖️  COMPARACIÓN: TRANSITORIOS vs PERMANENTES:")
        print("-" * 70)
        comparison = merged.groupby('TIPO_CULTIVO').agg({
            'VALOR_F': ['sum', 'mean'],
            'HECTAREAS': 'sum',
            'CULTIVO': 'nunique'
        })
        comparison.columns = ['CO2_Total', 'CO2_Promedio', 'Hectareas_Total', 'Num_Cultivos']
        print(comparison)
        
        # 9. Guardar resultados
        print("\n\n💾 Guardando resultados...")
        merged.to_csv('data/merged_crops_co2.csv', index=False)
        crop_stats.to_csv('data/crop_emissions_analysis.csv', index=False)
        print("   ✓ data/merged_crops_co2.csv")
        print("   ✓ data/crop_emissions_analysis.csv")
        
        print("\n" + "=" * 70)
        print("✅ ANÁLISIS COMPLETADO EXITOSAMENTE")
        print("=" * 70)
    else:
        print("\n⚠️  No se pudieron combinar los datos.")
else:
    print("\n⚠️  No hay datos de cultivos para analizar.")
