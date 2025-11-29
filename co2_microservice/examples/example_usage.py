import requests
import random
from datetime import datetime

BASE_URL = "http://localhost:8000"

def main():
    # 1. Check Health
    print("Checking health...")
    resp = requests.get(f"{BASE_URL}/health")
    print(resp.json())

    # 2. Add Data
    print("\nAdding data...")
    for _ in range(10):
        data = {
            "timestamp": datetime.now().isoformat(),
            "co2_level": random.uniform(400, 1200),
            "temperature": random.uniform(20, 30),
            "humidity": random.uniform(30, 60),
            "occupancy": random.randint(0, 50)
        }
        requests.post(f"{BASE_URL}/data", json=data)
    print("Data added.")

    # 3. Train Model
    print("\nTraining model...")
    resp = requests.post(f"{BASE_URL}/model/train")
    print(resp.json())

    # 4. Predict
    print("\nPredicting...")
    req = {
        "features": [
            [25.0, 45.0, 10],
            [22.0, 50.0, 5]
        ]
    }
    resp = requests.post(f"{BASE_URL}/predict", json=req)
    print(resp.json())

    # 5. Get Stats
    print("\nGetting stats...")
    resp = requests.get(f"{BASE_URL}/analysis/stats")
    print(resp.json())

if __name__ == "__main__":
    main()
