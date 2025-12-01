import pandas as pd

print("Inspeccionando cultivos_transitorios.xlsx...")
df = pd.read_excel('data/cultivos_transitorios.xlsx', nrows=3)

print("\nColumnas (primeras 20):")
for i, col in enumerate(df.columns[:20]):
    print(f"{i}: '{col}' (tipo: {type(col).__name__})")

print("\nPrimeras filas:")
print(df.iloc[:, :10])
