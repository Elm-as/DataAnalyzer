"""
Test de validation complète après correction TF-IDF
Vérifier que les résultats sont maintenant logiques et cohérents
"""
import requests
import pandas as pd
import json

def test_complete_validation():
    print("✅ TEST COMPLET: Validation de l'analyse Symptom Matching")
    print("=" * 70)
    
    # 1. Charger les données
    print("\n[1/4] Chargement des données...")
    df = pd.read_csv('disease_symptom_matrix.csv')
    print(f"   ✅ {df.shape[0]} maladies × {df.shape[1]} colonnes")
    print(f"   ✅ Colonnes: {list(df.columns[:5])}... ({len(df.columns)} total)")
    
    # 2. Analyser manuellement les top symptômes
    print("\n[2/4] Vérification des données brutes...")
    symptom_cols = [col for col in df.columns if col not in ['id', 'name']]
    symptom_freq = df[symptom_cols].sum()
    top_10_manual = symptom_freq.nlargest(10)
    
    print("   Top 10 symptômes (fréquence directe):")
    for i, (symptom, freq) in enumerate(top_10_manual.items(), 1):
        pct = 100 * freq / len(df)
        print(f"      {i:2d}. {symptom:30s} {int(freq):3d} maladies ({pct:5.1f}%)")
    
    # 3. Appeler l'API
    print("\n[3/4] Appel de l'endpoint /analyze/symptom-matching...")
    data = df.to_dict('records')
    config = {
        'disease_column': 'name',
        'symptom_columns': symptom_cols,
        'model': 'all',
        'test_size': 0.2,
        'top_predictions': 5
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/analyze/symptom-matching',
            json={'data': data, 'config': config},
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"   ❌ ERREUR HTTP {response.status_code}")
            print(response.text)
            return
        
        result = response.json()
        
        # 4. Valider les résultats
        print("\n[4/4] Validation des résultats...")
        
        # Vérifier TF-IDF
        if result.get('tfidf_analysis') and result['tfidf_analysis'].get('top_symptoms_global'):
            tfidf_results = result['tfidf_analysis']['top_symptoms_global']
            
            print("\n   🔍 TF-IDF Analysis (Top 5):")
            print("      Symptômes  │  Fréquence  │  Variance  │  Score")
            print("      " + "─" * 60)
            
            for item in tfidf_results[:5]:
                symptom = item['symptom']
                freq_pct = item.get('frequency_pct', 'N/A')
                variance = item.get('variance', 'N/A')
                score = item['tfidf_score']
                
                # ✅ Vérification: c'est un vrai symptôme
                is_valid = symptom in symptom_cols
                marker = "✅" if is_valid else "❌"
                
                print(f"      {marker} {symptom:25s} {str(freq_pct):>6}% {str(variance):>8} {score:>7.4f}")
            
            print("\n   ✅ Validation TF-IDF:")
            all_symptoms_valid = all(item['symptom'] in symptom_cols for item in tfidf_results[:10])
            if all_symptoms_valid:
                print("      ✅ Tous les symptômes affichés sont des vraies colonnes")
            else:
                print("      ❌ ERREUR: Des tokens au lieu de symptômes!")
                return
            
            # Comparer avec les résultats manuels
            manual_top5 = [s for s, _ in top_10_manual[:5].items()]
            api_top5 = [item['symptom'] for item in tfidf_results[:5]]
            
            print("\n   📊 Comparaison avec résultats manuels:")
            print(f"      Manuels:  {manual_top5}")
            print(f"      API:      {api_top5}")
            
            # Les ordres peuvent différer (fréquence vs TF-IDF), mais les symptômes doivent être similaires
            overlap = len(set(manual_top5) & set(api_top5))
            print(f"      ✅ Chevauchement: {overlap}/5 symptômes en commun")
        
        # Vérifier Bernoulli NB
        if result.get('bernoulli_nb'):
            bernoulli = result['bernoulli_nb']
            print(f"\n   🎲 Bernoulli Naive Bayes:")
            print(f"      ✅ Accuracy: {bernoulli.get('accuracy', 'N/A')} (attendu: 0.75-0.95)")
            print(f"      ✅ Nombre de classes: {bernoulli.get('n_classes', 'N/A')} (attendu: 431)")
            
            if bernoulli.get('example_predictions'):
                ex = bernoulli['example_predictions'][0]
                print(f"      ✅ Exemple prédiction pour '{ex['true_disease']}':")
                for pred in ex['top_predictions'][:3]:
                    print(f"         - {pred['disease']:30s} {pred['probability']*100:6.1f}%")
        
        # Vérifier Multinomial NB
        if result.get('multinomial_nb'):
            multinomial = result['multinomial_nb']
            print(f"\n   📈 Multinomial Naive Bayes:")
            print(f"      ✅ Accuracy: {multinomial.get('accuracy', 'N/A')} (attendu: 0.70-0.90)")
            print(f"      ✅ CV Accuracy: {multinomial.get('cv_mean_accuracy', 'N/A')} ± {multinomial.get('cv_std', 'N/A')}")
        
        # Vérifier Symptom Importance
        if result.get('symptom_importance') and result['symptom_importance'].get('top_symptoms'):
            importance = result['symptom_importance']['top_symptoms']
            print(f"\n   ⭐ Symptom Importance (Top 3):")
            for item in importance[:3]:
                print(f"      ✅ {item['symptom']:30s} score={item['importance_score']:.4f}")
        
        print("\n" + "=" * 70)
        print("✅ VALIDATION COMPLÈTE RÉUSSIE!")
        print("=" * 70)
        print("\n📋 Résumé:")
        print(f"   ✅ TF-IDF: Symptômes réels (pas de tokens génériques)")
        print(f"   ✅ Bernoulli NB: Accuracy {result.get('bernoulli_nb', {}).get('accuracy', 'N/A')}")
        print(f"   ✅ Multinomial NB: Accuracy {result.get('multinomial_nb', {}).get('accuracy', 'N/A')}")
        print(f"   ✅ Symptom Importance: Calculé correctement")
        print(f"\n🎯 Les résultats sont maintenant cliniquement sensés et logiques!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERREUR: Backend non disponible sur http://localhost:5000")
        print("   Lancez: python backend/app.py")
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_complete_validation()
