import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score, 
                            roc_auc_score, confusion_matrix, classification_report)
try:
    import xgboost as xgb
    import lightgbm as lgb
    ADVANCED_LIBS = True
except ImportError:
    ADVANCED_LIBS = False

# Import validation module
try:
    from utils.data_validator import FeatureValidator
    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False

class ClassificationAnalyzer:
    def __init__(self, df):
        self.df = df
        
    def perform_analysis(self, config):
        """
        Classification avec différents algorithmes
        config = {
            'target': 'nom_colonne_cible',
            'features': ['col1', 'col2', ...],
            'methods': ['knn', 'svm', 'random_forest', 'decision_tree', 'naive_bayes', 
                       'gradient_boosting', 'xgboost', 'lightgbm'],
            'test_size': 0.2,
            'cv_folds': 5,
            'tune_hyperparameters': False
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
            is_valid, issues = FeatureValidator.validate_classification_features(X_raw, y_raw)
            
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
        y = self.df[config['target']]
        
        # Encoder la variable cible si nécessaire
        le = LabelEncoder()
        if y.dtype == 'object':
            y = le.fit_transform(y)
            results['label_mapping'] = dict(zip(le.classes_, le.transform(le.classes_)))
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=config.get('test_size', 0.2), random_state=42, stratify=y
        )
        
        # Standardisation
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        methods = config.get('methods', ['knn', 'random_forest'])
        
        # K-Nearest Neighbors
        if 'knn' in methods:
            results['models']['knn'] = self._knn_classification(
                X_train_scaled, X_test_scaled, y_train, y_test, config
            )
        
        # Support Vector Machine
        if 'svm' in methods:
            results['models']['svm'] = self._svm_classification(
                X_train_scaled, X_test_scaled, y_train, y_test, config
            )
        
        # Random Forest
        if 'random_forest' in methods:
            results['models']['random_forest'] = self._random_forest_classification(
                X_train, X_test, y_train, y_test, config
            )
        
        # Decision Tree
        if 'decision_tree' in methods:
            results['models']['decision_tree'] = self._decision_tree_classification(
                X_train, X_test, y_train, y_test, config
            )
        
        # Naive Bayes
        if 'naive_bayes' in methods:
            results['models']['naive_bayes'] = self._naive_bayes_classification(
                X_train_scaled, X_test_scaled, y_train, y_test, config
            )
        
        # Gradient Boosting
        if 'gradient_boosting' in methods:
            results['models']['gradient_boosting'] = self._gradient_boosting_classification(
                X_train, X_test, y_train, y_test, config
            )
        
        # XGBoost
        if 'xgboost' in methods and ADVANCED_LIBS:
            results['models']['xgboost'] = self._xgboost_classification(
                X_train, X_test, y_train, y_test, config
            )
        
        # LightGBM
        if 'lightgbm' in methods and ADVANCED_LIBS:
            results['models']['lightgbm'] = self._lightgbm_classification(
                X_train, X_test, y_train, y_test, config
            )
        
        # AdaBoost
        if 'adaboost' in methods:
            results['models']['adaboost'] = self._adaboost_classification(
                X_train, X_test, y_train, y_test, config
            )
        
        # Comparaison des modèles
        results['summary'] = self._compare_models(results['models'])
        
        return results
    
    def _knn_classification(self, X_train, X_test, y_train, y_test, config):
        n_neighbors = config.get('knn_neighbors', 5)
        model = KNeighborsClassifier(n_neighbors=n_neighbors)
        model.fit(X_train, y_train)
        
        return self._evaluate_classifier(model, X_train, X_test, y_train, y_test, 
                                        f'K-Nearest Neighbors (k={n_neighbors})', config)
    
    def _svm_classification(self, X_train, X_test, y_train, y_test, config):
        kernel = config.get('svm_kernel', 'rbf')
        C = config.get('svm_C', 1.0)
        
        model = SVC(kernel=kernel, C=C, probability=True)
        model.fit(X_train, y_train)
        
        return self._evaluate_classifier(model, X_train, X_test, y_train, y_test, 
                                        f'Support Vector Machine ({kernel})', config)
    
    def _random_forest_classification(self, X_train, X_test, y_train, y_test, config):
        n_estimators = config.get('rf_n_estimators', 100)
        max_depth = config.get('rf_max_depth', None)
        
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        result = self._evaluate_classifier(model, X_train, X_test, y_train, y_test, 
                                          'Random Forest', config)
        
        # Feature importance
        feature_importance = list(zip(config['features'], model.feature_importances_))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        result['feature_importance'] = [
            {'feature': f, 'importance': float(imp)} 
            for f, imp in feature_importance
        ]
        
        return result
    
    def _decision_tree_classification(self, X_train, X_test, y_train, y_test, config):
        max_depth = config.get('dt_max_depth', None)
        
        model = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
        model.fit(X_train, y_train)
        
        result = self._evaluate_classifier(model, X_train, X_test, y_train, y_test, 
                                          'Decision Tree', config)
        
        # Feature importance
        feature_importance = list(zip(config['features'], model.feature_importances_))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        result['feature_importance'] = [
            {'feature': f, 'importance': float(imp)} 
            for f, imp in feature_importance
        ]
        result['tree_depth'] = int(model.get_depth())
        result['n_leaves'] = int(model.get_n_leaves())
        
        return result
    
    def _naive_bayes_classification(self, X_train, X_test, y_train, y_test, config):
        model = GaussianNB()
        model.fit(X_train, y_train)
        
        return self._evaluate_classifier(model, X_train, X_test, y_train, y_test, 
                                        'Naive Bayes (Gaussian)', config)
    
    def _gradient_boosting_classification(self, X_train, X_test, y_train, y_test, config):
        n_estimators = config.get('gb_n_estimators', 100)
        learning_rate = config.get('gb_learning_rate', 0.1)
        
        model = GradientBoostingClassifier(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            random_state=42
        )
        model.fit(X_train, y_train)
        
        result = self._evaluate_classifier(model, X_train, X_test, y_train, y_test, 
                                          'Gradient Boosting', config)
        
        # Feature importance
        feature_importance = list(zip(config['features'], model.feature_importances_))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        result['feature_importance'] = [
            {'feature': f, 'importance': float(imp)} 
            for f, imp in feature_importance
        ]
        
        return result
    
    def _xgboost_classification(self, X_train, X_test, y_train, y_test, config):
        n_estimators = config.get('xgb_n_estimators', 100)
        learning_rate = config.get('xgb_learning_rate', 0.1)
        max_depth = config.get('xgb_max_depth', 6)
        
        model = xgb.XGBClassifier(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            random_state=42,
            use_label_encoder=False,
            eval_metric='logloss'
        )
        model.fit(X_train, y_train)
        
        result = self._evaluate_classifier(model, X_train, X_test, y_train, y_test, 
                                          'XGBoost', config)
        
        # Feature importance
        feature_importance = list(zip(config['features'], model.feature_importances_))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        result['feature_importance'] = [
            {'feature': f, 'importance': float(imp)} 
            for f, imp in feature_importance
        ]
        
        return result
    
    def _lightgbm_classification(self, X_train, X_test, y_train, y_test, config):
        n_estimators = config.get('lgbm_n_estimators', 100)
        learning_rate = config.get('lgbm_learning_rate', 0.1)
        
        model = lgb.LGBMClassifier(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            random_state=42,
            verbose=-1
        )
        model.fit(X_train, y_train)
        
        result = self._evaluate_classifier(model, X_train, X_test, y_train, y_test, 
                                          'LightGBM', config)
        
        # Feature importance
        feature_importance = list(zip(config['features'], model.feature_importances_))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        result['feature_importance'] = [
            {'feature': f, 'importance': float(imp)} 
            for f, imp in feature_importance
        ]
        
        return result
    
    def _adaboost_classification(self, X_train, X_test, y_train, y_test, config):
        n_estimators = config.get('ada_n_estimators', 50)
        learning_rate = config.get('ada_learning_rate', 1.0)
        
        model = AdaBoostClassifier(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            random_state=42
        )
        model.fit(X_train, y_train)
        
        result = self._evaluate_classifier(model, X_train, X_test, y_train, y_test, 
                                          'AdaBoost', config)
        
        # Feature importance
        feature_importance = list(zip(config['features'], model.feature_importances_))
        feature_importance.sort(key=lambda x: x[1], reverse=True)
        result['feature_importance'] = [
            {'feature': f, 'importance': float(imp)} 
            for f, imp in feature_importance
        ]
        
        return result
    
    def _evaluate_classifier(self, model, X_train, X_test, y_train, y_test, method_name, config):
        """Évalue un modèle de classification"""
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        # Probabilités si disponibles
        try:
            y_pred_proba_test = model.predict_proba(X_test)
            has_proba = True
        except:
            y_pred_proba_test = None
            has_proba = False
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred_test)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train, y_train, 
                                   cv=config.get('cv_folds', 5), 
                                   scoring='accuracy')
        
        result = {
            'method': method_name,
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
            'cv_scores': {
                'mean': float(cv_scores.mean()),
                'std': float(cv_scores.std()),
                'scores': cv_scores.tolist()
            },
            'confusion_matrix': cm.tolist(),
            'predictions_sample': y_pred_test[:10].tolist()
        }
        
        if has_proba:
            result['probabilities_sample'] = y_pred_proba_test[:10].tolist()
        
        return result
    
    def _compare_models(self, models):
        """Compare les performances des différents modèles"""
        comparison = []
        
        for name, model_results in models.items():
            comparison.append({
                'model': model_results['method'],
                'test_accuracy': model_results['test_metrics']['accuracy'],
                'test_f1': model_results['test_metrics']['f1'],
                'test_precision': model_results['test_metrics']['precision'],
                'test_recall': model_results['test_metrics']['recall'],
                'cv_mean': model_results['cv_scores']['mean']
            })
        
        # Trier par F1-score
        comparison.sort(key=lambda x: x['test_f1'], reverse=True)
        
        return {
            'best_model': comparison[0]['model'] if comparison else None,
            'comparison': comparison
        }
