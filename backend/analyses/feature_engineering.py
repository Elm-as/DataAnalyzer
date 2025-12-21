"""
Automatic feature engineering suggestions and transformations.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from collections import Counter


class FeatureEngineer:
    """Automatic feature engineering and suggestions."""
    
    @staticmethod
    def analyze_and_suggest(df: pd.DataFrame, target_col: str = None) -> Dict[str, Any]:
        """
        Analyze dataset and suggest feature engineering opportunities.
        
        Args:
            df: Input dataframe
            target_col: Target column name (optional)
            
        Returns:
            Dictionary with suggestions and automatically engineered features
        """
        suggestions = {
            'categorical_grouping': [],
            'normalization': [],
            'derived_features': [],
            'transformations': [],
            'interaction_features': []
        }
        
        feature_cols = [col for col in df.columns if col != target_col]
        
        # Analyze categorical columns for rare category grouping
        for col in feature_cols:
            if df[col].dtype == 'object' or df[col].nunique() < 20:
                suggestion = FeatureEngineer._suggest_categorical_grouping(df[col])
                if suggestion:
                    suggestions['categorical_grouping'].append({
                        'column': col,
                        'suggestion': suggestion
                    })
        
        # Analyze numeric columns for normalization
        numeric_cols = df[feature_cols].select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            suggestion = FeatureEngineer._suggest_normalization(df[col])
            if suggestion:
                suggestions['normalization'].append({
                    'column': col,
                    'method': suggestion
                })
        
        # Suggest derived features
        derived = FeatureEngineer._suggest_derived_features(df, feature_cols)
        suggestions['derived_features'] = derived
        
        # Suggest transformations for skewed data
        for col in numeric_cols:
            if len(df[col].dropna()) > 0:
                skewness = df[col].skew()
                if abs(skewness) > 1:
                    suggestions['transformations'].append({
                        'column': col,
                        'skewness': float(skewness),
                        'suggested_transform': 'log' if skewness > 1 else 'sqrt',
                        'reason': f'High skewness detected ({skewness:.2f})'
                    })
        
        # Suggest interaction features for numeric columns
        if len(numeric_cols) >= 2:
            interactions = FeatureEngineer._suggest_interactions(df, numeric_cols, target_col)
            suggestions['interaction_features'] = interactions[:5]  # Top 5
        
        return suggestions
    
    @staticmethod
    def _suggest_categorical_grouping(series: pd.Series) -> str:
        """Suggest grouping for rare categories."""
        value_counts = series.value_counts()
        total = len(series)
        
        # Find categories with < 5% frequency
        rare_categories = value_counts[value_counts / total < 0.05]
        
        if len(rare_categories) > 2:
            return f"Group {len(rare_categories)} rare categories (< 5% frequency) into 'Other'"
        
        return None
    
    @staticmethod
    def _suggest_normalization(series: pd.Series) -> str:
        """Suggest normalization method based on data distribution."""
        if series.isna().all():
            return None
        
        data = series.dropna()
        
        # Check range
        min_val, max_val = data.min(), data.max()
        data_range = max_val - min_val
        
        # Check for outliers using IQR
        q1, q3 = data.quantile(0.25), data.quantile(0.75)
        iqr = q3 - q1
        outliers = ((data < q1 - 1.5 * iqr) | (data > q3 + 1.5 * iqr)).sum()
        
        if outliers > len(data) * 0.1:
            return "RobustScaler (many outliers detected)"
        elif data_range > 1000:
            return "StandardScaler (large range)"
        elif min_val >= 0 and max_val <= 1:
            return "No normalization needed (already in [0,1])"
        else:
            return "StandardScaler or MinMaxScaler"
    
    @staticmethod
    def _suggest_derived_features(df: pd.DataFrame, feature_cols: List[str]) -> List[Dict[str, Any]]:
        """Suggest derived features based on common patterns."""
        suggestions = []
        
        # Look for family-related columns (common in Titanic-like datasets)
        family_patterns = ['sibsp', 'parch', 'sibling', 'parent', 'child']
        family_cols = [col for col in feature_cols 
                      if any(pattern in col.lower() for pattern in family_patterns)]
        
        if len(family_cols) >= 2:
            suggestions.append({
                'name': 'FamilySize',
                'formula': f'{" + ".join(family_cols)} + 1',
                'reason': 'Combine family-related features',
                'columns_used': family_cols
            })
            
            suggestions.append({
                'name': 'IsAlone',
                'formula': f'1 if FamilySize == 1 else 0',
                'reason': 'Binary indicator for traveling alone',
                'columns_used': family_cols
            })
        
        # Look for price/fare columns that might benefit from log transform
        price_patterns = ['price', 'fare', 'cost', 'amount', 'salary']
        price_cols = [col for col in feature_cols 
                     if any(pattern in col.lower() for pattern in price_patterns)]
        
        for col in price_cols:
            if col in df.columns and df[col].dtype in [np.float64, np.int64]:
                if (df[col] > 0).all():
                    suggestions.append({
                        'name': f'Log_{col}',
                        'formula': f'log({col})',
                        'reason': 'Log transform for price/fare features',
                        'columns_used': [col]
                    })
        
        # Look for name/title columns
        name_patterns = ['name', 'title', 'full_name']
        name_cols = [col for col in feature_cols 
                    if any(pattern in col.lower() for pattern in name_patterns)]
        
        if name_cols:
            suggestions.append({
                'name': 'Title',
                'formula': f'Extract title from {name_cols[0]} (Mr., Mrs., etc.)',
                'reason': 'Extract social title from name',
                'columns_used': name_cols
            })
        
        return suggestions
    
    @staticmethod
    def _suggest_interactions(df: pd.DataFrame, numeric_cols: List[str], 
                            target_col: str = None) -> List[Dict[str, Any]]:
        """Suggest interaction features between numeric columns."""
        suggestions = []
        
        # Limit to first 10 numeric columns to avoid combinatorial explosion
        cols_to_check = list(numeric_cols)[:10]
        
        for i, col1 in enumerate(cols_to_check):
            for col2 in cols_to_check[i+1:]:
                # Check if multiplication makes sense (no constant columns)
                if df[col1].std() > 0 and df[col2].std() > 0:
                    suggestions.append({
                        'name': f'{col1}_x_{col2}',
                        'formula': f'{col1} * {col2}',
                        'type': 'multiplication',
                        'columns_used': [col1, col2]
                    })
        
        return suggestions
    
    @staticmethod
    def apply_feature_engineering(df: pd.DataFrame, 
                                 suggestions: Dict[str, Any],
                                 apply_list: List[str] = None) -> Tuple[pd.DataFrame, List[str]]:
        """
        Apply suggested feature engineering transformations.
        
        Args:
            df: Input dataframe
            suggestions: Suggestions from analyze_and_suggest
            apply_list: List of transformation names to apply (if None, apply all safe ones)
            
        Returns:
            Tuple of (transformed dataframe, list of new column names)
        """
        df_transformed = df.copy()
        new_columns = []
        
        # Apply derived features
        for suggestion in suggestions.get('derived_features', []):
            try:
                name = suggestion['name']
                cols_used = suggestion['columns_used']
                
                # Check if all required columns exist
                if all(col in df.columns for col in cols_used):
                    if 'FamilySize' in name:
                        df_transformed[name] = df[cols_used].sum(axis=1) + 1
                        new_columns.append(name)
                    elif 'IsAlone' in name and 'FamilySize' in df_transformed.columns:
                        df_transformed[name] = (df_transformed['FamilySize'] == 1).astype(int)
                        new_columns.append(name)
                    elif 'Log_' in name:
                        col = cols_used[0]
                        # Add small constant to avoid log(0)
                        df_transformed[name] = np.log1p(df[col])
                        new_columns.append(name)
            except Exception:
                continue
        
        # Apply transformations for skewed data
        for suggestion in suggestions.get('transformations', []):
            try:
                col = suggestion['column']
                transform = suggestion['suggested_transform']
                
                if col in df.columns:
                    if transform == 'log':
                        new_col = f'{col}_log'
                        df_transformed[new_col] = np.log1p(df[col].clip(lower=0))
                        new_columns.append(new_col)
                    elif transform == 'sqrt':
                        new_col = f'{col}_sqrt'
                        df_transformed[new_col] = np.sqrt(df[col].clip(lower=0))
                        new_columns.append(new_col)
            except Exception:
                continue
        
        return df_transformed, new_columns


class ImbalanceHandler:
    """Handle class imbalance detection and strategies."""
    
    @staticmethod
    def detect_imbalance(y: pd.Series) -> Dict[str, Any]:
        """
        Detect class imbalance in target variable.
        
        Args:
            y: Target variable series
            
        Returns:
            Imbalance analysis and recommendations
        """
        class_counts = y.value_counts()
        total = len(y)
        
        # Calculate imbalance ratio
        max_class = class_counts.max()
        min_class = class_counts.min()
        imbalance_ratio = max_class / min_class if min_class > 0 else float('inf')
        
        # Class distribution
        distribution = {
            str(cls): {
                'count': int(count),
                'percentage': float(count / total * 100)
            }
            for cls, count in class_counts.items()
        }
        
        # Determine severity
        if imbalance_ratio > 10:
            severity = 'severe'
            recommendation = 'SMOTE or undersampling strongly recommended'
        elif imbalance_ratio > 3:
            severity = 'moderate'
            recommendation = 'Class weights or SMOTE recommended'
        elif imbalance_ratio > 1.5:
            severity = 'mild'
            recommendation = 'Class weights may help'
        else:
            severity = 'none'
            recommendation = 'Classes are balanced, no action needed'
        
        # Suggest metrics
        if imbalance_ratio > 1.5:
            suggested_metrics = ['F1-score', 'Precision', 'Recall', 'AUC-ROC']
        else:
            suggested_metrics = ['Accuracy', 'F1-score']
        
        # Suggest strategies
        strategies = []
        if imbalance_ratio > 3:
            strategies.append({
                'name': 'Class Weights',
                'description': 'Assign higher weights to minority class',
                'implementation': 'Use class_weight="balanced" in sklearn models'
            })
        
        if imbalance_ratio > 5:
            strategies.append({
                'name': 'SMOTE',
                'description': 'Synthetic Minority Over-sampling Technique',
                'implementation': 'Use imblearn.over_sampling.SMOTE'
            })
            strategies.append({
                'name': 'Undersampling',
                'description': 'Reduce majority class samples',
                'implementation': 'Use imblearn.under_sampling.RandomUnderSampler'
            })
        
        return {
            'is_imbalanced': imbalance_ratio > 1.5,
            'imbalance_ratio': float(imbalance_ratio),
            'severity': severity,
            'distribution': distribution,
            'recommendation': recommendation,
            'suggested_metrics': suggested_metrics,
            'strategies': strategies,
            'majority_class': str(class_counts.idxmax()),
            'minority_class': str(class_counts.idxmin())
        }
    
    @staticmethod
    def calculate_class_weights(y: np.ndarray) -> Dict[int, float]:
        """
        Calculate balanced class weights.
        
        Args:
            y: Target labels
            
        Returns:
            Dictionary mapping class labels to weights
        """
        classes, counts = np.unique(y, return_counts=True)
        n_samples = len(y)
        n_classes = len(classes)
        
        # Balanced weight formula: n_samples / (n_classes * class_count)
        weights = {
            int(cls): float(n_samples / (n_classes * count))
            for cls, count in zip(classes, counts)
        }
        
        return weights
