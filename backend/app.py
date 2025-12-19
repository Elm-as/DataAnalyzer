from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
import io
import traceback
from datetime import datetime
import os

# Import analysis modules
from analyses.regression import RegressionAnalyzer
from analyses.classification import ClassificationAnalyzer
from analyses.discriminant import DiscriminantAnalyzer
from analyses.neural_networks import NeuralNetworkAnalyzer
from analyses.time_series import TimeSeriesAnalyzer
from analyses.clustering import ClusteringAnalyzer
from analyses.data_cleaning import DataCleaner
from analyses.advanced_stats import AdvancedStatsAnalyzer
from analyses.symptom_matching import SymptomMatchingAnalyzer
from reports.pdf_generator import PDFReportGenerator

# Import validation modules
try:
    from utils.data_validator import DataValidator, DataCleaner as NewDataCleaner, BooleanDetector
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Backend is running"}), 200

@app.route('/validate-data', methods=['POST'])
def validate_data():
    """Valide la qualité des données et retourne un rapport"""
    try:
        if not VALIDATION_AVAILABLE:
            return jsonify({"error": "Validation module not available"}), 500
        
        data = request.json
        df = pd.DataFrame(data['data'])
        columns = data.get('columns', list(df.columns))
        
        # Valider et obtenir le rapport
        report = DataValidator.validate(df, columns)
        
        return jsonify(report), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 400

@app.route('/detect-booleans', methods=['POST'])
def detect_booleans():
    """Détecte les colonnes booléennes et les convertit automatiquement"""
    try:
        if not VALIDATION_AVAILABLE:
            return jsonify({"error": "Validation module not available"}), 500
        
        data = request.json
        df = pd.DataFrame(data['data'])
        
        # Détecter les colonnes booléennes
        boolean_cols = BooleanDetector.detect_boolean_columns(df)
        detected_cols = [col for col, is_bool in boolean_cols.items() if is_bool]
        
        # Convertir automatiquement
        df_converted, converted = BooleanDetector.auto_convert_booleans(df)
        
        # Rapport après conversion
        validation_report = DataValidator.validate(df_converted)
        
        return jsonify({
            "data": df_converted.to_dict('records'),
            "boolean_columns": detected_cols,
            "converted_count": len(converted),
            "conversion_report": {col: True for col in converted},
            "quality_after_conversion": validation_report['quality'],
            "message": f"{len(detected_cols)} colonnes booléennes détectées et converties automatiquement"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 400

@app.route('/validate-and-clean', methods=['POST'])
def validate_and_clean_data():
    """Valide et nettoie les données automatiquement"""
    try:
        if not VALIDATION_AVAILABLE:
            return jsonify({"error": "Validation module not available"}), 500
        
        data = request.json
        df = pd.DataFrame(data['data'])
        config = data.get('config', {
            'remove_high_null_cols': True,
            'remove_duplicates': True,
            'null_threshold': 0.8
        })
        
        # Nettoyer les données
        cleaned_df, report = NewDataCleaner.auto_clean(
            df,
            remove_high_null_cols=config.get('remove_high_null_cols', True),
            remove_duplicates=config.get('remove_duplicates', True),
            null_threshold=config.get('null_threshold', 0.8)
        )
        
        # Obtenir le rapport après nettoyage
        validation_report = DataValidator.validate(cleaned_df)
        
        return jsonify({
            "data": cleaned_df.to_dict('records'),
            "cleaning_report": report,
            "validation_report": validation_report,
            "removed_rows": len(df) - len(cleaned_df),
            "removed_columns": list(set(df.columns) - set(cleaned_df.columns))
        }), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 400

@app.route('/analyze/basic', methods=['POST'])
def analyze_basic():
    """Analyses de base complètes avec pandas/numpy"""
    try:
        data = request.json
        df = pd.DataFrame(data['data'])
        config = data.get('config', {})
        
        results = {}
        
        # Statistiques descriptives
        if config.get('descriptiveStats', True):
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            stats = []
            for col in numeric_cols:
                col_data = df[col].dropna()
                stats.append({
                    'column': col,
                    'count': int(col_data.count()),
                    'mean': float(col_data.mean()),
                    'median': float(col_data.median()),
                    'std': float(col_data.std()),
                    'min': float(col_data.min()),
                    'max': float(col_data.max()),
                    'q1': float(col_data.quantile(0.25)),
                    'q3': float(col_data.quantile(0.75)),
                    'skewness': float(col_data.skew()),
                    'kurtosis': float(col_data.kurtosis())
                })
            results['descriptiveStats'] = stats
        
        # Corrélations
        if config.get('correlations', True):
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                corr_matrix = df[numeric_cols].corr()
                results['correlations'] = corr_matrix.to_dict()
        
        # Distributions
        if config.get('distributions', True):
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            distributions = []
            for col in numeric_cols:
                col_data = df[col].dropna()
                hist, bin_edges = np.histogram(col_data, bins=10)
                distributions.append({
                    'column': col,
                    'histogram': hist.tolist(),
                    'bins': [{'start': float(bin_edges[i]), 'end': float(bin_edges[i+1]), 'count': int(hist[i])} 
                             for i in range(len(hist))]
                })
            results['distributions'] = distributions
        
        # Détection d'outliers (IQR method)
        if config.get('outliers', True):
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            outliers = []
            for col in numeric_cols:
                col_data = df[col].dropna()
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
                outlier_indices = df[outlier_mask].index.tolist()
                
                outliers.append({
                    'column': col,
                    'outlierCount': len(outlier_indices),
                    'outlierPercentage': (len(outlier_indices) / len(df)) * 100,
                    'outliers': [{'index': int(i), 'value': float(df.loc[i, col])} for i in outlier_indices[:10]],
                    'bounds': {'lower': float(lower_bound), 'upper': float(upper_bound)}
                })
            results['outliers'] = outliers
        
        # Analyse catégorielle
        if config.get('categorical', True):
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            categorical_analysis = []
            for col in categorical_cols:
                value_counts = df[col].value_counts()
                categorical_analysis.append({
                    'column': col,
                    'uniqueValues': int(df[col].nunique()),
                    'mode': str(df[col].mode()[0]) if len(df[col].mode()) > 0 else None,
                    'frequencies': value_counts.head(10).to_dict(),
                    'totalValues': int(len(df[col]))
                })
            results['categorical'] = categorical_analysis
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/analyze/regression', methods=['POST'])
def analyze_regression():
    """Analyse de régression (linéaire, polynomiale, logistique, Ridge, Lasso)"""
    try:
        data = request.json
        df = pd.DataFrame(data['data'])
        config = data['config']
        
        analyzer = RegressionAnalyzer(df)
        results = analyzer.perform_analysis(config)
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/analyze/classification', methods=['POST'])
def analyze_classification():
    """Classification (KNN, SVM, Random Forest, Decision Trees, XGBoost, LightGBM)"""
    try:
        data = request.json
        df = pd.DataFrame(data['data'])
        config = data['config']
        
        analyzer = ClassificationAnalyzer(df)
        results = analyzer.perform_analysis(config)
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/analyze/discriminant', methods=['POST'])
def analyze_discriminant():
    """Analyse discriminante (LDA, QDA)"""
    try:
        data = request.json
        df = pd.DataFrame(data['data'])
        config = data['config']
        
        analyzer = DiscriminantAnalyzer(df)
        results = analyzer.perform_analysis(config)
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/analyze/neural-networks', methods=['POST'])
def analyze_neural_networks():
    """Réseaux de neurones (MLP, CNN, RNN, LSTM)"""
    try:
        data = request.json
        df = pd.DataFrame(data['data'])
        config = data['config']
        
        analyzer = NeuralNetworkAnalyzer(df)
        results = analyzer.perform_analysis(config)
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/analyze/time-series', methods=['POST'])
def analyze_time_series():
    """Séries temporelles (ARIMA, SARIMA, Prophet)"""
    try:
        data = request.json
        df = pd.DataFrame(data['data'])
        config = data['config']
        
        analyzer = TimeSeriesAnalyzer(df)
        results = analyzer.perform_analysis(config)
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/analyze/clustering-advanced', methods=['POST'])
def analyze_clustering_advanced():
    """Clustering avancé (K-Means, DBSCAN, Hierarchical, GMM)"""
    try:
        data = request.json
        df = pd.DataFrame(data['data'])
        config = data['config']
        
        analyzer = ClusteringAnalyzer(df)
        results = analyzer.perform_analysis(config)
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/clean/data', methods=['POST'])
def clean_data():
    """Nettoyage des données (valeurs manquantes, doublons, normalisation, encodage)"""
    try:
        data = request.json
        df = pd.DataFrame(data['data'])
        config = data['config']
        
        cleaner = DataCleaner(df)
        cleaned_df, report = cleaner.clean(config)
        
        return jsonify({
            "cleaned_data": cleaned_df.to_dict(orient='records'),
            "report": report
        }), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/analyze/advanced-stats', methods=['POST'])
def analyze_advanced_stats():
    """Statistiques avancées (tests d'hypothèse, ANOVA, tests non-paramétriques)"""
    try:
        data = request.json
        df = pd.DataFrame(data['data'])
        config = data['config']
        
        analyzer = AdvancedStatsAnalyzer(df)
        results = analyzer.perform_analysis(config)
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/analyze/symptom-matching', methods=['POST'], endpoint='analyze_symptom_matching_analysis')
def analyze_symptom_matching_analysis():
    """Analyse de correspondance symptômes-maladies (TF-IDF + Naive Bayes)"""
    try:
        data = request.json
        df = pd.DataFrame(data['data'])
        config = data.get('config', {})
        
        analyzer = SymptomMatchingAnalyzer(df)
        results = analyzer.perform_analysis(config)
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

# Stocker les analyseurs pour prédictions
active_analyzers = {}

@app.route('/analyze/symptom-matching/train', methods=['POST'], endpoint='train_symptom_matching_model')
def train_symptom_matching_model():
    """Entraîne et stocke le modèle de correspondance symptômes-maladies pour les prédictions"""
    try:
        data = request.json
        df = pd.DataFrame(data['data'])
        config = data.get('config', {})
        
        analyzer = SymptomMatchingAnalyzer(df)
        results = analyzer.perform_analysis(config)
        
        # Stocker l'analyzer pour prédictions futures
        dataset_id = data.get('dataset_id', 'default')
        active_analyzers[dataset_id] = analyzer
        
        print(f"[BACKEND] Analyzer stocké pour dataset {dataset_id}")
        print(f"  - Modèle: {type(analyzer.trained_model)}")
        print(f"  - Features: {len(analyzer.feature_names) if analyzer.feature_names else 0}")
        print(f"  - Classes: {len(analyzer.classes_) if analyzer.classes_ is not None else 0}")
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint de prédiction en temps réel
    Utilise le modèle entraîné pour prédire la variable cible
    
    Body:
    {
        "dataset_id": "default",
        "features": {
            "fievre": 1,
            "fatigue": 1,
            "cephalees": 0,
            ...
        }
    }
    
    Returns:
    {
        "predictions": [
            {"class": "Paludisme", "probability": 0.85},
            {"class": "Grippe", "probability": 0.12},
            ...
        ],
        "top_prediction": {"class": "Paludisme", "probability": 0.85}
    }
    """
    try:
        data = request.json
        dataset_id = data.get('dataset_id', 'default')
        features = data.get('features', {})
        
        # Récupérer l'analyzer
        if dataset_id not in active_analyzers:
            return jsonify({"error": f"Aucun modèle entraîné pour dataset {dataset_id}. Lancez d'abord une analyse."}), 400
        
        analyzer = active_analyzers[dataset_id]
        
        if analyzer.trained_model is None:
            return jsonify({"error": "Aucun modèle ML entraîné. Relancez l'analyse avec model='bernoulli' ou 'all'."}), 400
        
        # Construire X_test à partir des features
        # Ordre doit correspondre à analyzer.feature_names
        X_test = []
        for feature_name in analyzer.feature_names:
            value = features.get(feature_name, 0)  # Par défaut 0 si absent
            X_test.append(value)
        
        X_test = np.array([X_test])  # Shape (1, n_features)
        
        print(f"\n[PREDICT] Prédiction pour dataset {dataset_id}")
        print(f"  - X_test shape: {X_test.shape}")
        print(f"  - Features fournies: {len(features)}/{len(analyzer.feature_names)}")
        print(f"  - Valeurs non-nulles: {np.sum(X_test > 0)}")
        
        # Prédire avec probabilités
        y_proba = analyzer.trained_model.predict_proba(X_test)[0]
        
        # Trier par probabilité décroissante
        top_indices = y_proba.argsort()[-10:][::-1]  # Top 10
        
        predictions = []
        for idx in top_indices:
            predictions.append({
                'class': str(analyzer.classes_[idx]),
                'probability': round(float(y_proba[idx]), 4)
            })
        
        result = {
            'predictions': predictions,
            'top_prediction': predictions[0] if predictions else None,
            'n_features_used': int(np.sum(X_test > 0)),
            'total_features': len(analyzer.feature_names)
        }
        
        print(f"  - Top prédiction: {result['top_prediction']}")
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/report/generate', methods=['POST'])
def generate_report():
    """Génération de rapport PDF A4, police 13-14, noir et blanc"""
    try:
        data = request.json
        analysis_results = data['results']
        config = data.get('config', {})
        
        generator = PDFReportGenerator()
        pdf_buffer = generator.generate(analysis_results, config)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'rapport_analyse_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )

