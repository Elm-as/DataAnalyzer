"""Test pour reproduire l'erreur 500 du backend"""
import requests
import pandas as pd
import json

# Charger un petit dataset pour test
df = pd.read_csv('disease_symptom_matrix.csv').head(10)  # Seulement 10 lignes

print("Dataset chargé:", df.shape)

# Préparer les données comme le frontend
data = df.to_dict('records')
columns = [{'name': col, 'type': 'boolean' if col not in ['id', 'name'] else 'text'} for col in df.columns]

# Test 1: Symptom Matching
print("\n[TEST 1] Symptom Matching...")
try:
    response = requests.post(
        'http://localhost:5000/analyze/symptom-matching',
        json={
            'data': data,
            'config': {
                'symptom_columns': 'auto'
            }
        },
        timeout=30
    )
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Erreur: {response.text}")
    else:
        print("✅ Succès!")
except Exception as e:
    print(f"❌ Exception: {e}")

# Test 2: Regression
print("\n[TEST 2] Regression...")
try:
    # Créer un dataset numérique simple
    df_num = pd.DataFrame({
        'x1': [1, 2, 3, 4, 5],
        'x2': [2, 4, 6, 8, 10],
        'target': [3, 5, 7, 9, 11]
    })
    
    response = requests.post(
        'http://localhost:5000/analyze/regression',
        json={
            'data': df_num.to_dict('records'),
            'config': {
                'target': 'target',
                'features': ['x1', 'x2']
            }
        },
        timeout=30
    )
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Erreur: {response.text}")
    else:
        print("✅ Succès!")
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n[FIN DES TESTS]")
