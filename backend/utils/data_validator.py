"""
Module de validation et nettoyage des données pour les analyses
Fournit des fonctions robustes pour préparer les données avant analyse
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, List, Any


class DataValidator:
    """Valide la qualité des données avant analyse"""

    @staticmethod
    def validate(df: pd.DataFrame, columns: List[str] = None) -> Dict[str, Any]:
        """
        Analyse complète de la qualité des données
        Retourne un rapport détaillé par colonne
        """
        report = {
            'isValid': True,
            'quality': {
                'completeness': 0,
                'nullPercentage': 0,
                'duplicateRows': 0,
            },
            'columnAnalysis': {},
            'issues': [],
            'warnings': [],
            'suggestions': [],
            'problematicColumns': [],
        }

        if df.empty:
            report['isValid'] = False
            report['issues'].append('DataFrame vide')
            return report

        # Analyser chaque colonne
        cols_to_analyze = columns if columns else df.columns.tolist()

        for col in cols_to_analyze:
            if col not in df.columns:
                continue
                
            values = df[col]
            null_count = values.isna().sum()
            null_pct = (null_count / len(df)) * 100
            unique_count = values.nunique()
            
            # Détecter le type
            dtype = str(df[col].dtype)
            if 'int' in dtype or 'float' in dtype:
                col_type = 'number'
            elif 'object' in dtype:
                col_type = 'string'
            elif 'datetime' in dtype:
                col_type = 'date'
            else:
                col_type = 'unknown'
            
            # Calculer la variance (pour numériques)
            variance = 0
            if col_type == 'number':
                numeric_values = values.dropna()
                if len(numeric_values) > 0:
                    variance = float(numeric_values.std())
            
            # Identifier les problèmes
            issue = None
            if null_pct == 100:
                issue = 'Colonne complètement vide'
                report['problematicColumns'].append(col)
            elif null_pct >= 70:
                issue = f'{null_pct:.1f}% de valeurs manquantes'
                report['problematicColumns'].append(col)
            elif null_pct >= 50:
                issue = f'{null_pct:.1f}% de valeurs manquantes'
                report['problematicColumns'].append(col)
            
            if variance == 0 and unique_count > 1 and col_type == 'number':
                issue = 'Pas de variance numérique'
                if col not in report['problematicColumns']:
                    report['problematicColumns'].append(col)
            
            report['columnAnalysis'][col] = {
                'nullCount': int(null_count),
                'nullPercentage': float(null_pct),
                'uniqueValues': int(unique_count),
                'type': col_type,
                'variance': float(variance),
                'issue': issue
            }

        # Calculer les métriques globales
        total_values = sum(len(df) - v['nullCount'] for v in report['columnAnalysis'].values())
        total_possible = len(cols_to_analyze) * len(df)
        
        report['quality']['completeness'] = (total_values / total_possible) * 100 if total_possible > 0 else 0
        report['quality']['nullPercentage'] = 100 - report['quality']['completeness']
        
        # Détecter les doublons
        json_strings = df.astype(str).apply(lambda x: ''.join(x), axis=1)
        report['quality']['duplicateRows'] = len(df) - len(df.drop_duplicates())

        # Générer les alertes
        if report['quality']['nullPercentage'] > 50:
            report['isValid'] = False
            report['issues'].append(f"Données incomplètes : {report['quality']['nullPercentage']:.1f}% N/A")
        elif report['quality']['nullPercentage'] > 30:
            report['warnings'].append(f"Données partiellement incomplètes : {report['quality']['nullPercentage']:.1f}% N/A")

        if report['quality']['duplicateRows'] > 0:
            report['warnings'].append(f"{report['quality']['duplicateRows']} lignes dupliquées détectées")

        if len(report['problematicColumns']) > 0:
            report['warnings'].append(f"{len(report['problematicColumns'])} colonnes problématiques")
            report['suggestions'].append(
                f"Envisager de supprimer ou nettoyer: {', '.join(report['problematicColumns'][:5])}"
            )

        if report['quality']['nullPercentage'] > 20:
            report['suggestions'].append('Utiliser "Nettoyage Automatique" avant analyse')

        if report['quality']['completeness'] >= 80:
            report['suggestions'].append('Qualité des données suffisante pour analyse')

        return report

    @staticmethod
    def validate_for_analysis(
        df: pd.DataFrame,
        config: Dict[str, Any],
        analysis_type: str = 'general'
    ) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Valide les données pour une analyse spécifique
        
        Args:
            df: DataFrame pandas
            config: Configuration de l'analyse
            analysis_type: Type d'analyse ('regression', 'classification', etc.)
        
        Returns:
            (is_valid, issues_dict, suggestions)
        """
        issues = {}
        suggestions = []
        is_valid = True

        # Vérification basique
        if df.empty:
            return False, {'error': 'DataFrame vide'}, ['Charger un fichier de données']

        if len(df) < 10:
            issues['rows'] = f'Seulement {len(df)} lignes (minimum recommandé: 20)'
            is_valid = False
            suggestions.append('Charger plus de données')

        # Vérifications spécifiques par type d'analyse
        if analysis_type in ['regression', 'classification']:
            if 'target' not in config:
                issues['target'] = 'Colonne cible non spécifiée'
                is_valid = False
            else:
                target = config['target']
                if target not in df.columns:
                    issues['target'] = f'Colonne cible "{target}" non trouvée'
                    is_valid = False
                else:
                    # Vérifier que la cible n'est pas vide
                    target_nulls = df[target].isna().sum()
                    target_null_pct = (target_nulls / len(df)) * 100
                    
                    if target_null_pct > 50:
                        issues['target'] = f'Cible {target_null_pct:.1f}% vide'
                        is_valid = False
                        suggestions.append(
                            f'Supprimer les {target_nulls} lignes où la cible est vide'
                        )
                    elif target_null_pct > 20:
                        suggestions.append(
                            f'La cible est {target_null_pct:.1f}% vide. Envisager le '
                            f'nettoyage automatique'
                        )

        # Vérifier les features
        if 'features' in config:
            features = config['features']
            missing_features = [f for f in features if f not in df.columns]
            
            if missing_features:
                issues['features'] = f'Features manquantes: {missing_features}'
                is_valid = False
            else:
                # Vérifier la qualité des features
                null_pcts = {}
                for feat in features:
                    null_pct = (df[feat].isna().sum() / len(df)) * 100
                    null_pcts[feat] = null_pct
                    
                    if null_pct > 80:
                        issues[f'feature_{feat}'] = f'{feat} est {null_pct:.1f}% vide'
                        is_valid = False

                # Avertissement sur features partiellement vides
                high_null_features = [f for f, pct in null_pcts.items() if 30 < pct <= 80]
                if high_null_features:
                    suggestions.append(
                        f'Features partiellement vides ({", ".join(high_null_features)}). '
                        f'Utiliser "Nettoyage Automatique"'
                    )

        return is_valid, issues, suggestions

    @staticmethod
    def get_data_quality_report(df: pd.DataFrame) -> Dict[str, Any]:
        """Génère un rapport de qualité des données"""
        
        report = {
            'total_cells': df.size,
            'null_cells': df.isna().sum().sum(),
            'null_percentage': (df.isna().sum().sum() / df.size) * 100,
            'duplicate_rows': len(df) - len(df.drop_duplicates()),
            'columns': {},
        }

        for col in df.columns:
            null_count = df[col].isna().sum()
            null_pct = (null_count / len(df)) * 100
            unique_count = df[col].nunique()
            
            report['columns'][col] = {
                'type': str(df[col].dtype),
                'null_count': int(null_count),
                'null_percentage': float(null_pct),
                'unique_values': int(unique_count),
                'missing_threshold_exceeded': null_pct > 50,
            }

        return report


class BooleanDetector:
    """Détecte et convertit automatiquement les colonnes booléennes"""
    
    @staticmethod
    def detect_boolean_columns(df: pd.DataFrame) -> Dict[str, bool]:
        """
        Détecte les colonnes qui sont réellement booléennes (0/1, True/False)
        même si elles sont stockées comme numériques
        
        Returns:
            Dict avec 'column_name': True/False
        """
        boolean_cols = {}
        
        for col in df.columns:
            values = df[col].dropna()
            
            if len(values) == 0:
                continue
            
            # Vérifier si tous les non-NaN sont 0, 1, True ou False
            is_boolean = True
            for val in values:
                if not (val in [0, 1, True, False, '0', '1', 'true', 'false', 'True', 'False']):
                    is_boolean = False
                    break
            
            # Ou vérifier si valeurs uniques sont seulement 2 et numériques 0/1
            unique_vals = set(values.dropna())
            if is_boolean or unique_vals <= {0, 1, 0.0, 1.0}:
                boolean_cols[col] = True
            else:
                boolean_cols[col] = False
        
        return boolean_cols
    
    @staticmethod
    def convert_to_boolean(df: pd.DataFrame, column: str) -> pd.Series:
        """
        Convertit une colonne en booléen
        Gère 0/1, True/False, Oui/Non, Yes/No
        """
        def convert_value(val):
            if pd.isna(val):
                return np.nan
            
            # Convertir en string pour comparaison
            str_val = str(val).strip().lower()
            
            if str_val in ['1', 'true', 'yes', 'oui']:
                return True
            elif str_val in ['0', 'false', 'no', 'non']:
                return False
            elif val in [1, 1.0, True]:
                return True
            elif val in [0, 0.0, False]:
                return False
            else:
                return np.nan
        
        return df[column].apply(convert_value)
    
    @staticmethod
    def auto_convert_booleans(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, bool]]:
        """
        Détecte et convertit automatiquement toutes les colonnes booléennes
        
        Returns:
            (DataFrame modifié, Dict des colonnes converties)
        """
        df_copy = df.copy()
        boolean_cols = BooleanDetector.detect_boolean_columns(df_copy)
        converted = {}
        
        for col, is_bool in boolean_cols.items():
            if is_bool:
                df_copy[col] = BooleanDetector.convert_to_boolean(df_copy, col)
                converted[col] = True
        
        return df_copy, converted


class DataCleaner:
    """Nettoie les données automatiquement ou sur demande"""

    @staticmethod
    def auto_clean(
        df: pd.DataFrame,
        remove_high_null_cols: bool = True,
        remove_duplicates: bool = True,
        null_threshold: float = 0.8
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Nettoie les données automatiquement
        
        Args:
            df: DataFrame à nettoyer
            remove_high_null_cols: Supprimer colonnes >80% N/A
            remove_duplicates: Supprimer les lignes dupliquées
            null_threshold: Seuil (0-1) pour supprimer colonnes
        
        Returns:
            (df_cleaned, report)
        """
        df_clean = df.copy()
        report = {
            'original_shape': df.shape,
            'operations': [],
            'warnings': [],
        }

        # 1. Supprimer les colonnes 100% vides
        empty_cols = [col for col in df_clean.columns if df_clean[col].isna().all()]
        if empty_cols:
            df_clean = df_clean.drop(columns=empty_cols)
            report['operations'].append(
                f"Supprimé {len(empty_cols)} colonnes vides: {', '.join(empty_cols)}"
            )

        # 2. Supprimer les colonnes avec trop de N/A
        if remove_high_null_cols:
            high_null_cols = [
                col for col in df_clean.columns
                if (df_clean[col].isna().sum() / len(df_clean)) > null_threshold
            ]
            if high_null_cols:
                df_clean = df_clean.drop(columns=high_null_cols)
                report['operations'].append(
                    f"Supprimé {len(high_null_cols)} colonnes très vides " +
                    f"(>{null_threshold*100:.0f}% N/A)"
                )

        # 3. Supprimer les doublons
        if remove_duplicates:
            initial_rows = len(df_clean)
            df_clean = df_clean.drop_duplicates()
            removed = initial_rows - len(df_clean)
            if removed > 0:
                report['operations'].append(f"Supprimé {removed} lignes dupliquées")

        # 4. Supprimer les colonnes d'index/ID typiques
        index_cols = [col for col in df_clean.columns 
                     if col.lower() in ['index', 'id', 'row', 'num', 'n°', 'rownum']
                     and df_clean[col].nunique() == len(df_clean)]
        if index_cols:
            df_clean = df_clean.drop(columns=index_cols)
            report['operations'].append(
                f"Supprimé {len(index_cols)} colonnes d'index: {', '.join(index_cols)}"
            )

        report['final_shape'] = df_clean.shape
        report['removed_rows'] = df.shape[0] - df_clean.shape[0]
        report['removed_cols'] = df.shape[1] - df_clean.shape[1]

        return df_clean, report

    @staticmethod
    def handle_missing_values(
        df: pd.DataFrame,
        strategy: str = 'drop',
        threshold: float = 0.5
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Traite les valeurs manquantes
        
        Args:
            df: DataFrame
            strategy: 'drop' (supprimer lignes), 'mean' (moyenne), 'median' (médiane), 'forward_fill'
            threshold: Seuil de lignes complètes à garder
        
        Returns:
            (df_cleaned, report)
        """
        df_clean = df.copy()
        report = {'strategy': strategy}

        if strategy == 'drop':
            # Supprimer les lignes avec au moins une valeur manquante
            initial_rows = len(df_clean)
            df_clean = df_clean.dropna()
            report['rows_removed'] = initial_rows - len(df_clean)
            report['message'] = f"Supprimé {report['rows_removed']} lignes incomplètes"

        elif strategy in ['mean', 'median']:
            # Pour les colonnes numériques
            numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if df_clean[col].isna().any():
                    value = df_clean[col].mean() if strategy == 'mean' else df_clean[col].median()
                    df_clean[col] = df_clean[col].fillna(value)
            
            report['columns_filled'] = list(numeric_cols)
            report['message'] = f"Colonnes numériques remplies avec {strategy}"

        elif strategy == 'forward_fill':
            df_clean = df_clean.fillna(method='ffill')
            report['message'] = "Utilisation forward fill pour les N/A"

        return df_clean, report


class FeatureValidator:
    """Valide les features pour des analyses spécifiques"""

    @staticmethod
    def validate_regression_features(
        X: pd.DataFrame,
        y: pd.Series,
        min_samples: int = 20
    ) -> Tuple[bool, List[str]]:
        """
        Valide les features pour la régression
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []

        # Vérifier le nombre d'échantillons
        if len(X) < min_samples:
            issues.append(
                f"Seulement {len(X)} échantillons (minimum: {min_samples})"
            )

        # Vérifier que X n'est pas vide
        if X.empty or y.empty:
            issues.append("X ou y est vide")
            return False, issues

        # Vérifier les NaN
        X_nulls = X.isna().sum().sum()
        y_nulls = y.isna().sum()
        
        if y_nulls / len(y) > 0.5:
            issues.append(f"Target y est {(y_nulls/len(y))*100:.1f}% vide")

        if X_nulls > 0:
            issues.append(f"X contient {X_nulls} valeurs NaN")

        # Vérifier la variance des features
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        zero_variance_cols = [col for col in numeric_cols if X[col].std() == 0]
        
        if zero_variance_cols:
            issues.append(
                f"Colonnes sans variance: {', '.join(zero_variance_cols)}"
            )

        # Vérifier que y a de la variance
        if y.std() == 0:
            issues.append("La variable cible n'a pas de variance")

        return len(issues) == 0, issues

    @staticmethod
    def validate_classification_features(
        X: pd.DataFrame,
        y: pd.Series,
        min_samples_per_class: int = 5
    ) -> Tuple[bool, List[str]]:
        """
        Valide les features pour la classification
        """
        issues = []

        # Vérifier le nombre d'échantillons par classe
        class_counts = y.value_counts()
        
        for cls, count in class_counts.items():
            if count < min_samples_per_class:
                issues.append(
                    f"Classe '{cls}' a {count} échantillons "
                    f"(minimum: {min_samples_per_class})"
                )

        # Vérifier l'équilibre des classes (avertissement)
        if len(class_counts) > 1:
            max_class = class_counts.max()
            min_class = class_counts.min()
            imbalance_ratio = max_class / min_class
            
            if imbalance_ratio > 10:
                issues.append(
                    f"Classes très déséquilibrées (ratio {imbalance_ratio:.1f}:1)"
                )

        # Vérifications communes avec régression
        if X.empty or y.empty:
            issues.append("X ou y est vide")

        if y.isna().sum() / len(y) > 0.5:
            issues.append(f"Target y est {(y.isna().sum()/len(y))*100:.1f}% vide")

        return len(issues) == 0, issues
