import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer, KNNImputer

class DataCleaner:
    def __init__(self, df):
        self.df = df.copy()
        self.report = {
            'original_shape': df.shape,
            'operations': [],
            'warnings': []
        }
        
    def clean(self, config):
        """
        Nettoyage complet des données
        config = {
            'remove_duplicates': True,
            'handle_missing': {
                'method': 'drop' | 'mean' | 'median' | 'mode' | 'knn' | 'forward_fill' | 'backward_fill',
                'threshold': 0.5  # Supprimer les colonnes avec plus de 50% de valeurs manquantes
            },
            'handle_outliers': {
                'method': 'iqr' | 'zscore' | 'remove' | 'cap',
                'columns': ['col1', 'col2'],
                'threshold': 3  # Pour zscore
            },
            'normalize': {
                'method': 'standard' | 'minmax' | 'robust',
                'columns': ['col1', 'col2']
            },
            'encode_categorical': {
                'method': 'label' | 'onehot',
                'columns': ['col1', 'col2']
            },
            'convert_types': {
                'date_columns': ['date_col'],
                'numeric_columns': ['num_col']
            }
        }
        """
        
        # 1. Suppression des doublons
        if config.get('remove_duplicates', False):
            self._remove_duplicates()
        
        # 2. Conversion des types
        if 'convert_types' in config:
            self._convert_types(config['convert_types'])
        
        # 3. Gestion des valeurs manquantes
        if 'handle_missing' in config:
            self._handle_missing_values(config['handle_missing'])
        
        # 4. Gestion des valeurs aberrantes
        if 'handle_outliers' in config:
            self._handle_outliers(config['handle_outliers'])
        
        # 5. Normalisation/Standardisation
        if 'normalize' in config:
            self._normalize_data(config['normalize'])
        
        # 6. Encodage des variables catégorielles
        if 'encode_categorical' in config:
            self._encode_categorical(config['encode_categorical'])
        
        # Rapport final
        self.report['final_shape'] = self.df.shape
        self.report['rows_removed'] = self.report['original_shape'][0] - self.report['final_shape'][0]
        self.report['columns_removed'] = self.report['original_shape'][1] - self.report['final_shape'][1]
        
        return self.df, self.report
    
    def _remove_duplicates(self):
        """Suppression des lignes en double"""
        n_before = len(self.df)
        self.df = self.df.drop_duplicates()
        n_removed = n_before - len(self.df)
        
        self.report['operations'].append({
            'operation': 'remove_duplicates',
            'rows_removed': n_removed,
            'description': f'{n_removed} lignes dupliquées supprimées'
        })
    
    def _convert_types(self, type_config):
        """Conversion des types de colonnes"""
        conversions = []
        
        # Conversion en date
        if 'date_columns' in type_config:
            for col in type_config['date_columns']:
                if col in self.df.columns:
                    try:
                        self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                        conversions.append(f'{col} → datetime')
                    except Exception as e:
                        self.report['warnings'].append(f'Échec conversion date pour {col}: {str(e)}')
        
        # Conversion en numérique
        if 'numeric_columns' in type_config:
            for col in type_config['numeric_columns']:
                if col in self.df.columns:
                    try:
                        self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                        conversions.append(f'{col} → numeric')
                    except Exception as e:
                        self.report['warnings'].append(f'Échec conversion numérique pour {col}: {str(e)}')
        
        if conversions:
            self.report['operations'].append({
                'operation': 'convert_types',
                'conversions': conversions,
                'description': f'{len(conversions)} conversions de types effectuées'
            })
    
    def _handle_missing_values(self, missing_config):
        """Gestion des valeurs manquantes"""
        method = missing_config.get('method', 'drop')
        threshold = missing_config.get('threshold', 0.5)
        
        # Statistiques avant traitement
        missing_before = self.df.isnull().sum().sum()
        
        # Supprimer les colonnes avec trop de valeurs manquantes
        if threshold < 1.0:
            cols_to_drop = []
            for col in self.df.columns:
                missing_ratio = self.df[col].isnull().sum() / len(self.df)
                if missing_ratio > threshold:
                    cols_to_drop.append(col)
            
            if cols_to_drop:
                self.df = self.df.drop(columns=cols_to_drop)
                self.report['operations'].append({
                    'operation': 'drop_high_missing_columns',
                    'columns_dropped': cols_to_drop,
                    'threshold': threshold,
                    'description': f'{len(cols_to_drop)} colonnes supprimées (>{threshold*100}% manquant)'
                })
        
        # Traiter les valeurs manquantes restantes
        if method == 'drop':
            n_before = len(self.df)
            self.df = self.df.dropna()
            n_removed = n_before - len(self.df)
            
            self.report['operations'].append({
                'operation': 'drop_missing_rows',
                'rows_removed': n_removed,
                'description': f'{n_removed} lignes avec valeurs manquantes supprimées'
            })
        
        elif method in ['mean', 'median', 'mode']:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            
            if method == 'mean':
                imputer = SimpleImputer(strategy='mean')
            elif method == 'median':
                imputer = SimpleImputer(strategy='median')
            else:  # mode
                imputer = SimpleImputer(strategy='most_frequent')
            
            if len(numeric_cols) > 0:
                self.df[numeric_cols] = imputer.fit_transform(self.df[numeric_cols])
            
            # Pour les colonnes catégorielles, utiliser le mode
            cat_cols = self.df.select_dtypes(include=['object']).columns
            if len(cat_cols) > 0:
                mode_imputer = SimpleImputer(strategy='most_frequent')
                self.df[cat_cols] = mode_imputer.fit_transform(self.df[cat_cols])
            
            self.report['operations'].append({
                'operation': f'impute_{method}',
                'columns_affected': list(numeric_cols) + list(cat_cols),
                'description': f'Imputation par {method} effectuée'
            })
        
        elif method == 'knn':
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                imputer = KNNImputer(n_neighbors=5)
                self.df[numeric_cols] = imputer.fit_transform(self.df[numeric_cols])
                
                self.report['operations'].append({
                    'operation': 'impute_knn',
                    'columns_affected': list(numeric_cols),
                    'description': 'Imputation KNN (k=5) effectuée'
                })
        
        elif method == 'forward_fill':
            self.df = self.df.fillna(method='ffill')
            self.report['operations'].append({
                'operation': 'forward_fill',
                'description': 'Forward fill appliqué'
            })
        
        elif method == 'backward_fill':
            self.df = self.df.fillna(method='bfill')
            self.report['operations'].append({
                'operation': 'backward_fill',
                'description': 'Backward fill appliqué'
            })
        
        # Statistiques après traitement
        missing_after = self.df.isnull().sum().sum()
        self.report['operations'][-1]['missing_values_handled'] = missing_before - missing_after
    
    def _handle_outliers(self, outlier_config):
        """Gestion des valeurs aberrantes"""
        method = outlier_config.get('method', 'iqr')
        columns = outlier_config.get('columns', [])
        threshold = outlier_config.get('threshold', 3)
        
        if not columns:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        outliers_info = []
        
        for col in columns:
            if col not in self.df.columns:
                continue
            
            n_before = len(self.df)
            
            if method == 'iqr':
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                if outlier_config.get('action', 'remove') == 'remove':
                    self.df = self.df[(self.df[col] >= lower_bound) & (self.df[col] <= upper_bound)]
                elif outlier_config.get('action', 'remove') == 'cap':
                    self.df[col] = self.df[col].clip(lower_bound, upper_bound)
                
                n_outliers = n_before - len(self.df)
                outliers_info.append({
                    'column': col,
                    'method': 'IQR',
                    'bounds': {'lower': float(lower_bound), 'upper': float(upper_bound)},
                    'outliers_detected': n_outliers
                })
            
            elif method == 'zscore':
                z_scores = np.abs((self.df[col] - self.df[col].mean()) / self.df[col].std())
                
                if outlier_config.get('action', 'remove') == 'remove':
                    self.df = self.df[z_scores < threshold]
                
                n_outliers = n_before - len(self.df)
                outliers_info.append({
                    'column': col,
                    'method': 'Z-Score',
                    'threshold': threshold,
                    'outliers_detected': n_outliers
                })
        
        if outliers_info:
            self.report['operations'].append({
                'operation': f'handle_outliers_{method}',
                'outliers_info': outliers_info,
                'total_outliers': sum(info['outliers_detected'] for info in outliers_info),
                'description': f'Valeurs aberrantes traitées par méthode {method}'
            })
    
    def _normalize_data(self, normalize_config):
        """Normalisation/Standardisation des données"""
        method = normalize_config.get('method', 'standard')
        columns = normalize_config.get('columns', [])
        
        if not columns:
            columns = self.df.select_dtypes(include=[np.number]).columns
        
        # Filtrer les colonnes qui existent
        columns = [col for col in columns if col in self.df.columns]
        
        if method == 'standard':
            scaler = StandardScaler()
            scaler_name = 'StandardScaler (mean=0, std=1)'
        elif method == 'minmax':
            scaler = MinMaxScaler()
            scaler_name = 'MinMaxScaler (range 0-1)'
        elif method == 'robust':
            scaler = RobustScaler()
            scaler_name = 'RobustScaler (résistant aux outliers)'
        else:
            return
        
        if len(columns) > 0:
            self.df[columns] = scaler.fit_transform(self.df[columns])
            
            self.report['operations'].append({
                'operation': f'normalize_{method}',
                'columns_normalized': columns,
                'scaler': scaler_name,
                'description': f'Normalisation {method} appliquée à {len(columns)} colonnes'
            })
    
    def _encode_categorical(self, encode_config):
        """Encodage des variables catégorielles"""
        method = encode_config.get('method', 'label')
        columns = encode_config.get('columns', [])
        
        if not columns:
            columns = self.df.select_dtypes(include=['object']).columns
        
        encoding_info = []
        
        for col in columns:
            if col not in self.df.columns:
                continue
            
            if method == 'label':
                le = LabelEncoder()
                self.df[col] = le.fit_transform(self.df[col].astype(str))
                encoding_info.append({
                    'column': col,
                    'method': 'LabelEncoder',
                    'n_categories': len(le.classes_),
                    'categories': le.classes_.tolist()[:10]  # Limiter à 10 pour le rapport
                })
            
            elif method == 'onehot':
                # One-hot encoding
                dummies = pd.get_dummies(self.df[col], prefix=col)
                self.df = pd.concat([self.df.drop(col, axis=1), dummies], axis=1)
                encoding_info.append({
                    'column': col,
                    'method': 'OneHotEncoder',
                    'n_categories': len(dummies.columns),
                    'new_columns': dummies.columns.tolist()[:10]  # Limiter à 10
                })
        
        if encoding_info:
            self.report['operations'].append({
                'operation': f'encode_{method}',
                'encoding_info': encoding_info,
                'description': f'Encodage {method} appliqué à {len(encoding_info)} colonnes'
            })
