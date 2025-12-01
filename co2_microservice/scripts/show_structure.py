"""
Script para mostrar la estructura completa de los archivos de cultivos
"""
import pandas as pd

print("=" * 80)
print("ESTRUCTURA DE ARCHIVOS DE CULTIVOS")
print("=" * 80)

# Cultivos transitorios
print("\n📄 CULTIVOS TRANSITORIOS (primeras 10 filas, primeras 15 columnas)")
print("-" * 80)
df_t = pd.read_excel('data/cultivos_transitorios.xlsx', nrows=10)
print(df_t.iloc[:, :15])

print("\n\nColumnas completas:")
for i, col in enumerate(df_t.columns[:30]):
    print(f"  {i:2d}: {repr(col)}")

# Cultivos permanentes
print("\n\n📄 CULTIVOS PERMANENTES (primeras 10 filas, primeras 15 columnas)")
print("-" * 80)
df_p = pd.read_excel('data/cultivos_permanentes.xlsx', nrows=10)
print(df_p.iloc[:, :15])

print("\n\nColumnas completas:")
for i, col in enumerate(df_p.columns[:30]):
    print(f"  {i:2d}: {repr(col)}")

print("\n" + "=" * 80)
print("Revisa la salida arriba para identificar dónde están los años")
print("=" * 80)
