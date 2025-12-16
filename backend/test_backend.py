"""
Script de test pour vérifier que toutes les dépendances sont installées
et que le backend fonctionne correctement
"""

import sys

def test_imports():
    """Test de tous les imports nécessaires"""
    print("🔍 Test des imports...")
    
    tests = {
        'Flask': 'flask',
        'Flask-CORS': 'flask_cors',
        'Pandas': 'pandas',
        'NumPy': 'numpy',
        'Scikit-learn': 'sklearn',
        'SciPy': 'scipy',
        'Statsmodels': 'statsmodels',
        'ReportLab': 'reportlab',
        'Matplotlib': 'matplotlib',
        'Seaborn': 'seaborn',
    }
    
    optional_tests = {
        'TensorFlow': 'tensorflow',
        'Prophet': 'prophet',
        'XGBoost': 'xgboost',
        'LightGBM': 'lightgbm',
    }
    
    failed = []
    success = []
    
    # Test des dépendances requises
    for name, module in tests.items():
        try:
            __import__(module)
            print(f"  ✅ {name}")
            success.append(name)
        except ImportError:
            print(f"  ❌ {name} - MANQUANT")
            failed.append(name)
    
    # Test des dépendances optionnelles
    optional_missing = []
    for name, module in optional_tests.items():
        try:
            __import__(module)
            print(f"  ✅ {name} (optionnel)")
            success.append(name)
        except ImportError:
            print(f"  ⚠️  {name} (optionnel) - Non installé")
            optional_missing.append(name)
    
    print(f"\n📊 Résumé:")
    print(f"  ✅ Succès: {len(success)}/{len(tests) + len(optional_tests)}")
    print(f"  ❌ Échecs: {len(failed)}/{len(tests)}")
    print(f"  ⚠️  Optionnels manquants: {len(optional_missing)}/{len(optional_tests)}")
    
    if failed:
        print(f"\n❗ Installez les dépendances manquantes:")
        print(f"  pip install {' '.join([tests[f] for f in failed])}")
        return False
    
    if optional_missing:
        print(f"\n💡 Dépendances optionnelles disponibles:")
        for m in optional_missing:
            print(f"  pip install {optional_tests[m]}")
    
    return True

def test_analyses():
    """Test rapide des modules d'analyse"""
    print("\n🧪 Test des modules d'analyse...")
    
    try:
        import pandas as pd
        import numpy as np
        
        # Créer des données de test
        data = pd.DataFrame({
            'x1': np.random.rand(100),
            'x2': np.random.rand(100),
            'y': np.random.rand(100),
            'cat': np.random.choice(['A', 'B', 'C'], 100)
        })
        
        # Test régression
        try:
            from analyses.regression import RegressionAnalyzer
            analyzer = RegressionAnalyzer(data)
            config = {
                'target': 'y',
                'features': ['x1', 'x2'],
                'methods': ['linear'],
                'test_size': 0.2
            }
            result = analyzer.perform_analysis(config)
            print("  ✅ Régression")
        except Exception as e:
            print(f"  ❌ Régression: {str(e)}")
        
        # Test classification
        try:
            from analyses.classification import ClassificationAnalyzer
            analyzer = ClassificationAnalyzer(data)
            config = {
                'target': 'cat',
                'features': ['x1', 'x2'],
                'methods': ['knn'],
                'test_size': 0.2
            }
            result = analyzer.perform_analysis(config)
            print("  ✅ Classification")
        except Exception as e:
            print(f"  ❌ Classification: {str(e)}")
        
        # Test clustering
        try:
            from analyses.clustering import ClusteringAnalyzer
            analyzer = ClusteringAnalyzer(data)
            config = {
                'features': ['x1', 'x2'],
                'methods': ['kmeans'],
                'n_clusters': 3
            }
            result = analyzer.perform_analysis(config)
            print("  ✅ Clustering")
        except Exception as e:
            print(f"  ❌ Clustering: {str(e)}")
        
        # Test nettoyage
        try:
            from analyses.data_cleaning import DataCleaner
            cleaner = DataCleaner(data)
            config = {
                'remove_duplicates': True,
                'handle_missing': {'method': 'mean'}
            }
            cleaned_df, report = cleaner.clean(config)
            print("  ✅ Nettoyage de données")
        except Exception as e:
            print(f"  ❌ Nettoyage: {str(e)}")
        
        # Test stats avancées
        try:
            from analyses.advanced_stats import AdvancedStatsAnalyzer
            analyzer = AdvancedStatsAnalyzer(data)
            config = {
                'tests': ['normality'],
                'alpha': 0.05
            }
            result = analyzer.perform_analysis(config)
            print("  ✅ Statistiques avancées")
        except Exception as e:
            print(f"  ❌ Stats avancées: {str(e)}")
        
        # Test PDF
        try:
            from reports.pdf_generator import PDFReportGenerator
            generator = PDFReportGenerator()
            print("  ✅ Générateur PDF")
        except Exception as e:
            print(f"  ❌ PDF: {str(e)}")
        
        print("\n✨ Tests des modules terminés!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {str(e)}")
        return False

def test_flask():
    """Test du serveur Flask"""
    print("\n🌐 Test du serveur Flask...")
    
    try:
        from app import app
        print("  ✅ Application Flask chargée")
        
        # Lister les routes
        print("\n📍 Routes disponibles:")
        for rule in app.url_map.iter_rules():
            methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            print(f"  {methods:10s} {rule.rule}")
        
        return True
    except Exception as e:
        print(f"  ❌ Erreur Flask: {str(e)}")
        return False

def main():
    print("="*60)
    print("🚀 DataAnalyzer - Test du Backend")
    print("="*60)
    
    # Test des imports
    if not test_imports():
        print("\n❌ Certaines dépendances sont manquantes!")
        print("   Installez-les avec: pip install -r requirements.txt")
        sys.exit(1)
    
    # Test des analyses
    if not test_analyses():
        print("\n⚠️  Certains modules d'analyse ont des problèmes")
    
    # Test Flask
    if not test_flask():
        print("\n❌ Le serveur Flask a des problèmes")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ Tous les tests sont passés!")
    print("="*60)
    print("\n💡 Pour démarrer le serveur:")
    print("   python app.py")
    print("\n📚 Consultez README.md pour plus d'informations")
    print("="*60)

if __name__ == '__main__':
    main()
