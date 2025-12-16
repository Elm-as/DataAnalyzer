import pandas as pd
import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

class DiscriminantAnalyzer:
    def __init__(self, df):
        self.df = df
        
    def perform_analysis(self, config):
        """
        Analyse discriminante LDA et QDA
        config = {
            'target': 'nom_colonne_cible',
            'features': ['col1', 'col2', ...],
            'methods': ['lda', 'qda'],
            'test_size': 0.2,
            'cv_folds': 5,
            'n_components': None  # Pour LDA, réduction de dimensionalité
        }
        """
        results = {
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
        
        # Standardisation (recommandée pour LDA/QDA)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        methods = config.get('methods', ['lda', 'qda'])
        
        # Linear Discriminant Analysis
        if 'lda' in methods:
            results['models']['lda'] = self._lda_analysis(
                X_train_scaled, X_test_scaled, y_train, y_test, config
            )
        
        # Quadratic Discriminant Analysis
        if 'qda' in methods:
            results['models']['qda'] = self._qda_analysis(
                X_train_scaled, X_test_scaled, y_train, y_test, config
            )
        
        # Comparaison des modèles
        results['summary'] = self._compare_models(results['models'])
        
        return results
    
    def _lda_analysis(self, X_train, X_test, y_train, y_test, config):
        """Linear Discriminant Analysis"""
        n_components = config.get('n_components', None)
        
        # Limiter n_components au minimum entre n_features-1 et n_classes-1
        n_classes = len(np.unique(y_train))
        n_features = X_train.shape[1]
        max_components = min(n_features, n_classes - 1)
        
        if n_components is not None:
            n_components = min(n_components, max_components)
        else:
            n_components = max_components
        
        model = LinearDiscriminantAnalysis(n_components=n_components)
        model.fit(X_train, y_train)
        
        # Prédictions
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        y_pred_proba_test = model.predict_proba(X_test)
        
        # Transform pour voir la projection
        X_train_lda = model.transform(X_train)
        X_test_lda = model.transform(X_test)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train, y_train, 
                                   cv=config.get('cv_folds', 5), 
                                   scoring='accuracy')
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred_test)
        
        result = {
            'method': 'Linear Discriminant Analysis (LDA)',
            'n_components': n_components,
            'explained_variance_ratio': model.explained_variance_ratio_.tolist() if hasattr(model, 'explained_variance_ratio_') else None,
            'classes': model.classes_.tolist(),
            'prior_probabilities': model.priors_.tolist(),
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
            'predictions_sample': y_pred_test[:10].tolist(),
            'probabilities_sample': y_pred_proba_test[:10].tolist(),
            'transformed_dimensions': X_train_lda.shape[1],
            'interpretation': self._interpret_lda(model, config['features'])
        }
        
        return result
    
    def _qda_analysis(self, X_train, X_test, y_train, y_test, config):
        """Quadratic Discriminant Analysis"""
        model = QuadraticDiscriminantAnalysis()
        model.fit(X_train, y_train)
        
        # Prédictions
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        y_pred_proba_test = model.predict_proba(X_test)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train, y_train, 
                                   cv=config.get('cv_folds', 5), 
                                   scoring='accuracy')
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred_test)
        
        result = {
            'method': 'Quadratic Discriminant Analysis (QDA)',
            'classes': model.classes_.tolist(),
            'prior_probabilities': model.priors_.tolist(),
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
            'predictions_sample': y_pred_test[:10].tolist(),
            'probabilities_sample': y_pred_proba_test[:10].tolist(),
            'note': 'QDA assume que chaque classe a sa propre matrice de covariance'
        }
        
        return result
    
    def _interpret_lda(self, model, feature_names):
        """Interprétation des composantes LDA"""
        if not hasattr(model, 'scalings_'):
            return None
        
        # Scalings (coefficients) pour chaque composante
        scalings = model.scalings_
        
        interpretations = []
        for i in range(scalings.shape[1]):
            component_loadings = list(zip(feature_names, scalings[:, i]))
            component_loadings.sort(key=lambda x: abs(x[1]), reverse=True)
            
            interpretations.append({
                'component': i + 1,
                'variance_explained': float(model.explained_variance_ratio_[i]) if hasattr(model, 'explained_variance_ratio_') else None,
                'top_features': [
                    {'feature': f, 'loading': float(l)} 
                    for f, l in component_loadings[:5]
                ]
            })
        
        return interpretations
    
    def _compare_models(self, models):
        """Compare LDA et QDA"""
        comparison = []
        
        for name, model_results in models.items():
            comparison.append({
                'model': model_results['method'],
                'test_accuracy': model_results['test_metrics']['accuracy'],
                'test_f1': model_results['test_metrics']['f1'],
                'cv_mean': model_results['cv_scores']['mean'],
                'cv_std': model_results['cv_scores']['std']
            })
        
        comparison.sort(key=lambda x: x['test_f1'], reverse=True)
        
        recommendation = ""
        if len(comparison) == 2:
            lda_acc = next((m['test_accuracy'] for m in comparison if 'LDA' in m['model']), 0)
            qda_acc = next((m['test_accuracy'] for m in comparison if 'QDA' in m['model']), 0)
            
            if lda_acc > qda_acc:
                recommendation = "LDA est recommandé : les classes partagent probablement une matrice de covariance commune"
            elif qda_acc > lda_acc:
                recommendation = "QDA est recommandé : les classes ont des matrices de covariance différentes"
            else:
                recommendation = "Les deux modèles sont équivalents"
        
        return {
            'best_model': comparison[0]['model'] if comparison else None,
            'comparison': comparison,
            'recommendation': recommendation
        }
