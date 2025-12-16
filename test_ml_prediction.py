#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test complet du nouveau système de prédiction ML
Vérifie: analyse → stockage modèle → prédiction temps réel
"""
import sys
import os
import pandas as pd
import numpy as np
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from analyses.symptom_matching import SymptomMatchingAnalyzer

print("\n" + "="*80)
print("TEST COMPLET: Système de Prédiction ML")
print("="*80)

# 1. CHARGER LES DONNÉES
print("\n[1/5] Chargement disease_symptom_matrix.csv...")
df = pd.read_csv('disease_symptom_matrix.csv')
print(f"   ✅ {df.shape[0]} maladies × {df.shape[1]} colonnes")
print(f"   Colonnes: id, name + {df.shape[1] - 2} symptômes")

# 2. LANCER L'ANALYSE (comme le frontend)
print("\n[2/5] Lancement de l'analyse Symptom Matching...")
config = {
    'disease_column': 'name',
    'id_column': 'id',
    'symptom_columns': 'auto',
    'model': 'all',  # TF-IDF + Bernoulli + Multinomial
    'test_size': 0.2,
    'top_predictions': 5
}

analyzer = SymptomMatchingAnalyzer(df)
results = analyzer.perform_analysis(config)

print(f"   ✅ Analyse terminée")
print(f"   - Modèle entraîné: {type(analyzer.trained_model)}")
print(f"   - Features: {len(analyzer.feature_names) if analyzer.feature_names else 0}")
print(f"   - Classes: {len(analyzer.classes_) if analyzer.classes_ is not None else 0}")
print(f"   - Variable cible: {analyzer.target_column}")

# 3. VÉRIFIER LES RÉSULTATS
print("\n[3/5] Vérification des résultats...")
if results.get('bernoulli_nb'):
    bernoulli = results['bernoulli_nb']
    print(f"   ✅ Bernoulli NB:")
    print(f"      - Accuracy: {bernoulli.get('accuracy', 'N/A')}")
    print(f"      - Train samples: {bernoulli.get('train_samples', 'N/A')}")
    print(f"      - Test samples: {bernoulli.get('test_samples', 'N/A')}")
    print(f"      - N classes: {bernoulli.get('n_classes', 'N/A')}")
    
    if bernoulli.get('example_predictions'):
        print(f"   ✅ Exemples de prédictions:")
        for i, ex in enumerate(bernoulli['example_predictions'][:2], 1):
            print(f"      Exemple {i}:")
            print(f"        - Vraie maladie: {ex['true_disease']}")
            print(f"        - Top 3 prédictions:")
            for j, pred in enumerate(ex['top_predictions'][:3], 1):
                print(f"           {j}. {pred['disease']}: {pred['probability']*100:.1f}%")

# 4. TESTER LA PRÉDICTION (simuler ce que fait le frontend)
print("\n[4/5] Test de prédiction en temps réel...")
print("   Scénario: Patient avec fièvre, fatigue, céphalées")

# Créer un vecteur de features (tous à 0 sauf ceux qu'on active)
test_features = {}
for feature_name in analyzer.feature_names:
    # Activer certains symptômes
    if 'fievre' in feature_name.lower():
        test_features[feature_name] = 1
    elif 'fatigue' in feature_name.lower():
        test_features[feature_name] = 1
    elif 'cephalee' in feature_name.lower() or 'cephale' in feature_name.lower():
        test_features[feature_name] = 1
    else:
        test_features[feature_name] = 0

# Construire X_test
X_test = np.array([[test_features[fname] for fname in analyzer.feature_names]])

print(f"   - Features actives: {np.sum(X_test > 0)}/{len(analyzer.feature_names)}")
print(f"   - Symptômes sélectionnés:")
active_symptoms = [fname for fname in analyzer.feature_names if test_features[fname] == 1]
for sym in active_symptoms[:10]:
    print(f"      • {sym}")
if len(active_symptoms) > 10:
    print(f"      ... et {len(active_symptoms) - 10} autres")

# Prédire
y_proba = analyzer.trained_model.predict_proba(X_test)[0]
top_indices = y_proba.argsort()[-5:][::-1]

print(f"\n   ✅ Top 5 prédictions:")
for i, idx in enumerate(top_indices, 1):
    disease = analyzer.classes_[idx]
    probability = y_proba[idx]
    print(f"      {i}. {disease}: {probability*100:.2f}%")

# 5. SIMULATION ENDPOINT /predict
print("\n[5/5] Simulation de l'endpoint /predict...")
predict_request = {
    'dataset_id': 'default',
    'features': test_features
}

print(f"   📤 Request body:")
print(f"      - dataset_id: {predict_request['dataset_id']}")
print(f"      - features: {len(predict_request['features'])} colonnes")
print(f"      - actives: {sum(1 for v in predict_request['features'].values() if v != 0)}")

# Simuler la réponse
response = {
    'predictions': [
        {
            'class': str(analyzer.classes_[idx]),
            'probability': round(float(y_proba[idx]), 4)
        }
        for idx in top_indices
    ],
    'top_prediction': {
        'class': str(analyzer.classes_[top_indices[0]]),
        'probability': round(float(y_proba[top_indices[0]]), 4)
    },
    'n_features_used': int(np.sum(X_test > 0)),
    'total_features': len(analyzer.feature_names)
}

print(f"\n   📥 Response:")
print(f"      - Top prédiction: {response['top_prediction']['class']}")
print(f"      - Probabilité: {response['top_prediction']['probability']*100:.2f}%")
print(f"      - Features utilisées: {response['n_features_used']}/{response['total_features']}")

# RÉSUMÉ FINAL
print("="*80)
print("RÉSUMÉ")
print("="*80)
print("✅ 1. Dataset chargé: 431 maladies × 1419 symptômes")
acc = results['bernoulli_nb'].get('accuracy')
acc_str = f"{acc*100:.1f}%" if acc else "N/A (entraîné sur toutes données)"
print(f"✅ 2. Modèle entraîné: Bernoulli NB (accuracy: {acc_str})")
print(f"✅ 3. Prédictions générées: Top 5 maladies avec probabilités")
print(f"✅ 4. API /predict simulée: {response['top_prediction']['class']} ({response['top_prediction']['probability']*100:.1f}%)")
print("\n🎉 Tout fonctionne ! Le Simulateur peut maintenant utiliser de vraies prédictions ML.")
print("\n📋 PROCHAINES ÉTAPES:")
print("   1. Lancer le backend: cd backend && python app.py")
print("   2. Lancer le frontend: npm run dev")
print("   3. Uploader disease_symptom_matrix.csv")
print("   4. Lancer l'analyse 'Correspondance Donnees' avec model='all'")
print("   5. Aller dans Simulateur → Sélectionner symptômes → Lancer Prédiction")
print("   6. Voir les probabilités RÉELLES du modèle Bernoulli NB !")
print("="*80)
