#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test complet du flow: Frontend -> Backend -> Résultats
Simule exactement ce que le frontend envoie et fait
"""

import sys
import os
import json
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from analyses.symptom_matching import SymptomMatchingAnalyzer

print("\n" + "="*70)
print("FULL INTEGRATION TEST")
print("Simulation: Frontend upload disease_symptom_matrix.csv")
print("="*70)

# 1. LOAD DATA (comme le ferait le frontend)
print("\n[STEP 1] Chargement du CSV...")
csv_path = os.path.join(os.path.dirname(__file__), 'disease_symptom_matrix.csv')
df = pd.read_csv(csv_path)
print(f"  OK: {df.shape[0]} rows, {df.shape[1]} columns")

# 2. CONVERT TO JSON (comme le ferait le frontend)
print("\n[STEP 2] Conversion en format API...")
data_json = df.to_dict('records')
columns_info = [
    {'name': col, 'type': 'boolean' if col not in ['id', 'name'] else 'string'}
    for col in df.columns
]
print(f"  OK: {len(data_json)} rows à envoyer")
print(f"  OK: {len(columns_info)} colonnes détectées")

# 3. PREPARE CONFIG (comme le ferait le frontend)
print("\n[STEP 3] Préparation de la configuration...")
# AnalysisOptions.tsx auto-détecte la meilleure target et features
# Cherche une colonne catégorique/string comme target (de préférence)
target_col = None
for col_name in ['name', 'disease', 'target', 'label']:
    if col_name in [c['name'] for c in columns_info]:
        target_col = next(c for c in columns_info if c['name'] == col_name)
        break

if not target_col:
    # Sinon prendre la première colonne string
    target_col = next((c for c in columns_info if c['type'] == 'string'), columns_info[0])

# Features = toutes les colonnes sauf target, id, et autres colonnes texte
exclude_for_features = [target_col['name'], 'id']
feature_cols = [c for c in columns_info if c['name'] not in exclude_for_features]

config = {
    'disease_column': target_col['name'],
    'symptom_columns': [c['name'] for c in feature_cols],
    'model': 'all',
    'test_size': 0.2,
    'top_predictions': 5,
}
print(f"  OK: Target={target_col['name']}, Features={len(config['symptom_columns'])}")

# 4. ANALYZE (comme ferait le backend)
print("\n[STEP 4] Execution de l'analyse...")
df_analyze = pd.DataFrame(data_json)
analyzer = SymptomMatchingAnalyzer(df_analyze)
results = analyzer.perform_analysis(config)

# 5. VALIDATE RESULTS
print("\n[STEP 5] Validation des résultats...")
required_fields = ['success', 'total_diseases', 'total_symptoms', 'tfidf_analysis']
missing = [f for f in required_fields if f not in results]
if missing:
    print(f"  ERROR: Champs manquants: {missing}")
    sys.exit(1)

if not results['success']:
    print(f"  ERROR: {results.get('error', 'Unknown error')}")
    sys.exit(1)

print(f"  OK: success={results['success']}")
print(f"  OK: total_diseases={results['total_diseases']}")
print(f"  OK: total_symptoms={results['total_symptoms']}")

# 6. DISPLAY RESULTS (comme ferait le frontend)
print("\n[STEP 6] Affichage des résultats...")

# Résumé
print(f"\n  === RESUME ===")
print(f"  Maladies: {results['total_diseases']}")
print(f"  Symptômes: {results['total_symptoms']}")

# TF-IDF
if results.get('tfidf_analysis') and results['tfidf_analysis'].get('top_symptoms_global'):
    print(f"\n  === TOP 5 SYMPTOMES (TF-IDF) ===")
    for i, sym in enumerate(results['tfidf_analysis']['top_symptoms_global'][:5], 1):
        print(f"  {i}. {sym['symptom']:30} score={sym['tfidf_score']:6.4f}")

# Bernoulli
if results.get('bernoulli_nb'):
    nb = results['bernoulli_nb']
    if nb.get('accuracy'):
        print(f"\n  === BERNOULLI NAIVE BAYES ===")
        print(f"  Accuracy: {nb['accuracy']*100:.1f}%")
        print(f"  Classes: {nb.get('n_classes', 'N/A')}")
    else:
        print(f"\n  === BERNOULLI NAIVE BAYES ===")
        print(f"  Note: {nb.get('note', 'Non disponible')}")

# Multinomial
if results.get('multinomial_nb'):
    nb = results['multinomial_nb']
    if nb.get('accuracy'):
        print(f"\n  === MULTINOMIAL NAIVE BAYES ===")
        print(f"  Accuracy: {nb['accuracy']*100:.1f}%")
    else:
        print(f"\n  === MULTINOMIAL NAIVE BAYES ===")
        print(f"  Note: {nb.get('note', 'Non disponible')}")

# Symptom Importance
if results.get('symptom_importance'):
    si = results['symptom_importance']
    print(f"\n  === SYMPTOM IMPORTANCE ===")
    print(f"  Symptoms analyzed: {si.get('total_symptoms', 'N/A')}")
    print(f"  Analysis type: {si.get('analysis_type', 'N/A')[:40]}...")

# Disease Similarity
if results.get('disease_similarity'):
    ds = results['disease_similarity']
    print(f"\n  === DISEASE SIMILARITY ===")
    print(f"  Disease pairs: {ds.get('total_pairs', 'N/A')}")
    print(f"  Unique diseases: {ds.get('unique_diseases', 'N/A')}")

# Top Symptoms Per Disease  
if results.get('top_symptoms_per_disease'):
    tspd = results['top_symptoms_per_disease']
    print(f"\n  === TOP SYMPTOMS PER DISEASE ===")
    print(f"  Diseases covered: {len(tspd)}")
    if tspd and tspd[0].get('disease'):
        print(f"  Example: {tspd[0]['disease'][:30]}...")

# 7. FINAL CHECK
print("\n" + "="*70)
print("[SUCCESS] FULL INTEGRATION TEST PASSED")
print("="*70)
print("\nLe systeme fonctionne correctement de bout en bout!")
print("Prochaine etape: Tester avec le frontend (npm run dev)")
print("\n")
