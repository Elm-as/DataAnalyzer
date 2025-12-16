"""
Script de test pour valider les améliorations
Exécutez ceci pour vérifier que tout fonctionne
"""

import sys
import os

# Ajouter backend au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Tester les imports des nouveaux modules"""
    print("=" * 60)
    print("🧪 TEST 1 : Imports")
    print("=" * 60)
    
    try:
        from utils.data_validator import DataValidator, DataCleaner, FeatureValidator
        print("✅ DataValidator importé")
        print("✅ DataCleaner importé")
        print("✅ FeatureValidator importé")
        return True
    except ImportError as e:
        print(f"❌ Erreur import : {e}")
        return False


def test_data_validator():
    """Tester le module DataValidator"""
    print("\n" + "=" * 60)
    print("🧪 TEST 2 : DataValidator")
    print("=" * 60)
    
    try:
        import pandas as pd
        import numpy as np
        from utils.data_validator import DataValidator
        
        # Créer un dataset de test
        df = pd.DataFrame({
            'id': range(1, 101),
            'name': [f'Person_{i}' for i in range(1, 101)],
            'age': [np.random.randint(18, 80) if i % 10 != 0 else np.nan for i in range(100)],
            'salary': [np.random.randint(30000, 150000) for _ in range(100)],
            'empty_col': [np.nan] * 100,
            'category': [np.random.choice(['A', 'B', 'C']) for _ in range(100)]
        })
        
        # Test validate_for_analysis
        print("\nTest validate_for_analysis...")
        is_valid, issues, suggestions = DataValidator.validate_for_analysis(
            df,
            {'target': 'salary', 'features': ['age', 'category']},
            'regression'
        )
        print(f"  - Valid: {is_valid}")
        if issues:
            print(f"  - Issues: {list(issues.keys())}")
        if suggestions:
            print(f"  - Suggestions: {len(suggestions)}")
        
        # Test get_data_quality_report
        print("\nTest get_data_quality_report...")
        report = DataValidator.get_data_quality_report(df)
        print(f"  - Total cells: {report['total_cells']}")
        print(f"  - Null cells: {report['null_cells']}")
        print(f"  - Null percentage: {report['null_percentage']:.2f}%")
        print(f"  - Columns analyzed: {len(report['columns'])}")
        
        # Afficher détails colonnes
        print("\n  Colonnes:")
        for col, info in report['columns'].items():
            print(f"    {col}: {info['null_percentage']:.1f}% N/A, {info['unique_values']} uniques")
        
        print("✅ DataValidator fonctionne")
        return True
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_cleaner():
    """Tester le module DataCleaner"""
    print("\n" + "=" * 60)
    print("🧪 TEST 3 : DataCleaner")
    print("=" * 60)
    
    try:
        import pandas as pd
        import numpy as np
        from utils.data_validator import DataCleaner
        
        # Créer un dataset "sale" avec des problèmes
        df = pd.DataFrame({
            'index': range(1, 101),  # Colonne d'index inutile
            'id': range(1000, 1100),  # Colonne d'ID
            'name': [f'Item_{i}' for i in range(100)],
            'value': [np.random.randint(10, 100) for _ in range(100)],
            'notes': [np.nan] * 100,  # Colonne 100% vide
            'category': [np.random.choice(['A', 'B']) for _ in range(100)]
        })
        
        # Ajouter quelques doublons
        df = pd.concat([df, df.iloc[:5]], ignore_index=True)
        
        print(f"\nDataset avant nettoyage: {df.shape}")
        print(f"Colonnes: {list(df.columns)}")
        
        # Nettoyage
        df_clean, report = DataCleaner.auto_clean(df)
        
        print(f"\nDataset après nettoyage: {df_clean.shape}")
        print(f"Colonnes: {list(df_clean.columns)}")
        
        print("\nOpérations effectuées:")
        for op in report['operations']:
            print(f"  - {op}")
        
        print(f"\nRésumé:")
        print(f"  - Colonnes supprimées: {report['removed_cols']}")
        print(f"  - Lignes supprimées: {report['removed_rows']}")
        
        print("✅ DataCleaner fonctionne")
        return True
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        return False


def test_feature_validator():
    """Tester le module FeatureValidator"""
    print("\n" + "=" * 60)
    print("🧪 TEST 4 : FeatureValidator")
    print("=" * 60)
    
    try:
        import pandas as pd
        import numpy as np
        from utils.data_validator import FeatureValidator
        
        # Dataset pour régression
        X = pd.DataFrame({
            'age': np.random.randint(18, 80, 50),
            'income': np.random.randint(20000, 150000, 50)
        })
        y = pd.Series(np.random.randint(0, 1000000, 50))
        
        # Test régression
        print("\nTest validate_regression_features...")
        is_valid, issues = FeatureValidator.validate_regression_features(X, y)
        print(f"  - Valid: {is_valid}")
        if issues:
            print(f"  - Issues: {issues}")
        else:
            print(f"  - No issues found ✅")
        
        # Dataset pour classification
        y_cat = pd.Series(np.random.choice(['A', 'B', 'C'], 50))
        
        # Test classification
        print("\nTest validate_classification_features...")
        is_valid, issues = FeatureValidator.validate_classification_features(X, y_cat)
        print(f"  - Valid: {is_valid}")
        if issues:
            print(f"  - Issues: {issues}")
        else:
            print(f"  - No issues found ✅")
        
        print("✅ FeatureValidator fonctionne")
        return True
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        return False


def test_csv_with_missing_values():
    """Tester un CSV réaliste avec valeurs manquantes"""
    print("\n" + "=" * 60)
    print("🧪 TEST 5 : CSV Réaliste")
    print("=" * 60)
    
    try:
        import pandas as pd
        import numpy as np
        from utils.data_validator import DataValidator, DataCleaner
        
        # Créer un CSV réaliste
        np.random.seed(42)
        df = pd.DataFrame({
            'id': range(1, 101),
            'age': np.random.randint(18, 80, 100),
            'salary': np.random.randint(30000, 150000, 100),
            'department': np.random.choice(['Sales', 'IT', 'HR', 'Finance'], 100),
            'performance_score': [np.random.randint(1, 10) if i % 7 != 0 else np.nan for i in range(100)],
            'bonus_percentage': [np.random.randint(0, 30) if i % 5 != 0 else np.nan for i in range(100)],
            'notes': [np.nan] * 100,  # Colonne vide
            'feedback': [np.random.choice(['Good', 'Bad', 'Neutral']) if i % 3 == 0 else np.nan for i in range(100)]
        })
        
        print(f"\nDataset original: {df.shape}")
        
        # Valider
        report = DataValidator.validate(df)
        
        print(f"\nQualité des données:")
        print(f"  - Complétude: {report['quality']['completeness']:.1f}%")
        print(f"  - Doublons: {report['quality']['duplicateRows']}")
        print(f"  - Colonnes problématiques: {len(report['problematicColumns'])}")
        
        # Nettoyer
        df_clean, clean_report = DataCleaner.auto_clean(df)
        
        print(f"\nAprès nettoyage: {df_clean.shape}")
        print(f"  - Colonnes: {', '.join(df_clean.columns)}")
        
        print("✅ CSV réaliste traité avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Exécuter tous les tests"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║      🧪 TESTS DES AMÉLIORATIONS DATAANALYZER 🧪          ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    results = {
        'Imports': test_imports(),
        'DataValidator': test_data_validator(),
        'DataCleaner': test_data_cleaner(),
        'FeatureValidator': test_feature_validator(),
        'CSV réaliste': test_csv_with_missing_values(),
    }
    
    # Résumé
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8} {test_name}")
    
    print("=" * 60)
    print(f"Résultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("\n🎉 Tous les tests passent ! Les améliorations sont prêtes.")
    else:
        print(f"\n⚠️  {total - passed} test(s) échoué(s). Vérifier les erreurs ci-dessus.")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
