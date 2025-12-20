import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso, LogisticRegression, ElasticNet
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import json

# Import validation module
try:
    from utils.data_validator import FeatureValidator
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False

class RegressionAnalyzer:
    def __init__(self, df):
        self.df = df

        # Pour /predict (runtime)
        self.model_type = 'regression'
        self._encoded_feature_columns = None
        self._original_feature_columns = None
        self._predict_scaler = None
        self._predict_poly = None
        self._predict_model = None
        self._best_model_key = None
        self._best_model_label = None
        self._target_column = None

    def _encode_features(self, X_raw: pd.DataFrame) -> pd.DataFrame:
        """Encode les features en numérique (bool/date/catégoriel) et gère les NA."""
        X = X_raw.copy()

        for col in X.columns:
            # Bool -> 0/1
            if X[col].dtype == bool:
                X[col] = X[col].astype(int)
                continue

            # Dates -> timestamp (ns)
            if np.issubdtype(X[col].dtype, np.datetime64):
                X[col] = X[col].view('int64')
                continue

            # Tentative de parsing datetime pour object
            if X[col].dtype == object:
                parsed = pd.to_datetime(X[col], errors='ignore', utc=True)
                if np.issubdtype(parsed.dtype, np.datetime64):
                    X[col] = parsed.view('int64')

        # One-hot pour colonnes non numériques restantes
        non_numeric = [c for c in X.columns if not np.issubdtype(X[c].dtype, np.number)]
        if non_numeric:
            X = pd.get_dummies(X, columns=non_numeric, dummy_na=True)

        # Remplissage NA
        X = X.apply(pd.to_numeric, errors='coerce')
        X = X.fillna(X.mean(numeric_only=True)).fillna(0)
        return X

    def _encode_target(self, y_raw: pd.Series) -> pd.Series:
        y = y_raw.copy()
        if np.issubdtype(y.dtype, np.datetime64):
            return y.view('int64')
        if y.dtype == object:
            y = pd.to_numeric(y, errors='coerce')
        return y

    def _train_predictor(self, method_key: str, X_encoded: pd.DataFrame, y: pd.Series, config: dict):
        """Entraîne un modèle final pour /predict, basé sur method_key."""
        self._encoded_feature_columns = X_encoded.columns.tolist()
        self._original_feature_columns = list(config.get('features', []))
        self._target_column = config.get('target')
        self._best_model_key = method_key

        # Par défaut, on utilise scaler + modèle (hors polynomial)
        self._predict_poly = None

        if method_key == 'polynomial':
            degree = config.get('polynomial_degree', 2)
            self._predict_poly = PolynomialFeatures(degree=degree)
            X_poly = self._predict_poly.fit_transform(X_encoded.values)
            model = LinearRegression()
            model.fit(X_poly, y)
            self._predict_scaler = None
            self._predict_model = model
            return

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_encoded.values)

        if method_key == 'linear':
            model = LinearRegression()
        elif method_key == 'ridge':
            model = Ridge(alpha=config.get('ridge_alpha', 1.0))
        elif method_key == 'lasso':
            model = Lasso(alpha=config.get('lasso_alpha', 1.0))
        elif method_key in ('elastic', 'elastic_net'):
            model = ElasticNet(
                alpha=config.get('elastic_alpha', 1.0),
                l1_ratio=config.get('elastic_l1_ratio', 0.5)
            )
        else:
            # fallback
            model = Ridge(alpha=config.get('ridge_alpha', 1.0))

        model.fit(X_scaled, y)
        self._predict_scaler = scaler
        self._predict_model = model

    def predict(self, features: dict):
        """Prédit la valeur cible à partir d'un dict {feature: value}."""
        if self._predict_model is None or not self._original_feature_columns or not self._encoded_feature_columns:
            raise ValueError("No trained regression model available")

        # Construire une ligne avec les colonnes originales
        row = {}
        for col in self._original_feature_columns:
            row[col] = features.get(col, None)
        X_raw = pd.DataFrame([row])
        X_encoded = self._encode_features(X_raw)
        X_encoded = X_encoded.reindex(columns=self._encoded_feature_columns, fill_value=0)

        if self._predict_poly is not None:
            X_in = self._predict_poly.transform(X_encoded.values)
            pred = self._predict_model.predict(X_in)[0]
            return float(pred)

        X_scaled = self._predict_scaler.transform(X_encoded.values) if self._predict_scaler is not None else X_encoded.values
        pred = self._predict_model.predict(X_scaled)[0]
        return float(pred)
        
    def perform_analysis(self, config):
        """
        Effectue différents types de régression
        config = {
            'target': 'nom_colonne_cible',
            'features': ['col1', 'col2', ...],
            'methods': ['linear', 'polynomial', 'ridge', 'lasso', 'elastic', 'logistic'],
            'polynomial_degree': 2,
            'test_size': 0.2,
            'cv_folds': 5
        }
        """
        results = {
            'summary': {},
            'models': {}
        }
        
        # Valider les features si le module est disponible
        if VALIDATION_AVAILABLE:
            X_raw = self.df[config['features']]
            y_raw = self.df[config['target']]
            is_valid, issues = FeatureValidator.validate_regression_features(X_raw, y_raw)
            
            if not is_valid:
                return {
                    'error': 'Validation failed',
                    'validation_errors': issues,
                    'validation_warnings': [],
                    'summary': {},
                    'models': {}
                }
        
        # Préparation des données (robuste multi-types)
        X_raw = self.df[config['features']]
        y_raw = self.df[config['target']]

        X = self._encode_features(X_raw)
        y = self._encode_target(y_raw)
        y = y.fillna(y.mean(numeric_only=True) if hasattr(y, 'mean') else 0)
        
        # Vérifier si c'est une classification ou régression
        is_classification = len(y.unique()) <= 20 and config.get('is_classification', False)
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=config.get('test_size', 0.2), random_state=42
        )
        
        # Standardisation
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        methods = config.get('methods', ['linear'])
        
        # Régression Linéaire
        if 'linear' in methods:
            results['models']['linear'] = self._linear_regression(
                X_train_scaled, X_test_scaled, y_train, y_test, config
            )
        
        # Régression Polynomiale
        if 'polynomial' in methods:
            results['models']['polynomial'] = self._polynomial_regression(
                X_train, X_test, y_train, y_test, config
            )
        
        # Ridge Regression
        if 'ridge' in methods:
            results['models']['ridge'] = self._ridge_regression(
                X_train_scaled, X_test_scaled, y_train, y_test, config
            )
        
        # Lasso Regression
        if 'lasso' in methods:
            results['models']['lasso'] = self._lasso_regression(
                X_train_scaled, X_test_scaled, y_train, y_test, config
            )
        
        # ElasticNet
        if 'elastic' in methods:
            results['models']['elastic_net'] = self._elastic_net_regression(
                X_train_scaled, X_test_scaled, y_train, y_test, config
            )
        
        # Régression Logistique (pour classification)
        if 'logistic' in methods and is_classification:
            results['models']['logistic'] = self._logistic_regression(
                X_train_scaled, X_test_scaled, y_train, y_test, config
            )
        
        # Comparaison des modèles
        results['summary'] = self._compare_models(results['models'], is_classification)

        # Choisir une clé de meilleur modèle (utilisable côté UI)
        best_key = None
        if not is_classification and results['models']:
            best_key = max(
                results['models'].items(),
                key=lambda kv: kv[1].get('test_metrics', {}).get('r2', float('-inf'))
            )[0]
        elif is_classification and results['models']:
            best_key = max(
                results['models'].items(),
                key=lambda kv: kv[1].get('test_metrics', {}).get('f1', float('-inf'))
            )[0]

        self._best_model_label = results['summary'].get('best_model')
        if best_key:
            results['summary']['best_model_key'] = best_key
            # Entraîner un modèle final pour /predict
            try:
                self._train_predictor(best_key, X, y, config)
            except Exception:
                # Ne pas faire échouer l'analyse si l'entraînement final échoue
                self._predict_model = None
        
        return results
    
    def _linear_regression(self, X_train, X_test, y_train, y_test, config):
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train, y_train, 
                                   cv=config.get('cv_folds', 5), 
                                   scoring='r2')
        
        return {
            'method': 'Régression Linéaire',
            'coefficients': model.coef_.tolist(),
            'intercept': float(model.intercept_),
            'train_metrics': {
                'r2': float(r2_score(y_train, y_pred_train)),
                'mse': float(mean_squared_error(y_train, y_pred_train)),
                'rmse': float(np.sqrt(mean_squared_error(y_train, y_pred_train))),
                'mae': float(mean_absolute_error(y_train, y_pred_train))
            },
            'test_metrics': {
                'r2': float(r2_score(y_test, y_pred_test)),
                'mse': float(mean_squared_error(y_test, y_pred_test)),
                'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred_test))),
                'mae': float(mean_absolute_error(y_test, y_pred_test))
            },
            'cv_scores': {
                'mean': float(cv_scores.mean()),
                'std': float(cv_scores.std()),
                'scores': cv_scores.tolist()
            },
            'predictions_sample': y_pred_test[:10].tolist(),
            'actual_sample': y_test[:10].tolist(),
            'residuals_sample': (y_test - y_pred_test)[:10].tolist()
        }
    
    def _polynomial_regression(self, X_train, X_test, y_train, y_test, config):
        degree = config.get('polynomial_degree', 2)
        poly = PolynomialFeatures(degree=degree)
        
        X_train_poly = poly.fit_transform(X_train)
        X_test_poly = poly.transform(X_test)
        
        model = LinearRegression()
        model.fit(X_train_poly, y_train)
        
        y_pred_train = model.predict(X_train_poly)
        y_pred_test = model.predict(X_test_poly)
        
        return {
            'method': f'Régression Polynomiale (degré {degree})',
            'degree': degree,
            'n_features': X_train_poly.shape[1],
            'train_metrics': {
                'r2': float(r2_score(y_train, y_pred_train)),
                'mse': float(mean_squared_error(y_train, y_pred_train)),
                'rmse': float(np.sqrt(mean_squared_error(y_train, y_pred_train))),
                'mae': float(mean_absolute_error(y_train, y_pred_train))
            },
            'test_metrics': {
                'r2': float(r2_score(y_test, y_pred_test)),
                'mse': float(mean_squared_error(y_test, y_pred_test)),
                'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred_test))),
                'mae': float(mean_absolute_error(y_test, y_pred_test))
            },
            'predictions_sample': y_pred_test[:10].tolist(),
            'actual_sample': y_test[:10].tolist(),
            'residuals_sample': (y_test - y_pred_test)[:10].tolist()
        }
    
    def _ridge_regression(self, X_train, X_test, y_train, y_test, config):
        alpha = config.get('ridge_alpha', 1.0)
        model = Ridge(alpha=alpha)
        model.fit(X_train, y_train)
        
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        return {
            'method': 'Ridge Regression (L2)',
            'alpha': alpha,
            'coefficients': model.coef_.tolist(),
            'intercept': float(model.intercept_),
            'train_metrics': {
                'r2': float(r2_score(y_train, y_pred_train)),
                'mse': float(mean_squared_error(y_train, y_pred_train)),
                'rmse': float(np.sqrt(mean_squared_error(y_train, y_pred_train))),
                'mae': float(mean_absolute_error(y_train, y_pred_train))
            },
            'test_metrics': {
                'r2': float(r2_score(y_test, y_pred_test)),
                'mse': float(mean_squared_error(y_test, y_pred_test)),
                'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred_test))),
                'mae': float(mean_absolute_error(y_test, y_pred_test))
            },
            'predictions_sample': y_pred_test[:10].tolist(),
            'actual_sample': y_test[:10].tolist(),
            'residuals_sample': (y_test - y_pred_test)[:10].tolist()
        }
    
    def _lasso_regression(self, X_train, X_test, y_train, y_test, config):
        alpha = config.get('lasso_alpha', 1.0)
        model = Lasso(alpha=alpha)
        model.fit(X_train, y_train)
        
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        # Nombre de coefficients non-nuls (feature selection)
        n_nonzero = np.sum(model.coef_ != 0)
        
        return {
            'method': 'Lasso Regression (L1)',
            'alpha': alpha,
            'coefficients': model.coef_.tolist(),
            'intercept': float(model.intercept_),
            'n_nonzero_coefs': int(n_nonzero),
            'feature_selection': f'{n_nonzero}/{len(model.coef_)} features sélectionnées',
            'train_metrics': {
                'r2': float(r2_score(y_train, y_pred_train)),
                'mse': float(mean_squared_error(y_train, y_pred_train)),
                'rmse': float(np.sqrt(mean_squared_error(y_train, y_pred_train))),
                'mae': float(mean_absolute_error(y_train, y_pred_train))
            },
            'test_metrics': {
                'r2': float(r2_score(y_test, y_pred_test)),
                'mse': float(mean_squared_error(y_test, y_pred_test)),
                'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred_test))),
                'mae': float(mean_absolute_error(y_test, y_pred_test))
            },
            'predictions_sample': y_pred_test[:10].tolist(),
            'actual_sample': y_test[:10].tolist(),
            'residuals_sample': (y_test - y_pred_test)[:10].tolist()
        }
    
    def _elastic_net_regression(self, X_train, X_test, y_train, y_test, config):
        alpha = config.get('elastic_alpha', 1.0)
        l1_ratio = config.get('elastic_l1_ratio', 0.5)
        
        model = ElasticNet(alpha=alpha, l1_ratio=l1_ratio)
        model.fit(X_train, y_train)
        
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        return {
            'method': 'ElasticNet (L1 + L2)',
            'alpha': alpha,
            'l1_ratio': l1_ratio,
            'coefficients': model.coef_.tolist(),
            'intercept': float(model.intercept_),
            'train_metrics': {
                'r2': float(r2_score(y_train, y_pred_train)),
                'mse': float(mean_squared_error(y_train, y_pred_train)),
                'rmse': float(np.sqrt(mean_squared_error(y_train, y_pred_train))),
                'mae': float(mean_absolute_error(y_train, y_pred_train))
            },
            'test_metrics': {
                'r2': float(r2_score(y_test, y_pred_test)),
                'mse': float(mean_squared_error(y_test, y_pred_test)),
                'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred_test))),
                'mae': float(mean_absolute_error(y_test, y_pred_test))
            },
            'predictions_sample': y_pred_test[:10].tolist(),
            'actual_sample': y_test[:10].tolist(),
            'residuals_sample': (y_test - y_pred_test)[:10].tolist()
        }
    
    def _logistic_regression(self, X_train, X_test, y_train, y_test, config):
        model = LogisticRegression(max_iter=1000)
        model.fit(X_train, y_train)
        
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred_test)
        
        return {
            'method': 'Régression Logistique',
            'coefficients': model.coef_.tolist(),
            'intercept': model.intercept_.tolist(),
            'classes': model.classes_.tolist(),
            'train_metrics': {
                'accuracy': float(accuracy_score(y_train, y_pred_train)),
                'precision': float(precision_score(y_train, y_pred_train, average='weighted', zero_division=0)),
                'recall': float(recall_score(y_train, y_pred_train, average='weighted', zero_division=0)),
                'f1': float(f1_score(y_train, y_pred_train, average='weighted', zero_division=0))
            },
            'test_metrics': {
                'accuracy': float(accuracy_score(y_test, y_pred_test)),
                'precision': float(precision_score(y_test, y_pred_test, average='weighted', zero_division=0)),
                'recall': float(recall_score(y_test, y_pred_test, average='weighted', zero_division=0)),
                'f1': float(f1_score(y_test, y_pred_test, average='weighted', zero_division=0))
            },
            'confusion_matrix': cm.tolist(),
            'predictions_sample': y_pred_test[:10].tolist(),
            'probabilities_sample': y_pred_proba[:10].tolist(),
            'actual_sample': y_test[:10].tolist()
        }
    
    def _compare_models(self, models, is_classification):
        """Compare les performances des différents modèles"""
        comparison = []
        
        for name, model_results in models.items():
            if is_classification:
                comparison.append({
                    'model': model_results['method'],
                    'test_accuracy': model_results['test_metrics'].get('accuracy', 0),
                    'test_f1': model_results['test_metrics'].get('f1', 0),
                })
            else:
                comparison.append({
                    'model': model_results['method'],
                    'test_r2': model_results['test_metrics']['r2'],
                    'test_rmse': model_results['test_metrics']['rmse'],
                })
        
        # Trier par meilleure performance
        if is_classification:
            comparison.sort(key=lambda x: x['test_f1'], reverse=True)
        else:
            comparison.sort(key=lambda x: x['test_r2'], reverse=True)
        
        return {
            'best_model': comparison[0]['model'] if comparison else None,
            'comparison': comparison,
            'is_classification': is_classification
        }
