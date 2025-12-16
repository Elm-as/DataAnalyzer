#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test du endpoint /analyze/symptom-matching avec disease_symptom_matrix.csv
Simule ce que le frontend envoie exactement
"""

import sys
import os
import json
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from analyses.symptom_matching import SymptomMatchingAnalyzer

print("\n" + "="*70)
print("TEST ENDPOINT: /analyze/symptom-matching")
print("Simulation: Frontend envoie disease_symptom_matrix.csv")
print("="*70)

# Charger le CSV
csv_path = os.path.join(os.path.dirname(__file__), 'disease_symptom_matrix.csv')
print(f"\n[LOAD] Chargement du CSV...")
df = pd.read_csv(csv_path)
print(f"[OK] Shape: {df.shape}")

# Convertir en format que le frontend enverrait
data = df.to_dict('records')  # Liste de dicts (rows)
columns = df.columns.tolist()  # Liste de noms de colonnes

print(f"\n[CONFIG] Configuration comme le frontend l'enverrait:")

# Cette config correspond à ce que AnalysisOptions.tsx envoie
config = {
    'disease_column': 'name',  # Target: colonne 'name'
    'symptom_columns': columns[2:],  # Features: tout sauf 'id' et 'name'
    'model': 'all',
    'test_size': 0.2,
    'top_predictions': 5,
}

print(f"  - disease_column: {config['disease_column']}")
print(f"  - symptom_columns: {len(config['symptom_columns'])} colonnes")
print(f"  - model: {config['model']}")

# Créer l'analyseur
analyzer = SymptomMatchingAnalyzer(df)

# Exécuter l'analyse
print(f"\n[RUN] Execution de perform_analysis()...")
results = analyzer.perform_analysis(config)

# Vérifier les résultats
print(f"\n[RESULTS]:")
print(f"  success: {results['success']}")

if results['success']:
    print(f"\n[ANALYSES COMPLETED]:")
    for key in ['tfidf_analysis', 'bernoulli_nb', 'multinomial_nb', 
                'symptom_importance', 'disease_similarity', 'top_symptoms_per_disease']:
        if results.get(key):
            if isinstance(results[key], dict):
                print(f"  - {key}: OK (dict with {len(results[key])} keys)")
            elif isinstance(results[key], list):
                print(f"  - {key}: OK (list with {len(results[key])} items)")
    
    # Afficher un aperçu du TF-IDF
    if results.get('tfidf_analysis'):
        tfidf = results['tfidf_analysis']
        print(f"\n[TFIDF SAMPLE]:")
        print(f"  analysis_type: {tfidf.get('analysis_type')}")
        print(f"  total_symptoms: {tfidf.get('total_symptoms')}")
        print(f"  total_diseases: {tfidf.get('total_diseases')}")
        if tfidf.get('top_symptoms_global'):
            print(f"  top 3 symptoms:")
            for i, sym in enumerate(tfidf['top_symptoms_global'][:3]):
                print(f"    {i+1}. {sym['symptom']}: score={sym['tfidf_score']}")
    
    print(f"\n[SUCCESS] Endpoint fonctionne correctement!")
else:
    print(f"\n[ERROR] {results.get('error', 'Unknown error')}")
    import traceback
    if 'error' in results:
        print(f"Details: {results['error']}")

print("\n" + "="*70)
