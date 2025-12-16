"""
Test rapide de l'endpoint symptom-matching
"""
import requests
import pandas as pd
import json

def test_symptom_matching():
    print("🧪 Test endpoint /analyze/symptom-matching")
    print("=" * 60)
    
    # Charger disease_symptom_matrix.csv
    print("\n[1/3] Chargement des données...")
    df = pd.read_csv('disease_symptom_matrix.csv')
    print(f"   ✅ {df.shape[0]} maladies × {df.shape[1]} colonnes")
    
    # Préparer les données pour l'API
    print("\n[2/3] Préparation des données...")
    data = df.to_dict('records')
    
    # Identifier les colonnes
    symptom_cols = [col for col in df.columns if col not in ['id', 'name']]
    
    config = {
        'disease_column': 'name',
        'symptom_columns': symptom_cols,
        'model': 'all',  # TF-IDF + Bernoulli + Multinomial
        'test_size': 0.2,
        'top_predictions': 5
    }
    
    print(f"   ✅ {len(symptom_cols)} colonnes de symptômes")
    print(f"   ✅ Configuration: {config['model']}")
    
    # Appeler l'endpoint
    print("\n[3/3] Envoi de la requête au backend...")
    try:
        response = requests.post(
            'http://localhost:5000/analyze/symptom-matching',
            json={'data': data, 'config': config},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ SUCCÈS!")
            print("=" * 60)
            print(f"Total maladies: {result.get('total_diseases', 'N/A')}")
            print(f"Total symptômes: {result.get('total_symptoms', 'N/A')}")
            
            if result.get('bernoulli_nb'):
                print(f"\n🎲 Bernoulli Naive Bayes:")
                print(f"   Accuracy: {result['bernoulli_nb'].get('accuracy', 'N/A')}")
                print(f"   Classes: {result['bernoulli_nb'].get('n_classes', 'N/A')}")
            
            if result.get('multinomial_nb'):
                print(f"\n📈 Multinomial Naive Bayes:")
                print(f"   Accuracy: {result['multinomial_nb'].get('accuracy', 'N/A')}")
                print(f"   CV Accuracy: {result['multinomial_nb'].get('cv_mean_accuracy', 'N/A')}")
            
            if result.get('tfidf_analysis'):
                tfidf = result['tfidf_analysis']
                print(f"\n🔍 TF-IDF Analysis:")
                print(f"   Features: {tfidf.get('total_features', 'N/A')}")
                print(f"   Sparsity: {tfidf.get('sparsity', 'N/A')}")
                
                if tfidf.get('top_symptoms_global'):
                    print(f"\n   Top 5 symptômes:")
                    for i, sym in enumerate(tfidf['top_symptoms_global'][:5], 1):
                        print(f"      {i}. {sym['symptom']}: {sym['tfidf_score']}")
            
            print("\n" + "=" * 60)
            print("✅ Test réussi!")
            
        else:
            print(f"\n❌ ERREUR HTTP {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERREUR: Backend non disponible sur http://localhost:5000")
        print("   Lancez le backend avec: python backend/app.py")
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_symptom_matching()
