"""
Comprehensive data quality assessment before modeling.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple


class DataQualityAnalyzer:
    """Analyze data quality before modeling."""
    
    @staticmethod
    def generate_quality_report(df: pd.DataFrame, target_col: str = None) -> Dict[str, Any]:
        """
        Generate comprehensive data quality report.
        
        Args:
            df: Input dataframe
            target_col: Target column name (optional)
            
        Returns:
            Detailed quality report with warnings and recommendations
        """
        report = {
            'summary': {},
            'missing_values': {},
            'duplicates': {},
            'data_types': {},
            'potential_leaks': [],
            'useless_columns': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Basic summary
        report['summary'] = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage_mb': float(df.memory_usage(deep=True).sum() / 1024**2)
        }
        
        # Missing values analysis
        missing_analysis = DataQualityAnalyzer._analyze_missing_values(df)
        report['missing_values'] = missing_analysis
        
        if missing_analysis['critical_columns']:
            report['warnings'].append(
                f"{len(missing_analysis['critical_columns'])} columns have >50% missing values"
            )
            report['recommendations'].append(
                "Consider dropping columns with excessive missing values or using advanced imputation"
            )
        
        # Duplicates
        duplicates = DataQualityAnalyzer._analyze_duplicates(df)
        report['duplicates'] = duplicates
        
        if duplicates['count'] > 0:
            report['warnings'].append(
                f"{duplicates['count']} duplicate rows found ({duplicates['percentage']:.1f}%)"
            )
            report['recommendations'].append("Remove duplicate rows before modeling")
        
        # Useless columns
        useless = DataQualityAnalyzer._detect_useless_columns(df, target_col)
        report['useless_columns'] = useless
        
        if useless:
            report['warnings'].append(
                f"{len(useless)} potentially useless columns detected"
            )
            report['recommendations'].append(
                f"Consider removing: {', '.join([col['column'] for col in useless[:5]])}"
            )
        
        # Data leakage detection
        if target_col:
            leaks = DataQualityAnalyzer._detect_potential_leaks(df, target_col)
            report['potential_leaks'] = leaks
            
            if leaks:
                report['warnings'].append(
                    f"{len(leaks)} columns may cause data leakage"
                )
                report['recommendations'].append(
                    "Review high-correlation columns for potential data leakage"
                )
        
        # Data type issues
        type_issues = DataQualityAnalyzer._analyze_data_types(df)
        report['data_types'] = type_issues
        
        if type_issues['needs_conversion']:
            report['recommendations'].append(
                "Some columns may need type conversion for optimal modeling"
            )
        
        # Overall quality score
        quality_score = DataQualityAnalyzer._calculate_quality_score(report)
        report['quality_score'] = quality_score
        
        # Overall assessment
        if quality_score >= 80:
            report['overall_assessment'] = 'Good - Data is ready for modeling'
        elif quality_score >= 60:
            report['overall_assessment'] = 'Fair - Some cleaning recommended'
        else:
            report['overall_assessment'] = 'Poor - Significant cleaning required'
        
        return report
    
    @staticmethod
    def _analyze_missing_values(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze missing values in dataset."""
        missing_stats = []
        total_rows = len(df)
        
        for col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                missing_pct = (missing_count / total_rows) * 100
                missing_stats.append({
                    'column': col,
                    'missing_count': int(missing_count),
                    'missing_percentage': float(missing_pct),
                    'severity': 'critical' if missing_pct > 50 else 'high' if missing_pct > 30 else 'moderate'
                })
        
        # Sort by percentage
        missing_stats.sort(key=lambda x: x['missing_percentage'], reverse=True)
        
        return {
            'columns_with_missing': len(missing_stats),
            'total_missing_cells': int(df.isna().sum().sum()),
            'critical_columns': [m for m in missing_stats if m['severity'] == 'critical'],
            'details': missing_stats
        }
    
    @staticmethod
    def _analyze_duplicates(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze duplicate rows."""
        duplicate_mask = df.duplicated()
        duplicate_count = duplicate_mask.sum()
        
        return {
            'count': int(duplicate_count),
            'percentage': float((duplicate_count / len(df)) * 100) if len(df) > 0 else 0,
            'indices': df[duplicate_mask].index.tolist()[:10]  # First 10 indices
        }
    
    @staticmethod
    def _detect_useless_columns(df: pd.DataFrame, target_col: str = None) -> List[Dict[str, Any]]:
        """Detect columns that are likely useless for modeling."""
        useless = []
        
        for col in df.columns:
            if col == target_col:
                continue
            
            # Completely empty columns
            if df[col].isna().all():
                useless.append({
                    'column': col,
                    'reason': '100% missing values',
                    'action': 'drop'
                })
                continue
            
            # Single unique value (zero variance)
            if df[col].nunique() == 1:
                useless.append({
                    'column': col,
                    'reason': 'Zero variance (single unique value)',
                    'action': 'drop'
                })
                continue
            
            # Likely ID columns (many unique values, numeric, sequential)
            if df[col].dtype in [np.int64, np.float64]:
                unique_ratio = df[col].nunique() / len(df)
                if unique_ratio > 0.95:
                    useless.append({
                        'column': col,
                        'reason': f'Likely ID column ({unique_ratio*100:.1f}% unique values)',
                        'action': 'review'
                    })
            
            # Columns with very low variance
            if df[col].dtype in [np.int64, np.float64]:
                non_null = df[col].dropna()
                if len(non_null) > 0:
                    std = non_null.std()
                    if std < 1e-10:
                        useless.append({
                            'column': col,
                            'reason': 'Nearly zero variance',
                            'action': 'drop'
                        })
        
        return useless
    
    @staticmethod
    def _detect_potential_leaks(df: pd.DataFrame, target_col: str) -> List[Dict[str, Any]]:
        """Detect columns that might cause data leakage."""
        leaks = []
        
        if target_col not in df.columns:
            return leaks
        
        # Only check numeric columns for correlation
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if target_col in numeric_cols:
            target_data = df[target_col]
            
            for col in numeric_cols:
                if col == target_col:
                    continue
                
                # Calculate correlation
                try:
                    corr = df[col].corr(target_data)
                    if abs(corr) > 0.95:
                        leaks.append({
                            'column': col,
                            'correlation': float(corr),
                            'reason': 'Extremely high correlation with target',
                            'severity': 'high'
                        })
                    elif abs(corr) > 0.9:
                        leaks.append({
                            'column': col,
                            'correlation': float(corr),
                            'reason': 'Very high correlation with target',
                            'severity': 'moderate'
                        })
                except Exception:
                    continue
        
        # Check for columns with names suggesting leakage
        leak_keywords = ['id', 'uuid', 'key', 'index', 'row', 'result', 'outcome', 'final']
        for col in df.columns:
            if col == target_col:
                continue
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in leak_keywords):
                if col not in [leak['column'] for leak in leaks]:
                    leaks.append({
                        'column': col,
                        'reason': f'Column name suggests potential leakage',
                        'severity': 'low'
                    })
        
        return leaks
    
    @staticmethod
    def _analyze_data_types(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data types and suggest conversions."""
        type_summary = {
            'numeric': 0,
            'categorical': 0,
            'datetime': 0,
            'text': 0,
            'needs_conversion': []
        }
        
        for col in df.columns:
            dtype = df[col].dtype
            
            if dtype in [np.int64, np.float64]:
                type_summary['numeric'] += 1
                
                # Check if numeric is actually categorical
                unique_count = df[col].nunique()
                if unique_count < 10 and unique_count < len(df) * 0.05:
                    type_summary['needs_conversion'].append({
                        'column': col,
                        'current_type': 'numeric',
                        'suggested_type': 'categorical',
                        'reason': f'Only {unique_count} unique values'
                    })
            
            elif dtype == 'object':
                # Check if it's datetime
                try:
                    pd.to_datetime(df[col].dropna().head(100), errors='raise')
                    type_summary['needs_conversion'].append({
                        'column': col,
                        'current_type': 'object',
                        'suggested_type': 'datetime',
                        'reason': 'Values appear to be dates'
                    })
                    type_summary['datetime'] += 1
                except Exception:
                    # Check if it's categorical or text
                    unique_ratio = df[col].nunique() / len(df)
                    if unique_ratio < 0.05:
                        type_summary['categorical'] += 1
                    else:
                        type_summary['text'] += 1
            
            elif np.issubdtype(dtype, np.datetime64):
                type_summary['datetime'] += 1
        
        return type_summary
    
    @staticmethod
    def _calculate_quality_score(report: Dict[str, Any]) -> float:
        """Calculate overall data quality score (0-100)."""
        score = 100.0
        
        # Deduct for missing values
        missing_pct = 0
        if report['missing_values']['columns_with_missing'] > 0:
            total_cells = report['summary']['total_rows'] * report['summary']['total_columns']
            missing_cells = report['missing_values']['total_missing_cells']
            missing_pct = (missing_cells / total_cells) * 100 if total_cells > 0 else 0
            score -= min(missing_pct, 30)
        
        # Deduct for duplicates
        dup_pct = report['duplicates']['percentage']
        score -= min(dup_pct, 20)
        
        # Deduct for useless columns
        useless_ratio = len(report['useless_columns']) / max(report['summary']['total_columns'], 1)
        score -= min(useless_ratio * 20, 15)
        
        # Deduct for potential leaks
        score -= min(len(report['potential_leaks']) * 5, 15)
        
        return max(0.0, score)


class AnalysisJournal:
    """Track and log analysis sessions for reproducibility."""
    
    @staticmethod
    def create_entry(dataset_info: Dict[str, Any], config: Dict[str, Any], 
                    results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an analysis journal entry.
        
        Args:
            dataset_info: Information about the dataset
            config: Analysis configuration
            results: Analysis results
            
        Returns:
            Journal entry dictionary
        """
        from datetime import datetime
        
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'dataset': {
                'name': dataset_info.get('name', 'unknown'),
                'rows': dataset_info.get('rows', 0),
                'columns': dataset_info.get('columns', 0),
                'features': dataset_info.get('features', []),
                'target': dataset_info.get('target', None)
            },
            'configuration': {
                'analysis_type': config.get('type', 'unknown'),
                'methods': config.get('methods', []),
                'test_size': config.get('test_size', 0.2),
                'cv_folds': config.get('cv_folds', 5),
                'parameters': {k: v for k, v in config.items() 
                             if k not in ['type', 'methods', 'test_size', 'cv_folds', 'features', 'target', 'data']}
            },
            'results': {
                'best_model': results.get('best_model', None),
                'best_score': results.get('best_score', None),
                'all_models': list(results.get('models', {}).keys()) if 'models' in results else []
            }
        }
        
        return entry
    
    @staticmethod
    def format_for_export(entry: Dict[str, Any]) -> str:
        """Format journal entry for export/display."""
        lines = [
            "=" * 60,
            f"Analysis Session: {entry['timestamp']}",
            "=" * 60,
            "",
            "Dataset Information:",
            f"  Name: {entry['dataset']['name']}",
            f"  Rows: {entry['dataset']['rows']}",
            f"  Columns: {entry['dataset']['columns']}",
            f"  Target: {entry['dataset']['target']}",
            f"  Features: {', '.join(entry['dataset']['features'][:5])}{'...' if len(entry['dataset']['features']) > 5 else ''}",
            "",
            "Configuration:",
            f"  Analysis Type: {entry['configuration']['analysis_type']}",
            f"  Methods: {', '.join(entry['configuration']['methods'])}",
            f"  Test Size: {entry['configuration']['test_size']}",
            f"  CV Folds: {entry['configuration']['cv_folds']}",
            "",
            "Results:",
            f"  Best Model: {entry['results']['best_model']}",
            f"  Best Score: {entry['results']['best_score']}",
            f"  Models Evaluated: {', '.join(entry['results']['all_models'])}",
            "=" * 60
        ]
        
        return "\n".join(lines)
