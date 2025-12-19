from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
import io
import traceback
from datetime import datetime, timezone
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

active_analyzers = {}
SUMMARY_EXCLUDED_KEYS = {'data', 'features', 'target'}


def store_analyzer(dataset_id, model_type, analyzer, config, results=None):
    """Persist trained analyzer and metadata in memory."""
    active_analyzers[dataset_id] = {
        "model_type": model_type,
        "analyzer": analyzer,
        "config": config,
        "results": results,
        "trained_at": datetime.now(timezone.utc).isoformat()
    }


def _get_analyzer_entry(dataset_id):
    """Return normalized analyzer entry for a dataset_id."""
    if dataset_id not in active_analyzers:
        return None
    entry = active_analyzers[dataset_id]
    if isinstance(entry, dict) and "analyzer" in entry:
        return entry
    # Backward compatibility for stored analyzer objects
    return {
        "model_type": getattr(entry, "model_type", None) or "symptom_matching",
        "analyzer": entry,
        "config": getattr(entry, "config", {}),
        "results": getattr(entry, "results", None),
        "trained_at": None
    }


def _select_best_model(models, best_model_name):
    """Find the best model result based on provided name."""
    if not models:
        return None
    for result in models.values():
        if result.get('method') == best_model_name:
            return result
    # Fallback to first result
    return next(iter(models.values()))


def _normalize_payload(payload):
    """Convert numpy types to JSON serializable Python primitives."""
    if isinstance(payload, dict):
        return {k: _normalize_payload(v) for k, v in payload.items()}
    if isinstance(payload, list):
        return [_normalize_payload(v) for v in payload]
    if isinstance(payload, tuple):
        return tuple(_normalize_payload(item) for item in payload)
    if isinstance(payload, (np.integer, np.floating)):
        return payload.item()
    if isinstance(payload, np.ndarray):
        return payload.tolist()
    return payload


def _filtered_hyperparams(config, excluded_keys):
    """Return hyperparameters without non-relevant config entries."""
    return {k: v for k, v in (config or {}).items() if k not in excluded_keys}


def _build_classification_summary(entry):
    results = entry.get('results') or {}
    config = entry.get('config') or {}
    models = results.get('models', {})
    best_model_name = results.get('summary', {}).get('best_model')
    best_result = _select_best_model(models, best_model_name)
    
    metrics = best_result.get('test_metrics') if best_result else None
    feature_importance = best_result.get('feature_importance') if best_result else None
    coefficients = best_result.get('coefficients') if best_result else None
    if best_result:
        if best_result.get('classes'):
            num_classes = len(best_result.get('classes'))
        elif best_result.get('confusion_matrix'):
            num_classes = len(best_result.get('confusion_matrix'))
        else:
            num_classes = None
    else:
        num_classes = None
    
    return {
        "model_type": "classification",
        "algorithm": best_result.get('method') if best_result else None,
        "hyperparameters": _filtered_hyperparams(config, SUMMARY_EXCLUDED_KEYS),
        "coefficients": coefficients,
        "feature_importance": feature_importance,
        "metrics": metrics,
        "n_features": len(config.get('features', [])),
        "n_classes": num_classes
    }


def _build_regression_summary(entry):
    results = entry.get('results') or {}
    config = entry.get('config') or {}
    models = results.get('models', {})
    best_model_name = results.get('summary', {}).get('best_model')
    best_result = _select_best_model(models, best_model_name)
    
    metrics = best_result.get('test_metrics') if best_result else None
    coefficients = best_result.get('coefficients') if best_result else None
    
    return {
        "model_type": "regression",
        "algorithm": best_result.get('method') if best_result else None,
        "hyperparameters": _filtered_hyperparams(config, SUMMARY_EXCLUDED_KEYS),
        "coefficients": coefficients,
        "feature_importance": best_result.get('feature_importance') if best_result else None,
        "metrics": metrics,
        "n_features": len(config.get('features', [])),
        "n_classes": None
    }


def _build_time_series_summary(entry):
    results = entry.get('results') or {}
    models = results.get('models', {})
    best_model_name = results.get('summary', {}).get('best_model')
    best_result = _select_best_model(models, best_model_name)
    
    metrics = best_result.get('test_metrics') if best_result else None
    hyperparams = {}
    if best_result:
        if 'order' in best_result:
            hyperparams['order'] = best_result['order']
        if 'seasonal_order' in best_result:
            hyperparams['seasonal_order'] = best_result['seasonal_order']
    
    return {
        "model_type": "time_series",
        "algorithm": best_result.get('method') if best_result else None,
        "hyperparameters": hyperparams,
        "coefficients": None,
        "feature_importance": None,
        "metrics": metrics,
        "n_features": 1,
        "n_classes": None
    }


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


def _validate_and_get_entry(data):
    dataset_id = data.get('dataset_id')
    if not dataset_id:
        return None, jsonify({"error": "The dataset_id field is required"}), 400
    entry = _get_analyzer_entry(dataset_id)
    if entry is None:
        return None, jsonify({"error": f"No model stored for dataset {dataset_id}"}), 404
    return entry, None, None


@app.route('/models/summary', methods=['POST'])
def model_summary():
    """Return a summary of the trained model (type, algorithm, hyperparameters, metrics)."""
    try:
        data = request.json or {}
        model_type = data.get('model_type')
        if model_type not in ['classification', 'regression', 'time_series']:
            return jsonify({"error": "model_type must be classification, regression or time_series"}), 400
        
        entry, error_resp, status = _validate_and_get_entry(data)
        if error_resp:
            return error_resp, status
        
        if entry.get('model_type') != model_type:
            return jsonify({"error": f"Stored model type is {entry.get('model_type')} not {model_type}"}), 400
        
        if model_type == 'classification':
            summary = _build_classification_summary(entry)
        elif model_type == 'regression':
            summary = _build_regression_summary(entry)
        else:
            summary = _build_time_series_summary(entry)
        
        summary['dataset_id'] = data.get('dataset_id')
        summary['trained_at'] = entry.get('trained_at')
        return jsonify(_normalize_payload(summary)), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route('/models/plots/classification', methods=['POST'])
def model_plots_classification():
    """Return visualization payloads for classification models."""
    try:
        data = request.json or {}
        entry, error_resp, status = _validate_and_get_entry(data)
        if error_resp:
            return error_resp, status
        if entry.get('model_type') != 'classification':
            return jsonify({"error": "No classification model available for this dataset"}), 400
        
        results = entry.get('results') or {}
        models = results.get('models', {})
        best_result = _select_best_model(models, results.get('summary', {}).get('best_model'))
        if not best_result:
            return jsonify({"error": "No model result available"}), 400
        
        confusion = best_result.get('confusion_matrix')
        probabilities = best_result.get('probabilities_sample')
        prob_distribution = None
        if probabilities is not None:
            proba_array = np.array(probabilities)
            if proba_array.ndim == 2 and proba_array.size > 0:
                prob_distribution = {
                    "mean": proba_array.mean(axis=0).tolist(),
                    "min": proba_array.min(axis=0).tolist(),
                    "max": proba_array.max(axis=0).tolist()
                }
        
        response = {
            "dataset_id": data.get('dataset_id'),
            "model": best_result.get('method'),
            "plots": {
                "confusion_matrix": confusion,
                "probability_distribution": prob_distribution,
                "decision_boundary": None  # Can be generated on the frontend if needed (2D)
            }
        }
        return jsonify(_normalize_payload(response)), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route('/models/plots/regression', methods=['POST'])
def model_plots_regression():
    """Return visualization payloads for regression models."""
    try:
        data = request.json or {}
        entry, error_resp, status = _validate_and_get_entry(data)
        if error_resp:
            return error_resp, status
        if entry.get('model_type') != 'regression':
            return jsonify({"error": "No regression model available for this dataset"}), 400
        
        results = entry.get('results') or {}
        models = results.get('models', {})
        best_result = _select_best_model(models, results.get('summary', {}).get('best_model'))
        if not best_result:
            return jsonify({"error": "No model result available"}), 400
        
        response = {
            "dataset_id": data.get('dataset_id'),
            "model": best_result.get('method'),
            "plots": {
                "predicted_vs_actual": {
                    "predicted": best_result.get('predictions_sample'),
                    "actual": best_result.get('actual_sample')
                },
                "residuals": best_result.get('residuals_sample')
            }
        }
        return jsonify(_normalize_payload(response)), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route('/models/plots/time-series', methods=['POST'])
def model_plots_time_series():
    """Return visualization payloads for time series models."""
    try:
        data = request.json or {}
        entry, error_resp, status = _validate_and_get_entry(data)
        if error_resp:
            return error_resp, status
        if entry.get('model_type') != 'time_series':
            return jsonify({"error": "No time series model available for this dataset"}), 400
        
        results = entry.get('results') or {}
        models = results.get('models', {})
        best_result = _select_best_model(models, results.get('summary', {}).get('best_model'))
        if not best_result:
            return jsonify({"error": "No model result available"}), 400
        
        response = {
            "dataset_id": data.get('dataset_id'),
            "model": best_result.get('method'),
            "plots": {
                "observed_vs_predicted": {
                    "actual": best_result.get('test_actual'),
                    "predicted": best_result.get('test_predictions'),
                    "index": best_result.get('test_index')
                },
                "forecast": best_result.get('forecast')
            }
        }
        return jsonify(_normalize_payload(response)), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/analyze/regression', methods=['POST'])
def analyze_regression():
    """Analyse de régression (linéaire, polynomiale, logistique, Ridge, Lasso)"""
    try:
        data = request.json
        df = pd.DataFrame(data['data'])
        config = data['config']
        dataset_id = data.get('dataset_id', 'default')
        
        analyzer = RegressionAnalyzer(df)
        results = analyzer.perform_analysis(config)
        store_analyzer(dataset_id, 'regression', analyzer, config, results)
        
        response = {"dataset_id": dataset_id, **results}
        return jsonify(_normalize_payload(response)), 200
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/analyze/classification', methods=['POST'])
def analyze_classification():
    """Classification (KNN, SVM, Random Forest, Decision Trees, XGBoost, LightGBM)"""
    try:
        data = request.json
        df = pd.DataFrame(data['data'])
        config = data['config']
        dataset_id = data.get('dataset_id', 'default')
        
        analyzer = ClassificationAnalyzer(df)
        results = analyzer.perform_analysis(config)
        store_analyzer(dataset_id, 'classification', analyzer, config, results)
        
        response = {"dataset_id": dataset_id, **results}
        return jsonify(_normalize_payload(response)), 200
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
        dataset_id = data.get('dataset_id', 'default')
        
        analyzer = TimeSeriesAnalyzer(df)
        results = analyzer.perform_analysis(config)
        store_analyzer(dataset_id, 'time_series', analyzer, config, results)
        
        response = {"dataset_id": dataset_id, **results}
        return jsonify(_normalize_payload(response)), 200
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
        
        from analyses.symptom_matching import SymptomMatchingAnalyzer
        analyzer = SymptomMatchingAnalyzer(df)
        results = analyzer.perform_analysis(config)
        
        # Stocker l'analyzer pour prédictions futures
        dataset_id = data.get('dataset_id', 'default')
        store_analyzer(dataset_id, 'symptom_matching', analyzer, config, results)
        
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
        analyzer_entry = _get_analyzer_entry(dataset_id)
        if analyzer_entry is None:
            return jsonify({"error": f"Aucun modèle entraîné pour dataset {dataset_id}. Lancez d'abord une analyse."}), 400
        
        analyzer = analyzer_entry.get('analyzer')
        
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

