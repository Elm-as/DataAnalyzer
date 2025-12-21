"""
What-If analysis and counterfactual explanations.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional


class WhatIfAnalyzer:
    """Provide counterfactual explanations and what-if scenarios."""
    
    @staticmethod
    def find_counterfactual(model, X_sample: np.ndarray, feature_names: List[str],
                           current_prediction: int, desired_prediction: int,
                           feature_ranges: Dict[str, Tuple[float, float]],
                           max_changes: int = 3, max_iterations: int = 100) -> Dict[str, Any]:
        """
        Find minimal changes needed to flip prediction.
        
        Args:
            model: Trained model
            X_sample: Current feature values
            feature_names: List of feature names
            current_prediction: Current predicted class
            desired_prediction: Desired predicted class
            feature_ranges: Dictionary of valid ranges for each feature
            max_changes: Maximum number of features to change
            max_iterations: Maximum iterations to try
            
        Returns:
            Counterfactual explanation with suggested changes
        """
        if not hasattr(model, 'predict'):
            return {
                'found': False,
                'message': 'Model does not support prediction'
            }
        
        # Store original values
        original_values = X_sample.copy()
        best_candidate = None
        min_distance = float('inf')
        
        # Try random perturbations
        for _ in range(max_iterations):
            # Create a perturbed sample
            perturbed = X_sample.copy()
            
            # Randomly select features to change (up to max_changes)
            num_changes = np.random.randint(1, max_changes + 1)
            features_to_change = np.random.choice(len(feature_names), num_changes, replace=False)
            
            for idx in features_to_change:
                feature = feature_names[idx]
                if feature in feature_ranges:
                    min_val, max_val = feature_ranges[feature]
                    # Random value within range
                    perturbed[idx] = np.random.uniform(min_val, max_val)
            
            # Check prediction
            pred = model.predict(perturbed.reshape(1, -1))[0]
            
            if pred == desired_prediction:
                # Calculate distance from original
                distance = np.sum((perturbed - original_values) ** 2)
                
                if distance < min_distance:
                    min_distance = distance
                    best_candidate = perturbed.copy()
        
        if best_candidate is not None:
            # Extract changes
            changes = []
            for idx, (orig, new) in enumerate(zip(original_values, best_candidate)):
                if abs(orig - new) > 1e-6:
                    change_pct = ((new - orig) / orig * 100) if orig != 0 else 0
                    changes.append({
                        'feature': feature_names[idx],
                        'original_value': float(orig),
                        'suggested_value': float(new),
                        'change': float(new - orig),
                        'change_percentage': float(change_pct)
                    })
            
            return {
                'found': True,
                'changes': changes,
                'num_changes': len(changes),
                'distance': float(min_distance),
                'message': f'Found counterfactual with {len(changes)} changes'
            }
        
        return {
            'found': False,
            'message': f'Could not find counterfactual within {max_iterations} iterations'
        }
    
    @staticmethod
    def suggest_minimal_changes(model, X_sample: np.ndarray, feature_names: List[str],
                               feature_importance: Dict[str, float],
                               current_prob: float, target_prob: float = 0.7) -> Dict[str, Any]:
        """
        Suggest minimal changes to reach target probability.
        
        Args:
            model: Trained model
            X_sample: Current feature values
            feature_names: List of feature names
            feature_importance: Dictionary of feature importances
            current_prob: Current prediction probability
            target_prob: Target probability to reach
            
        Returns:
            Suggestions for minimal changes
        """
        if current_prob >= target_prob:
            return {
                'needed': False,
                'message': f'Current probability ({current_prob:.2%}) already meets target ({target_prob:.2%})'
            }
        
        # Get coefficients if available (linear models)
        if hasattr(model, 'coef_'):
            coef = model.coef_
            if len(coef.shape) > 1:
                coef = coef[0]
            
            # Sort features by absolute coefficient (impact)
            feature_impacts = []
            for idx, feat in enumerate(feature_names):
                if idx < len(coef):
                    feature_impacts.append({
                        'feature': feat,
                        'coefficient': float(coef[idx]),
                        'current_value': float(X_sample[idx]),
                        'impact_direction': 'increase' if coef[idx] > 0 else 'decrease'
                    })
            
            # Sort by absolute coefficient
            feature_impacts.sort(key=lambda x: abs(x['coefficient']), reverse=True)
            
            # Calculate required change in log-odds
            from scipy.special import logit
            current_logit = logit(np.clip(current_prob, 0.01, 0.99))
            target_logit = logit(np.clip(target_prob, 0.01, 0.99))
            required_change = target_logit - current_logit
            
            # Suggest changes for top features
            suggestions = []
            for impact in feature_impacts[:5]:
                coef = impact['coefficient']
                if abs(coef) > 0:
                    # Calculate how much to change this feature
                    suggested_change = required_change / coef
                    new_value = impact['current_value'] + suggested_change
                    
                    suggestions.append({
                        'feature': impact['feature'],
                        'current_value': impact['current_value'],
                        'suggested_change': float(suggested_change),
                        'suggested_value': float(new_value),
                        'expected_impact': f"{'Increase' if coef > 0 else 'Decrease'} probability"
                    })
            
            return {
                'needed': True,
                'current_probability': float(current_prob),
                'target_probability': float(target_prob),
                'gap': float(target_prob - current_prob),
                'suggestions': suggestions[:3],  # Top 3 suggestions
                'message': 'Suggested changes based on feature coefficients'
            }
        
        return {
            'needed': True,
            'message': 'Minimal changes analysis not available for this model type'
        }
    
    @staticmethod
    def generate_scenarios(X_sample: np.ndarray, feature_names: List[str],
                          model, n_scenarios: int = 5) -> List[Dict[str, Any]]:
        """
        Generate multiple what-if scenarios with small perturbations.
        
        Args:
            X_sample: Current feature values
            feature_names: List of feature names
            model: Trained model
            n_scenarios: Number of scenarios to generate
            
        Returns:
            List of scenario results
        """
        scenarios = []
        
        for i in range(n_scenarios):
            # Create small random perturbations (±10%)
            perturbation = np.random.uniform(-0.1, 0.1, size=X_sample.shape)
            perturbed = X_sample * (1 + perturbation)
            
            # Get prediction
            try:
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(perturbed.reshape(1, -1))[0]
                    pred = model.predict(perturbed.reshape(1, -1))[0]
                    
                    scenarios.append({
                        'scenario_id': i + 1,
                        'prediction': int(pred),
                        'probability': float(proba[pred]),
                        'changes': {
                            feat: float(perturbed[idx] - X_sample[idx])
                            for idx, feat in enumerate(feature_names)
                            if abs(perturbed[idx] - X_sample[idx]) > 1e-6
                        }
                    })
                else:
                    pred = model.predict(perturbed.reshape(1, -1))[0]
                    scenarios.append({
                        'scenario_id': i + 1,
                        'prediction': float(pred),
                        'changes': {
                            feat: float(perturbed[idx] - X_sample[idx])
                            for idx, feat in enumerate(feature_names)
                            if abs(perturbed[idx] - X_sample[idx]) > 1e-6
                        }
                    })
            except Exception:
                continue
        
        return scenarios


class StressTester:
    """Automated stress testing for model robustness."""
    
    @staticmethod
    def run_stress_tests(model, X_test: np.ndarray, y_test: np.ndarray,
                        feature_names: List[str]) -> Dict[str, Any]:
        """
        Run comprehensive stress tests on the model.
        
        Args:
            model: Trained model
            X_test: Test features
            y_test: Test labels
            feature_names: List of feature names
            
        Returns:
            Stress test results
        """
        results = {
            'noise_robustness': {},
            'extreme_values': {},
            'edge_cases': {},
            'overall_robustness': 'unknown'
        }
        
        # Test 1: Noise robustness
        noise_results = StressTester._test_noise_robustness(model, X_test, y_test)
        results['noise_robustness'] = noise_results
        
        # Test 2: Extreme values
        extreme_results = StressTester._test_extreme_values(model, X_test, y_test)
        results['extreme_values'] = extreme_results
        
        # Test 3: Missing features (set to mean)
        missing_results = StressTester._test_missing_features(model, X_test, y_test)
        results['edge_cases'] = missing_results
        
        # Calculate overall robustness score
        scores = []
        if 'score' in noise_results:
            scores.append(noise_results['score'])
        if 'score' in extreme_results:
            scores.append(extreme_results['score'])
        if 'score' in missing_results:
            scores.append(missing_results['score'])
        
        if scores:
            avg_score = np.mean(scores)
            if avg_score > 0.8:
                results['overall_robustness'] = 'high'
            elif avg_score > 0.6:
                results['overall_robustness'] = 'moderate'
            else:
                results['overall_robustness'] = 'low'
            
            results['robustness_score'] = float(avg_score)
        
        return results
    
    @staticmethod
    def _test_noise_robustness(model, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """Test model robustness to noise."""
        try:
            # Get baseline accuracy
            baseline_pred = model.predict(X_test)
            baseline_acc = np.mean(baseline_pred == y_test)
            
            # Add Gaussian noise (5% of std)
            noise_levels = [0.01, 0.05, 0.1]
            results = []
            
            for noise_level in noise_levels:
                X_noisy = X_test + np.random.normal(0, noise_level, X_test.shape)
                noisy_pred = model.predict(X_noisy)
                noisy_acc = np.mean(noisy_pred == y_test)
                
                results.append({
                    'noise_level': noise_level,
                    'accuracy': float(noisy_acc),
                    'accuracy_drop': float(baseline_acc - noisy_acc)
                })
            
            # Score based on accuracy drop
            max_drop = max([r['accuracy_drop'] for r in results])
            score = 1.0 - min(max_drop * 2, 1.0)  # Penalize drops > 50%
            
            return {
                'baseline_accuracy': float(baseline_acc),
                'noise_tests': results,
                'score': float(score),
                'interpretation': 'Robust' if score > 0.8 else 'Moderate' if score > 0.6 else 'Sensitive to noise'
            }
        except Exception as e:
            return {
                'error': f'Noise test failed: {str(e)}'
            }
    
    @staticmethod
    def _test_extreme_values(model, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """Test model with extreme values."""
        try:
            # Get baseline
            baseline_pred = model.predict(X_test)
            baseline_acc = np.mean(baseline_pred == y_test)
            
            # Create extreme values (3x std from mean)
            X_extreme = X_test.copy()
            for col in range(X_test.shape[1]):
                mean = X_test[:, col].mean()
                std = X_test[:, col].std()
                # Set 10% of values to extremes
                n_extreme = int(len(X_test) * 0.1)
                extreme_indices = np.random.choice(len(X_test), n_extreme, replace=False)
                X_extreme[extreme_indices, col] = mean + 3 * std * np.random.choice([-1, 1], n_extreme)
            
            extreme_pred = model.predict(X_extreme)
            extreme_acc = np.mean(extreme_pred == y_test)
            
            score = extreme_acc / baseline_acc if baseline_acc > 0 else 0
            
            return {
                'baseline_accuracy': float(baseline_acc),
                'extreme_accuracy': float(extreme_acc),
                'accuracy_drop': float(baseline_acc - extreme_acc),
                'score': float(score),
                'interpretation': 'Robust' if score > 0.9 else 'Moderate' if score > 0.7 else 'Sensitive to extremes'
            }
        except Exception as e:
            return {
                'error': f'Extreme values test failed: {str(e)}'
            }
    
    @staticmethod
    def _test_missing_features(model, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """Test model with missing features (replaced by mean)."""
        try:
            # Get baseline
            baseline_pred = model.predict(X_test)
            baseline_acc = np.mean(baseline_pred == y_test)
            
            # Set random features to mean (simulating missing)
            X_missing = X_test.copy()
            col_means = X_test.mean(axis=0)
            
            # Set 20% of values to mean
            mask = np.random.random(X_test.shape) < 0.2
            X_missing[mask] = np.take(col_means, np.where(mask)[1])
            
            missing_pred = model.predict(X_missing)
            missing_acc = np.mean(missing_pred == y_test)
            
            score = missing_acc / baseline_acc if baseline_acc > 0 else 0
            
            return {
                'baseline_accuracy': float(baseline_acc),
                'missing_accuracy': float(missing_acc),
                'accuracy_drop': float(baseline_acc - missing_acc),
                'score': float(score),
                'interpretation': 'Robust' if score > 0.9 else 'Moderate' if score > 0.7 else 'Sensitive to missing values'
            }
        except Exception as e:
            return {
                'error': f'Missing features test failed: {str(e)}'
            }
