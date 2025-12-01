"""
Script simplificado para analizar cultivos y CO2
"""

import pandas as pd
import numpy as np

print("=" * 60)
print("🌍 ANÁLISIS DE EMISIONES CO2 - Agricultura")
print("=" * 60)

# 1. Cargar datos de CO2
print("\n1️⃣ Cargando datos de emisiones CO2...")
co2_df = pd.read_excel('data/factores_limpios.xlsx')

# Normalizar REGION
co2_df['REGION'] = co2_df['REGION'].astype(str).str.upper().str.strip()

# Filtrar y limpiar
co2_df = co2_df[~co2_df['REGION'].isin(['NAN', 'NONE'])]
co2_df = co2_df[~co2_df['REGION'].str.contains('COLOMBIA', na=False)]

print(f"   ✓ {len(co2_df)} registros de CO2")

# 2. Cargar cultivos transitorios
print("\n2️⃣ Cargando cultivos transitorios...")
ct = pd.read_excel('data/cultivos_transitorios.xlsx')

# Encontrar columnas de años
year_cols = [col for col in ct.columns if str(col).isdigit() and 1900 < int(col) < 2100]
print(f"   Años disponibles: {min(year_cols)} - {max(year_cols)}")

# Transformar a formato largo
ct_long = ct.melt(
    id_vars=['TIPO', 'Departamento'],
    value_vars=year_cols,
    var_name='ANO',
    value_name='HECTAREAS'
)

ct_long['ANO'] = pd.to_numeric(ct_long['ANO'])
ct_long['HECTAREAS'] = pd.to_numeric(ct_long['HECTAREAS'], errors='coerce')
ct_long = ct_long.dropna(subset=['HECTAREAS'])
ct_long['TIPO_CULTIVO'] = 'TRANSITORIO'
ct_long = ct_long.rename(columns={'TIPO': 'CULTIVO', 'Departamento': 'REGION'})
ct_long['REGION'] = ct_long['REGION'].str.upper().str.strip()

print(f"   ✓ {len(ct_long)} registros")
print(f"   ✓ {ct_long['CULTIVO'].nunique()} cultivos diferentes")

# 3. Cargar cultivos permanentes  
print("\n3️⃣ Cargando cultivos permanentes...")
cp = pd.read_excel('data/cultivos_permanentes.xlsx')

# Encontrar columnas de años
year_cols_p = [col for col in cp.columns if str(col).isdigit() and 1900 < int(col) < 2100]

cp_long = cp.melt(
    id_vars=['Tipo', 'Departamento'],
    value_vars=year_cols_p,
    var_name='ANO',
    value_name='HECTAREAS'
)

cp_long['ANO'] = pd.to_numeric(cp_long['ANO'])
cp_long['HECTAREAS'] = pd.to_numeric(cp_long['HECTAREAS'], errors='coerce')
cp_long = cp_long.dropna(subset=['HECTAREAS'])
cp_long['TIPO_CULTIVO'] = 'PERMANENTE'
cp_long = cp_long.rename(columns={'Tipo': 'CULTIVO', 'Departamento': 'REGION'})
cp_long['REGION'] = cp_long['REGION'].str.upper().str.strip()

print(f"   ✓ {len(cp_long)} registros")
print(f"   ✓ {cp_long['CULTIVO'].nunique()} cultivos diferentes")

# 4. Combinar ambos tipos
print("\n4️⃣ Combinando datos de cultivos...")
all_crops = pd.concat([ct_long, cp_long], ignore_index=True)
print(f"   ✓ {len(all_crops)} registros totales")

# 5. Agrupar por región, año y cultivo
print("\n5️⃣ Agrupando datos...")
crops_grouped = all_crops.groupby(['ANO', 'REGION', 'CULTIVO', 'TIPO_CULTIVO'])[' HECTAREAS'].sum().reset_index()

# 6. Agrupar CO2 por región y año
co2_grouped = co2_df.groupby(['ANO', 'REGION'])['VALOR_F'].sum().reset_index()

# 7. Merge
print("\n6️⃣ Combinando con datos de CO2...")
merged = crops_grouped.merge(co2_grouped, on=['ANO', 'REGION'], how='inner')
print(f"   ✓ {len(merged)} registros combinados")

if len(merged) > 0:
    # 8. Análisis por cultivo
    print("\n7️⃣ Análisis por cultivo:")
    print("=" * 60)
    
    crop_analysis = merged.groupby(['CULTIVO', 'TIPO_CULTIVO']).agg({
        'VALOR_F': 'sum',
        'HECTAREAS': 'sum'
    }).reset_index()
    
    crop_analysis['CO2_POR_HA'] = crop_analysis['VALOR_F'] / crop_analysis['HECTAREAS']
    crop_analysis = crop_analysis.sort_values('VALOR_F', ascending=False)
    
    print("\n🏆 TOP 10 CULTIVOS MÁS CONTAMINANTES (por emisiones totales):")
    print(crop_analysis.head(10)[['CULTIVO', 'TIPO_CULTIVO', 'VALOR_F', 'HECTAREAS']].to_string(index=False))
    
    print("\n🌡️ TOP 10 CULTIVOS MÁS CONTAMINANTES (por hectárea):")
    top_per_ha = crop_analysis.sort_values('CO2_POR_HA', ascending=False)
    print(top_per_ha.head(10)[['CULTIVO', 'TIPO_CULTIVO', 'CO2_POR_HA', 'HECTAREAS']].to_string(index=False))
    
    # 9. Comparación transitorios vs permanentes
    print("\n8️⃣ Comparación: TRANSITORIOS vs PERMANENTES:")
    print("=" * 60)
    
    type_comparison = merged.groupby('TIPO_CULTIVO').agg({
        'VALOR_F': ['sum', 'mean'],
        'HECTAREAS': 'sum',
        'CULTIVO': 'nunique'
    })
    print(type_comparison)
    
    # 10. Guardar resultados
    print("\n9️⃣ Guardando resultados...")
    merged.to_csv('data/merged_crops_co2.csv', index=False)
    crop_analysis.to_csv('data/crop_emissions_analysis.csv', index=False)
    
    print("   ✓ data/merged_crops_co2.csv")
    print("   ✓ data/crop_emissions_analysis.csv")
else:
    print("\n⚠️  No se pudieron combinar los datos. Verifica las columnas de región y año.")

print("\n" + "=" * 60)
print("✅ Análisis completado")
print("=" * 60)
