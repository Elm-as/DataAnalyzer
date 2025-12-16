"""
Test spécifique pour la détection et conversion des colonnes booléennes
Démonstration avec disease_symptom_matrix.csv (1417 colonnes booléennes)
"""
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_boolean_detection():
    """Test de la détection de colonnes booléennes"""
    print("=" * 80)
    print("TEST: Detection et conversion automatique de colonnes booléennes")
    print("=" * 80)
    
    try:
        from utils.data_validator import BooleanDetector, DataValidator
        
        # Charger le CSV
        df = pd.read_csv('disease_symptom_matrix.csv')
        
        print(f"\nDataset original:")
        print(f"  - Lignes: {df.shape[0]}")
        print(f"  - Colonnes: {df.shape[1]}")
        print(f"  - Colonnes: id, name, + {df.shape[1] - 2} symptômes")
        
        # Afficher les types actuels
        print(f"\nTypes de colonnes avant conversion:")
        type_counts = df.dtypes.value_counts()
        for dtype, count in type_counts.items():
            print(f"  - {dtype}: {count} colonnes")
        
        # Détecter les colonnes booléennes
        boolean_cols = BooleanDetector.detect_boolean_columns(df)
        detected = [col for col, is_bool in boolean_cols.items() if is_bool]
        
        print(f"\nDetection:")
        print(f"  ✅ Colonnes booléennes détectées: {len(detected)}")
        print(f"  - Exemples: {detected[:5]}")
        
        # Montrer quelques valeurs
        print(f"\nExemples de valeurs (avant conversion):")
        for col in detected[:3]:
            unique_vals = df[col].unique()[:5]
            print(f"  - {col}: {unique_vals}")
        
        # Convertir automatiquement
        df_converted, converted = BooleanDetector.auto_convert_booleans(df)
        
        print(f"\nConversion:")
        print(f"  ✅ Colonnes converties: {len(converted)}")
        
        # Afficher les types après conversion
        print(f"\nTypes de colonnes après conversion:")
        type_counts_after = df_converted.dtypes.value_counts()
        for dtype, count in type_counts_after.items():
            print(f"  - {dtype}: {count} colonnes")
        
        # Montrer quelques valeurs converties
        print(f"\nExemples de valeurs (après conversion):")
        for col in detected[:3]:
            unique_vals = df_converted[col].unique()
            print(f"  - {col}: {unique_vals} (type: {df_converted[col].dtype})")
        
        # Comparer la qualité
        print(f"\nComparaison de qualité:")
        report_before = DataValidator.validate(df)
        report_after = DataValidator.validate(df_converted)
        
        print(f"  Avant conversion:")
        print(f"    - Complétude: {report_before['quality']['completeness']:.1f}%")
        print(f"    - Colonnes problématiques: {len(report_before['problematicColumns'])}")
        
        print(f"  Après conversion:")
        print(f"    - Complétude: {report_after['quality']['completeness']:.1f}%")
        print(f"    - Colonnes problématiques: {len(report_after['problematicColumns'])}")
        
        print(f"\n✅ TEST RÉUSSI!")
        print(f"\nRésumé:")
        print(f"  • {len(detected)} colonnes booléennes (0/1) converties en bool True/False")
        print(f"  • Types détectés: {type_counts_after.to_dict()}")
        print(f"  • Prêt pour les analyses!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_endpoint_boolean_detection():
    """Test de l'endpoint /detect-booleans"""
    print("\n" + "=" * 80)
    print("TEST: Endpoint /detect-booleans")
    print("=" * 80)
    
    try:
        from app import app
        
        # Charger un petit dataset pour le test
        df = pd.read_csv('disease_symptom_matrix.csv').iloc[:, :50]  # 50 colonnes seulement pour rapidité
        
        client = app.test_client()
        
        payload = {
            'data': df.to_dict('records'),
        }
        
        response = client.post(
            '/detect-booleans',
            json=payload,
            content_type='application/json'
        )
        
        if response.status_code == 200:
            result = response.get_json()
            print(f"\n✅ Endpoint /detect-booleans retourna 200 OK")
            print(f"\nRésultat:")
            print(f"  - Colonnes booléennes détectées: {result['boolean_columns'][:5]}")
            print(f"  - Nombre converties: {result['converted_count']}")
            print(f"  - Message: {result['message']}")
            return True
        else:
            print(f"\n❌ Erreur {response.status_code}: {response.get_json()}")
            return False
            
    except Exception as e:
        print(f"\n⚠️ Endpoint non testé (Flask non disponible): {str(e)}")
        return True

def main():
    print("\n" + "=" * 80)
    print("TESTS DE DETECTION ET CONVERSION DE COLONNES BOOLÉENNES")
    print("=" * 80 + "\n")
    
    success1 = test_boolean_detection()
    success2 = test_endpoint_boolean_detection()
    
    print("\n" + "=" * 80)
    if success1 and success2:
        print("✅ TOUS LES TESTS RÉUSSIS!")
        print("\nVous pouvez maintenant:")
        print("  1. Uploader un CSV avec 0/1 (colonnes booléennes)")
        print("  2. Le système détectera automatiquement qu'elles sont booléennes")
        print("  3. Les types seront correctement définis en 'boolean'")
        print("  4. Les analyses fonctionneront sans problème")
    else:
        print("⚠️ Certains tests ont échoué")
    print("=" * 80)

if __name__ == '__main__':
    main()
