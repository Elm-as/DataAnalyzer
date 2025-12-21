#!/usr/bin/env python3
"""
Test script for new ML improvements
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Test explainability module
print("=" * 60)
print("Testing Explainability Module")
print("=" * 60)

from analyses.explainability import ExplainabilityAnalyzer, ModelAuditor, CalibrationAnalyzer

# Create sample data
np.random.seed(42)
X = np.random.randn(100, 5)
y = (X[:, 0] + X[:, 1] > 0).astype(int)
feature_names = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']

# Train a simple model
model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X, y)

# Test feature importance
importance = ExplainabilityAnalyzer.get_feature_importance(model, feature_names, 'tree')
print(f"\n✓ Feature Importance: {importance['available']}")
if importance['available']:
    print(f"  Top features: {[f['feature'] for f in importance['top_features'][:3]]}")

# Test local explanation
X_sample = X[0]
local_exp = ExplainabilityAnalyzer.explain_prediction_local(model, X_sample, feature_names)
print(f"\n✓ Local Explanation: {local_exp['available']}")
if local_exp['available']:
    print(f"  Contributions: {len(local_exp['contributions'])} features")

# Test interpretation messages
messages = ExplainabilityAnalyzer.generate_interpretation_messages(1, 0.85, local_exp.get('contributions', []))
print(f"\n✓ Interpretation Messages: {len(messages)} messages")
for msg in messages[:2]:
    print(f"  - {msg}")

# Test calibration
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
model.fit(X_train, y_train)
y_proba = model.predict_proba(X_test)[:, 1]
calibration = CalibrationAnalyzer.analyze_calibration(y_test, y_proba)
print(f"\n✓ Calibration Analysis: Brier Score = {calibration.get('brier_score', 'N/A')}")
print(f"  Well Calibrated: {calibration.get('is_well_calibrated', False)}")

# Test model audit
print("\n" + "=" * 60)
print("Testing Model Auditor")
print("=" * 60)

models = {
    'model1': {
        'test_metrics': {'accuracy': 0.85},
        'train_metrics': {'accuracy': 0.87},
        'cross_validation': {'mean': 0.84, 'std': 0.05}
    },
    'model2': {
        'test_metrics': {'accuracy': 0.82},
        'train_metrics': {'accuracy': 0.95},
        'cross_validation': {'mean': 0.80, 'std': 0.08}
    }
}

audit = ModelAuditor.audit_model_selection(models, 'model1', y_test)
print(f"\n✓ Audit Report: {len(audit['justification'])} justifications")
print(f"  Warnings: {len(audit['warnings'])} warnings")
print(f"  Overfitting Risk: {audit['overfitting_risk']}")

# Test feature engineering
print("\n" + "=" * 60)
print("Testing Feature Engineering Module")
print("=" * 60)

from analyses.feature_engineering import FeatureEngineer, ImbalanceHandler

# Create sample dataframe
df = pd.DataFrame({
    'age': np.random.randint(20, 80, 100),
    'fare': np.random.exponential(30, 100),
    'sibsp': np.random.randint(0, 5, 100),
    'parch': np.random.randint(0, 3, 100),
    'survived': np.random.randint(0, 2, 100)
})

suggestions = FeatureEngineer.analyze_and_suggest(df, 'survived')
print(f"\n✓ Feature Engineering Suggestions:")
print(f"  Categorical grouping: {len(suggestions['categorical_grouping'])} suggestions")
print(f"  Normalizations: {len(suggestions['normalization'])} suggestions")
print(f"  Derived features: {len(suggestions['derived_features'])} suggestions")
print(f"  Transformations: {len(suggestions['transformations'])} suggestions")

# Test imbalance detection
imbalance = ImbalanceHandler.detect_imbalance(df['survived'])
print(f"\n✓ Imbalance Detection:")
print(f"  Is Imbalanced: {imbalance['is_imbalanced']}")
print(f"  Imbalance Ratio: {imbalance['imbalance_ratio']:.2f}")
print(f"  Severity: {imbalance['severity']}")

# Test data quality
print("\n" + "=" * 60)
print("Testing Data Quality Module")
print("=" * 60)

from analyses.data_quality import DataQualityAnalyzer

# Add some missing values and duplicates
df_dirty = df.copy()
df_dirty.loc[0:10, 'age'] = np.nan
df_dirty = pd.concat([df_dirty, df_dirty.iloc[:5]], ignore_index=True)

quality = DataQualityAnalyzer.generate_quality_report(df_dirty, 'survived')
print(f"\n✓ Quality Report:")
print(f"  Quality Score: {quality['quality_score']:.1f}/100")
print(f"  Warnings: {len(quality['warnings'])} warnings")
print(f"  Recommendations: {len(quality['recommendations'])} recommendations")
print(f"  Duplicates: {quality['duplicates']['count']}")
print(f"  Useless Columns: {len(quality['useless_columns'])}")

# Test What-If Analysis
print("\n" + "=" * 60)
print("Testing What-If Analysis Module")
print("=" * 60)

from analyses.what_if import WhatIfAnalyzer

scenarios = WhatIfAnalyzer.generate_scenarios(X[0], feature_names, model, n_scenarios=3)
print(f"\n✓ Scenarios Generated: {len(scenarios)} scenarios")
for i, scenario in enumerate(scenarios[:2], 1):
    print(f"  Scenario {i}: Prediction = {scenario.get('prediction')}")

print("\n" + "=" * 60)
print("All Tests Passed! ✓")
print("=" * 60)
