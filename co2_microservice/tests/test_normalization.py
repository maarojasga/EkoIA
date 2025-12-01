import pandas as pd
import sys
import os
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).resolve().parent.parent)
sys.path.append(project_root)

from utils.data_analysis import CO2DataAnalyzer

def test_normalization():
    print("Testing REGION normalization...")
    
    # Create dummy data with mixed case and accents
    data = {
        'ANO': [2020, 2020, 2020, 2020],
        'REGION': ['Bogotá', 'BOGOTA', 'bogota', 'Amazonía'],
        'VALOR_F': [100, 200, 300, 400],
        'UNIDAD_F': ['GefCO2', 'GefCO2', 'GefCO2', 'GefCO2']
    }
    df = pd.DataFrame(data)
    
    # Initialize analyzer
    analyzer = CO2DataAnalyzer(df)
    
    # Check available regions
    regions = analyzer.get_available_regions()
    print(f"Available regions: {regions}")
    
    # Expected: ['AMAZONIA', 'BOGOTA']
    expected = ['AMAZONIA', 'BOGOTA']
    
    if regions == expected:
        print("✓ Normalization successful!")
        return True
    else:
        print(f"❌ Normalization failed. Expected {expected}, got {regions}")
        return False

if __name__ == "__main__":
    if test_normalization():
        sys.exit(0)
    else:
        sys.exit(1)
