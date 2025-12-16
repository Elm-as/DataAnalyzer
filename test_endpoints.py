"""
Test des nouveaux endpoints: /validate-data et /clean-data
"""
import pandas as pd
import json
import sys
import os

# Ajouter backend au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_validate_data_endpoint():
    """Test de l'endpoint /validate-data"""
    print("=" * 60)
    print("🧪 TEST: /validate-data Endpoint")
    print("=" * 60)
    
    try:
        # Importer les modules Flask et validation
        from app import app
        
        # Créer un client de test
        client = app.test_client()
        
        # Créer des données de test
        test_data = {
            'id': range(1, 11),
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry', 'Iris', 'Jack'],
            'age': [25, 30, None, 28, 32, 29, None, 31, 27, 26],
            'salary': [50000, 60000, 55000, 65000, 70000, 58000, 62000, 75000, 52000, 61000],
            'category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B', 'A', 'C']
        }
        
        df = pd.DataFrame(test_data)
        
        # Préparer la requête
        payload = {
            'data': df.to_dict('records'),
            'columns': list(df.columns)
        }
        
        # Envoyer la requête
        response = client.post(
            '/validate-data',
            json=payload,
            content_type='application/json'
        )
        
        print(f"\n✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            report = response.get_json()
            print(f"✅ Validation réussie")
            print(f"  - Complétude globale: {report['quality'].get('completeness', 'N/A')}%")
            print(f"  - Colonnes analysées: {len(report['columnAnalysis'])}")
            print(f"  - Problèmes identifiés: {len(report['problematicColumns'])}")
            print(f"✅ Endpoint /validate-data fonctionne")
            return True
        else:
            print(f"❌ Erreur: {response.get_json()}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_clean_data_endpoint():
    """Test de l'endpoint /validate-and-clean"""
    print("\n" + "=" * 60)
    print("🧪 TEST: /validate-and-clean Endpoint")
    print("=" * 60)
    
    try:
        # Importer les modules Flask et validation
        from app import app
        
        # Créer un client de test
        client = app.test_client()
        
        # Créer des données de test avec N/A et colonnes vides
        test_data = {
            'id': range(1, 11),
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry', 'Iris', 'Jack'],
            'age': [25, 30, None, 28, 32, 29, None, 31, 27, 26],
            'salary': [50000, 60000, 55000, 65000, 70000, 58000, 62000, 75000, 52000, 61000],
            'empty_col': [None] * 10,
            'category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B', 'A', 'C']
        }
        
        df = pd.DataFrame(test_data)
        
        # Préparer la requête
        payload = {
            'data': df.to_dict('records'),
            'config': {
                'remove_empty_columns': True,
                'remove_index_columns': True,
                'remove_duplicates': True,
                'handle_missing': 'drop',
                'max_na_percentage': 80
            }
        }
        
        # Envoyer la requête
        response = client.post(
            '/validate-and-clean',
            json=payload,
            content_type='application/json'
        )
        
        print(f"\n✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.get_json()
            print(f"✅ Nettoyage réussi")
            print(f"  - Lignes supprimées: {result['removed_rows']}")
            print(f"  - Colonnes supprimées: {result['removed_columns']}")
            print(f"  - Données restantes: {len(result['data'])} lignes")
            print(f"✅ Endpoint /validate-and-clean fonctionne")
            return True
        else:
            print(f"❌ Erreur: {response.get_json()}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def main():
    print("\n" + "╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  🧪 TESTS DES ENDPOINTS BACKEND  🧪".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝\n")
    
    tests_passed = 0
    tests_total = 2
    
    if test_validate_data_endpoint():
        tests_passed += 1
    
    if test_clean_data_endpoint():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"✅ {tests_passed}/{tests_total} endpoints testés avec succès")
    
    if tests_passed == tests_total:
        print("\n🎉 Tous les endpoints fonctionnent ! Intégration réussie.")
    else:
        print("\n⚠️ Certains endpoints ne fonctionnent pas. Vérifier l'installation.")

if __name__ == '__main__':
    main()
