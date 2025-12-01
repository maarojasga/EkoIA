import requests
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint):
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        if response.status_code == 200:
            print(f"✓ {endpoint} passed")
            return True
        else:
            print(f"✗ {endpoint} failed with status {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"✗ {endpoint} failed with error: {e}")
        return False

def main():
    print("Verifying Dashboard Endpoints...")
    
    # Check health
    if not test_endpoint("/health"):
        print("Health check failed. Aborting.")
        sys.exit(1)
        
    # Check dashboard data
    if not test_endpoint("/dashboard/data"):
        print("Dashboard data check failed.")
        sys.exit(1)
        
    print("All checks passed!")

if __name__ == "__main__":
    main()
