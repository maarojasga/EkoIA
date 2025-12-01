"""
Script de Configuración Inicial
Ejecuta esto la primera vez para configurar todo automáticamente
"""
import os
import sys
import subprocess

def print_header(text):
    """Imprime un header bonito"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def install_dependencies():
    """Instala las dependencias necesarias"""
    print_header("1. INSTALANDO DEPENDENCIAS")
    
    try:
        print("Instalando paquetes de requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencias instaladas correctamente")
        return True
    except Exception as e:
        print(f"⚠ Error instalando dependencias: {e}")
        print("\nIntenta manualmente:")
        print("  pip install -r requirements.txt")
        return False

def check_data_directory():
    """Verifica y crea el directorio de datos"""
    print_header("2. VERIFICANDO DIRECTORIO DE DATOS")
    
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"✓ Directorio '{data_dir}/' creado")
    else:
        print(f"✓ Directorio '{data_dir}/' existe")
    
    # Verificar si hay archivos
    files = os.listdir(data_dir)
    if files:
        print(f"\nArchivos encontrados en data/:")
        for f in files:
            size = os.path.getsize(os.path.join(data_dir, f))
            print(f"  - {f} ({size:,} bytes)")
    else:
        print("\n⚠ No hay archivos en data/")
        print("\nPara agregar datos:")
        print("  1. Copia tu archivo Excel/CSV a la carpeta 'data/'")
        print("  2. Renómbralo a 'factores_limpios.csv' o 'factores_limpios.xlsx'")
        print("  3. O usa el endpoint /data/upload cuando el servidor esté corriendo")
    
    return True

def check_models_directory():
    """Verifica y crea el directorio de modelos"""
    print_header("3. VERIFICANDO DIRECTORIO DE MODELOS")
    
    models_dir = "models"
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        print(f"✓ Directorio '{models_dir}/' creado")
    else:
        print(f"✓ Directorio '{models_dir}/' existe")
    
    # Verificar si hay modelos guardados
    model_files = [f for f in os.listdir(models_dir) if f.endswith('.pkl')]
    if model_files:
        print(f"\nModelos encontrados:")
        for f in model_files:
            print(f"  - {f}")
    else:
        print("\n⚠ No hay modelos entrenados")
        print("\nPara entrenar modelos:")
        print("  POST http://localhost:8000/model/train")
    
    return True

def test_imports():
    """Verifica que los imports funcionen"""
    print_header("4. VERIFICANDO IMPORTS")
    
    packages = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy'),
        ('sklearn', 'Scikit-learn'),
        ('pydantic', 'Pydantic'),
        ('openpyxl', 'OpenPyXL'),
    ]
    
    all_ok = True
    for package, name in packages:
        try:
            __import__(package)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} - FALTA")
            all_ok = False
    
    if not all_ok:
        print("\n⚠ Algunos paquetes faltan. Ejecuta:")
        print("  pip install -r requirements.txt")
        return False
    
    return True

def show_next_steps():
    """Muestra los próximos pasos"""
    print_header("5. PRÓXIMOS PASOS")
    
    print("¡Configuración completa! Ahora puedes:\n")
    
    print("1️⃣  INICIAR EL SERVIDOR:")
    print("   uvicorn app.main:app --reload\n")
    
    print("2️⃣  ABRIR LA DOCUMENTACIÓN:")
    print("   http://localhost:8000/docs\n")
    
    print("3️⃣  VERIFICAR SALUD:")
    print("   curl http://localhost:8000/health\n")
    
    print("4️⃣  SUBIR TUS DATOS (si no están en data/):")
    print("   Ir a http://localhost:8000/docs")
    print("   Buscar POST /data/upload")
    print("   Subir tu archivo Excel/CSV\n")
    
    print("5️⃣  ENTRENAR EL MODELO:")
    print("   POST http://localhost:8000/model/train\n")
    
    print("6️⃣  PROBAR EL DEMO:")
    print("   python examples/complete_demo.py\n")
    
    print("="*60)
    print("📚 Documentación completa en: LEEME_PRIMERO.md")
    print("="*60)

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("  🚀 CONFIGURACIÓN INICIAL - CO2 MICROSERVICE v2.0")
    print("="*60)
    
    # Cambiar al directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"\nDirectorio de trabajo: {os.getcwd()}\n")
    
    steps = [
        install_dependencies,
        check_data_directory,
        check_models_directory,
        test_imports,
    ]
    
    success = True
    for step in steps:
        if not step():
            success = False
    
    if success:
        show_next_steps()
        print("\n✅ ¡Todo listo para empezar!\n")
        
        # Preguntar si quiere iniciar el servidor
        try:
            response = input("¿Quieres iniciar el servidor ahora? (s/n): ").strip().lower()
            if response in ['s', 'si', 'sí', 'y', 'yes']:
                print("\nIniciando servidor...")
                print("Presiona CTRL+C para detener\n")
                subprocess.call([sys.executable, "-m", "uvicorn", "app.main:app", "--reload"])
        except KeyboardInterrupt:
            print("\n\nServidor detenido.")
    else:
        print("\n⚠ Hubo algunos problemas. Revisa los mensajes arriba.")
        print("Puedes continuar manualmente siguiendo LEEME_PRIMERO.md\n")

if __name__ == "__main__":
    main()