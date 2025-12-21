"""
Module for model explainability and interpretability.
Provides feature importance, local explanations, and clear interpretation messages.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional


class ExplainabilityAnalyzer:
    """Provides explainability for ML models."""
    
    @staticmethod
    def get_feature_importance(model, feature_names: List[str], model_type: str = 'tree') -> Dict[str, Any]:
        """
        Extract feature importance from a trained model.
        
        Args:
            model: Trained sklearn model
            feature_names: List of feature names
            model_type: Type of model ('tree', 'linear', 'ensemble')
            
        Returns:
            Dictionary with top 10 features and their importance scores
        """
        try:
            # Tree-based models (Random Forest, XGBoost, LightGBM, etc.)
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                
            # Linear models (Logistic Regression, Linear Regression, etc.)
            elif hasattr(model, 'coef_'):
                coef = model.coef_
                if len(coef.shape) > 1:  # Multi-class
                    importances = np.abs(coef).mean(axis=0)
                else:
                    importances = np.abs(coef)
                    
            else:
                return {
                    'available': False,
                    'message': 'Feature importance not available for this model type'
                }
            
            # Create sorted importance list
            importance_dict = dict(zip(feature_names, importances))
            sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
            
            # Get top 10
            top_10 = sorted_features[:10]
            
            # Calculate percentage
            total_importance = sum(importances)
            top_10_with_pct = [
                {
                    'feature': feat,
                    'importance': float(imp),
                    'percentage': float(imp / total_importance * 100) if total_importance > 0 else 0
                }
                for feat, imp in top_10
            ]
            
            return {
                'available': True,
                'top_features': top_10_with_pct,
                'total_features': len(feature_names),
                'top_10_cumulative': sum([f['percentage'] for f in top_10_with_pct])
            }
            
        except Exception as e:
            return {
                'available': False,
                'message': f'Error extracting feature importance: {str(e)}'
            }
    
    @staticmethod
    def explain_prediction_local(model, X_sample: np.ndarray, feature_names: List[str], 
                                base_value: float = 0.5) -> Dict[str, Any]:
        """
        Provide local explanation for a single prediction.
        Uses a simplified SHAP-like approach based on feature values and model coefficients.
        
        Args:
            model: Trained model
            X_sample: Single sample to explain (1D array)
            feature_names: List of feature names
            base_value: Base probability/value (default 0.5 for classification)
            
        Returns:
            Dictionary with feature contributions
        """
        try:
            # For linear models, use coefficients directly
            if hasattr(model, 'coef_'):
                coef = model.coef_
                if len(coef.shape) > 1:
                    coef = coef[0]  # Use first class for binary
                
                # Calculate contributions
                contributions = X_sample * coef
                
            # For tree models, approximate with feature importance
            elif hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                # Approximate contribution by multiplying feature value with importance
                contributions = X_sample * importances
                
            else:
                return {
                    'available': False,
                    'message': 'Local explanations not available for this model type'
                }
            
            # Create sorted contribution list
            contrib_dict = dict(zip(feature_names, contributions))
            sorted_contrib = sorted(contrib_dict.items(), key=lambda x: abs(x[1]), reverse=True)
            
            # Get top contributors (both positive and negative)
            top_contributors = sorted_contrib[:5]
            
            explanations = []
            for feat, contrib in top_contributors:
                direction = "↑" if contrib > 0 else "↓"
                effect = "increases" if contrib > 0 else "decreases"
                explanations.append({
                    'feature': feat,
                    'contribution': float(contrib),
                    'direction': direction,
                    'message': f"{feat} {direction} prediction ({effect}: {abs(contrib):.3f})"
                })
            
            return {
                'available': True,
                'base_value': base_value,
                'contributions': explanations,
                'total_effect': float(np.sum(contributions))
            }
            
        except Exception as e:
            return {
                'available': False,
                'message': f'Error generating local explanation: {str(e)}'
            }
    
    @staticmethod
    def generate_interpretation_messages(prediction_class: Any, probability: float, 
                                        contributions: List[Dict]) -> List[str]:
        """
        Generate clear, human-readable interpretation messages.
        
        Args:
            prediction_class: Predicted class/value
            probability: Prediction probability/confidence
            contributions: List of feature contributions
            
        Returns:
            List of interpretation messages
        """
        messages = []
        
        # Main prediction message
        conf_level = "high" if probability > 0.8 else "moderate" if probability > 0.6 else "low"
        messages.append(
            f"Prediction: {prediction_class} with {conf_level} confidence ({probability*100:.1f}%)"
        )
        
        # Top contributors
        if contributions:
            messages.append("Top factors influencing this prediction:")
            for i, contrib in enumerate(contributions[:3], 1):
                messages.append(
                    f"{i}. {contrib['message']}"
                )
        
        return messages


class ModelAuditor:
    """Automatic model audit and justification."""
    
    @staticmethod
    def audit_model_selection(models: Dict[str, Dict], best_model_name: str, 
                              y_true: np.ndarray = None) -> Dict[str, Any]:
        """
        Audit and justify the selection of the best model.
        
        Args:
            models: Dictionary of model results
            best_model_name: Name of the selected best model
            y_true: True labels for bias detection (optional)
            
        Returns:
            Audit report with justification and warnings
        """
        if not models or best_model_name not in models:
            return {'error': 'Invalid model data'}
        
        best_model = models[best_model_name]
        audit_report = {
            'selected_model': best_model_name,
            'justification': [],
            'warnings': [],
            'bias_detected': [],
            'overfitting_risk': 'low',
            'stability_score': 0.0
        }
        
        # Get metrics
        cv_scores = best_model.get('cross_validation', {})
        test_metrics = best_model.get('test_metrics', {})
        train_metrics = best_model.get('train_metrics', {})
        
        # Justification based on performance
        if test_metrics.get('accuracy'):
            acc = test_metrics['accuracy']
            audit_report['justification'].append(
                f"Selected for highest accuracy: {acc:.3f}"
            )
            if acc < 0.6:
                audit_report['warnings'].append(
                    f"Low accuracy ({acc:.3f}) - consider data quality or feature engineering"
                )
        
        # Cross-validation analysis
        if cv_scores:
            cv_mean = cv_scores.get('mean', 0)
            cv_std = cv_scores.get('std', 0)
            audit_report['stability_score'] = float(cv_mean)
            
            if cv_std > 0.1:
                audit_report['warnings'].append(
                    f"High variance in cross-validation (std={cv_std:.3f}) - model may be unstable"
                )
            else:
                audit_report['justification'].append(
                    f"Stable cross-validation scores (mean={cv_mean:.3f}, std={cv_std:.3f})"
                )
        
        # Overfitting detection
        if train_metrics and test_metrics:
            train_acc = train_metrics.get('accuracy', 0)
            test_acc = test_metrics.get('accuracy', 0)
            
            if train_acc - test_acc > 0.15:
                audit_report['overfitting_risk'] = 'high'
                audit_report['warnings'].append(
                    f"Potential overfitting detected (train={train_acc:.3f}, test={test_acc:.3f})"
                )
            elif train_acc - test_acc > 0.08:
                audit_report['overfitting_risk'] = 'moderate'
                audit_report['warnings'].append(
                    f"Moderate overfitting (train={train_acc:.3f}, test={test_acc:.3f})"
                )
            else:
                audit_report['overfitting_risk'] = 'low'
                audit_report['justification'].append(
                    f"Good generalization (train={train_acc:.3f}, test={test_acc:.3f})"
                )
        
        # Class imbalance bias detection
        if y_true is not None:
            class_dist = ModelAuditor._analyze_class_distribution(y_true)
            if class_dist['imbalance_ratio'] > 3:
                audit_report['bias_detected'].append(
                    f"Class imbalance detected: {class_dist['imbalance_ratio']:.1f}:1 ratio"
                )
                audit_report['warnings'].append(
                    "Consider using class weights or resampling techniques"
                )
        
        # Model comparison
        if len(models) > 1:
            other_models = {k: v for k, v in models.items() if k != best_model_name}
            comparison = ModelAuditor._compare_with_others(best_model, other_models)
            if comparison['margin'] < 0.05:
                audit_report['warnings'].append(
                    f"Close performance with other models (margin: {comparison['margin']:.3f}) - "
                    f"consider ensemble methods"
                )
        
        return audit_report
    
    @staticmethod
    def _analyze_class_distribution(y: np.ndarray) -> Dict[str, Any]:
        """Analyze class distribution for imbalance."""
        unique, counts = np.unique(y, return_counts=True)
        max_count = np.max(counts)
        min_count = np.min(counts)
        
        return {
            'classes': len(unique),
            'imbalance_ratio': max_count / min_count if min_count > 0 else float('inf'),
            'distribution': dict(zip(unique, counts))
        }
    
    @staticmethod
    def _compare_with_others(best_model: Dict, other_models: Dict) -> Dict[str, Any]:
        """Compare best model with others."""
        best_acc = best_model.get('test_metrics', {}).get('accuracy', 0)
        
        other_accs = []
        for model in other_models.values():
            acc = model.get('test_metrics', {}).get('accuracy', 0)
            if acc > 0:
                other_accs.append(acc)
        
        if not other_accs:
            return {'margin': 1.0}
        
        second_best = max(other_accs)
        return {
            'margin': best_acc - second_best,
            'second_best_accuracy': second_best
        }


class CalibrationAnalyzer:
    """Analyze and improve probability calibration."""
    
    @staticmethod
    def analyze_calibration(y_true: np.ndarray, y_proba: np.ndarray, 
                           n_bins: int = 10) -> Dict[str, Any]:
        """
        Analyze probability calibration.
        
        Args:
            y_true: True labels (binary)
            y_proba: Predicted probabilities
            n_bins: Number of bins for calibration curve
            
        Returns:
            Calibration analysis including Brier score and curve data
        """
        try:
            # Brier score (lower is better)
            brier_score = np.mean((y_proba - y_true) ** 2)
            
            # Calibration curve
            bins = np.linspace(0, 1, n_bins + 1)
            bin_indices = np.digitize(y_proba, bins[:-1]) - 1
            bin_indices = np.clip(bin_indices, 0, n_bins - 1)
            
            calibration_data = []
            for i in range(n_bins):
                mask = bin_indices == i
                if np.sum(mask) > 0:
                    mean_predicted = np.mean(y_proba[mask])
                    mean_actual = np.mean(y_true[mask])
                    count = np.sum(mask)
                    
                    calibration_data.append({
                        'bin': i,
                        'predicted_probability': float(mean_predicted),
                        'actual_probability': float(mean_actual),
                        'count': int(count),
                        'calibration_error': float(abs(mean_predicted - mean_actual))
                    })
            
            # Expected Calibration Error (ECE)
            ece = np.mean([bin_data['calibration_error'] for bin_data in calibration_data])
            
            # Interpretation
            interpretation = []
            if brier_score < 0.1:
                interpretation.append("Excellent calibration - probabilities are well-calibrated")
            elif brier_score < 0.2:
                interpretation.append("Good calibration - probabilities are reasonably reliable")
            else:
                interpretation.append("Poor calibration - consider calibrating the model")
            
            if ece > 0.1:
                interpretation.append(
                    f"High calibration error (ECE={ece:.3f}) - predicted probabilities may be overconfident"
                )
            
            return {
                'brier_score': float(brier_score),
                'expected_calibration_error': float(ece),
                'calibration_curve': calibration_data,
                'interpretation': interpretation,
                'is_well_calibrated': brier_score < 0.15 and ece < 0.1
            }
            
        except Exception as e:
            return {
                'error': f'Error analyzing calibration: {str(e)}'
            }
    
    @staticmethod
    def suggest_calibration_method(brier_score: float, model_type: str) -> Dict[str, str]:
        """Suggest calibration method if needed."""
        if brier_score < 0.15:
            return {
                'needed': False,
                'message': 'Model is well-calibrated, no adjustment needed'
            }
        
        suggestions = {
            'tree': 'Platt scaling (sigmoid) recommended for tree-based models',
            'ensemble': 'Isotonic regression recommended for ensemble models',
            'linear': 'Model already produces calibrated probabilities',
            'svm': 'Platt scaling recommended for SVM'
        }
        
        return {
            'needed': True,
            'method': suggestions.get(model_type, 'Platt scaling or isotonic regression'),
            'message': f'Calibration recommended (Brier score: {brier_score:.3f})'
        }
