import pandas as pd
import requests
import json

# Charger le dataset de test
df = pd.read_csv('disease_symptom_matrix.csv')
print(f"Dataset chargé: {df.shape}")

# Configuration de base
base_url = "http://localhost:5000"

# Test 1: Symptom Matching
print("\n[TEST 1] Symptom Matching...")
try:
    response = requests.post(
        f"{base_url}/analyze/symptom-matching",
        json={
            "data": df.head(10).to_dict(orient='records'),
            "config": {"target": "Disease"}
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        print("✅ Succès!")
except Exception as e:
    print(f"❌ Exception: {e}")

# Test 2: Regression
print("\n[TEST 2] Regression...")
try:
    response = requests.post(
        f"{base_url}/analyze/regression",
        json={
            "data": df.head(10).to_dict(orient='records'),
            "config": {
                "target": "Disease",
                "features": list(df.columns[1:11])
            }
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        print("✅ Succès!")
except Exception as e:
    print(f"❌ Exception: {e}")

# Test 3: Classification
print("\n[TEST 3] Classification...")
try:
    response = requests.post(
        f"{base_url}/analyze/classification",
        json={
            "data": df.head(10).to_dict(orient='records'),
            "config": {
                "target": "Disease",
                "features": list(df.columns[1:11])
            }
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        print("✅ Succès!")
except Exception as e:
    print(f"❌ Exception: {e}")

# Test 4: Data Cleaning
print("\n[TEST 4] Data Cleaning...")
try:
    response = requests.post(
        f"{base_url}/clean/data",
        json={
            "data": df.head(10).to_dict(orient='records'),
            "config": {
                "handle_missing": "mean",
                "handle_outliers": "clip",
                "outlier_method": "iqr"
            }
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        print("✅ Succès!")
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n=== Tests terminés ===")
