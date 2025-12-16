#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test rapide du symptom_matching avec disease_symptom_matrix.csv
Exécute directement via le code Python, sans passer par l'API HTTP
"""

import sys
import os
import json
import pandas as pd
import numpy as np

# Ajouter le backend au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from analyses.symptom_matching import SymptomMatchingAnalyzer

print("\n" + "="*60)
print("TEST: SymptomMatchingAnalyzer avec disease_symptom_matrix.csv")
print("="*60)

# Charger les données
csv_path = os.path.join(os.path.dirname(__file__), 'disease_symptom_matrix.csv')
print(f"\n[LOAD] Chargement: {csv_path}")

try:
    df = pd.read_csv(csv_path)
    print(f"[OK] CSV charge: shape={df.shape}")
    print(f"     Colonnes: {list(df.columns[:5])} ... ({len(df.columns)} total)")
    print(f"     Dtypes uniques: {df.dtypes.unique()}")
    
    # Vérifier les valeurs uniques dans la première colonne (cible supposée)
    first_col = df.columns[0]
    print(f"\n     Premiere colonne '{first_col}':")
    print(f"       - Type: {df[first_col].dtype}")
    print(f"       - Unique values: {df[first_col].nunique()}")
    print(f"       - Sample: {df[first_col].head(3).tolist()}")
    
    # Vérifier les valeurs dans la deuxième colonne (feature supposée)
    if len(df.columns) > 1:
        second_col = df.columns[1]
        print(f"\n     Deuxieme colonne '{second_col}':")
        print(f"       - Type: {df[second_col].dtype}")
        print(f"       - Unique values: {df[second_col].nunique()}")
        print(f"       - Sample: {df[second_col].head(3).tolist()}")
    
except Exception as e:
    print(f"[ERROR] Chargement: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Créer l'analyseur
print(f"\n[INIT] Initialisation du SymptomMatchingAnalyzer...")
try:
    analyzer = SymptomMatchingAnalyzer(df)
    print("[OK] Analyzeur cree")
except Exception as e:
    print(f"[ERROR] Analyzeur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Configurer l'analyse
print(f"\n[CONFIG] Configuration de l'analyse...")
config = {
    'disease_column': 'name',  # Utiliser 'name' comme cible (428 maladies uniques au lieu de 431 ID uniques)
    'symptom_columns': df.columns[2:],  # Ignorer 'id' et 'name', utiliser le reste
    'model': 'all',
    'test_size': 0.2,
    'top_predictions': 5
}
print(f"        - Target: {config['disease_column']}")
print(f"        - Features: {len(config['symptom_columns'])} colonnes")

# Exécuter
print(f"\n[RUN] Execution de perform_analysis()...")
try:
    results = analyzer.perform_analysis(config)
    
    print(f"\n[RESULTS]:")
    print(f"   - success: {results['success']}")
    print(f"   - total_diseases: {results['total_diseases']}")
    print(f"   - total_symptoms: {results['total_symptoms']}")
    
    # Lister les analyses disponibles
    analyses = [k for k in results.keys() if k not in ['success', 'total_diseases', 'total_symptoms', 'disease_column', 'model_type']]
    non_null = [a for a in analyses if results[a] is not None]
    print(f"\n   Analyses disponibles ({len(non_null)} non-nulles):")
    for analysis in analyses:
        if results[analysis] is not None:
            if isinstance(results[analysis], dict):
                keys_str = ', '.join(list(results[analysis].keys())[:5])
                print(f"     [OK] {analysis}: dict avec {len(results[analysis])} keys")
            elif isinstance(results[analysis], list):
                print(f"     [OK] {analysis}: list avec {len(results[analysis])} items")
            else:
                print(f"     [OK] {analysis}: {type(results[analysis]).__name__}")
    
    # Vérifier les erreurs
    if not results['success'] and 'error' in results:
        print(f"\n   [WARN] Error: {results['error']}")
    
    print(f"\n[SUCCESS] Test reussi!")
    
except Exception as e:
    print(f"[ERROR] Analyse: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
