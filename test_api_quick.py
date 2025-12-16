"""Test endpoint symptom-matching avec disease_symptom_matrix.csv"""
import pandas as pd
import requests
import json

# Charger le CSV
df = pd.read_csv('disease_symptom_matrix.csv')
print(f'✅ CSV chargé: {df.shape[0]} × {df.shape[1]}')
print(f'Colonnes: {list(df.columns[:10])}...')
print(f'Types: {df.dtypes.unique()}')

# Tester l'endpoint symptom-matching
print('\n🧪 Test endpoint symptom-matching...')
try:
    # Préparer les données
    data = df.to_dict('records')
    columns = []
    for col in df.columns:
        col_type = 'number' if pd.api.types.is_numeric_dtype(df[col]) else ('boolean' if df[col].nunique() <= 2 else 'categorical')
        columns.append({'name': col, 'type': col_type})
    
    payload = {
        'data': data,
        'columns': columns,
        'config': {}
    }
    
    response = requests.post('http://localhost:5000/analyze/symptom-matching', json=payload)
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        print(f'✅ Endpoint répondait bien!')
        analyses_keys = list(result.get('analyses', {}).keys())
        print(f'Analyses keys: {analyses_keys}')
        
        # Vérifier symptomMatching
        if 'symptomMatching' in result.get('analyses', {}):
            sm = result['analyses']['symptomMatching']
            print(f'\n✅ symptomMatching présent!')
            print(f'   Keys: {list(sm.keys())}')
            if 'tfidf_analysis' in sm:
                print(f'   TF-IDF: {list(sm["tfidf_analysis"].keys())}')
        else:
            print(f'\n❌ symptomMatching PAS dans résultats')
            print(f'   Analyses disponnibles: {analyses_keys}')
    else:
        print(f'❌ Erreur: {response.text[:500]}')
        
except Exception as e:
    print(f'❌ Erreur connexion: {e}')
    print('💡 Backend lancé? Essayez: npm run backend')
