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
        
        # Préparation des données
        X = self.df[config['features']].fillna(self.df[config['features']].mean())
        y = self.df[config['target']].fillna(self.df[config['target']].mean())
        
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
            'predictions_sample': y_pred_test[:10].tolist()
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
            'predictions_sample': y_pred_test[:10].tolist()
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
            'predictions_sample': y_pred_test[:10].tolist()
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
            'predictions_sample': y_pred_test[:10].tolist()
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
            'predictions_sample': y_pred_test[:10].tolist()
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
            'probabilities_sample': y_pred_proba[:10].tolist()
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
