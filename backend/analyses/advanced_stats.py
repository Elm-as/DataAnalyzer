import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import chi2_contingency, f_oneway, kruskal, mannwhitneyu, shapiro, normaltest, levene, ttest_ind, ttest_rel
import warnings
warnings.filterwarnings('ignore')

class AdvancedStatsAnalyzer:
    def __init__(self, df):
        self.df = df
        
    def perform_analysis(self, config):
        """
        Statistiques avancées (tests d'hypothèse, ANOVA, etc.)
        config = {
            'tests': ['normality', 'ttest', 'anova', 'kruskal', 'chi_square', 'correlation_test'],
            'ttest': {
                'group_column': 'group',
                'value_column': 'value',
                'paired': False
            },
            'anova': {
                'group_column': 'group',
                'value_column': 'value'
            },
            'chi_square': {
                'var1': 'category1',
                'var2': 'category2'
            },
            'alpha': 0.05
        }
        """
        results = {
            'summary': {},
            'tests': {}
        }
        
        alpha = config.get('alpha', 0.05)
        tests = config.get('tests', [])
        
        # Test de normalité
        if 'normality' in tests:
            results['tests']['normality'] = self._test_normality(config, alpha)
        
        # T-Test
        if 'ttest' in tests and 'ttest' in config:
            results['tests']['ttest'] = self._t_test(config['ttest'], alpha)
        
        # ANOVA
        if 'anova' in tests and 'anova' in config:
            results['tests']['anova'] = self._anova_test(config['anova'], alpha)
        
        # Kruskal-Wallis (alternative non-paramétrique à ANOVA)
        if 'kruskal' in tests and 'kruskal' in config:
            results['tests']['kruskal'] = self._kruskal_test(config['kruskal'], alpha)
        
        # Chi-carré d'indépendance
        if 'chi_square' in tests and 'chi_square' in config:
            results['tests']['chi_square'] = self._chi_square_test(config['chi_square'], alpha)
        
        # Test de corrélation
        if 'correlation_test' in tests:
            results['tests']['correlation'] = self._correlation_tests(config, alpha)
        
        # Test de Levene (homogénéité des variances)
        if 'levene' in tests and 'levene' in config:
            results['tests']['levene'] = self._levene_test(config['levene'], alpha)
        
        # Mann-Whitney U (alternative non-paramétrique au t-test)
        if 'mann_whitney' in tests and 'mann_whitney' in config:
            results['tests']['mann_whitney'] = self._mann_whitney_test(config['mann_whitney'], alpha)
        
        # Résumé
        results['summary'] = self._summarize_tests(results['tests'], alpha)
        
        return results
    
    def _test_normality(self, config, alpha):
        """Tests de normalité (Shapiro-Wilk, D'Agostino)"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        normality_results = []
        
        for col in numeric_cols:
            data = self.df[col].dropna()
            
            if len(data) < 3:
                continue
            
            # Shapiro-Wilk test (recommandé pour n < 5000)
            if len(data) < 5000:
                shapiro_stat, shapiro_p = shapiro(data)
            else:
                shapiro_stat, shapiro_p = None, None
            
            # D'Agostino K² test
            try:
                dagostino_stat, dagostino_p = normaltest(data)
            except:
                dagostino_stat, dagostino_p = None, None
            
            normality_results.append({
                'column': col,
                'n_samples': len(data),
                'shapiro_wilk': {
                    'statistic': float(shapiro_stat) if shapiro_stat else None,
                    'p_value': float(shapiro_p) if shapiro_p else None,
                    'is_normal': shapiro_p > alpha if shapiro_p else None
                } if shapiro_stat else None,
                'dagostino': {
                    'statistic': float(dagostino_stat) if dagostino_stat else None,
                    'p_value': float(dagostino_p) if dagostino_p else None,
                    'is_normal': dagostino_p > alpha if dagostino_p else None
                } if dagostino_stat else None,
                'skewness': float(stats.skew(data)),
                'kurtosis': float(stats.kurtosis(data))
            })
        
        return {
            'test_name': 'Tests de normalité',
            'alpha': alpha,
            'results': normality_results,
            'interpretation': 'p > α : données normalement distribuées; p ≤ α : données non normales'
        }
    
    def _t_test(self, ttest_config, alpha):
        """Test t de Student"""
        group_col = ttest_config['group_column']
        value_col = ttest_config['value_column']
        paired = ttest_config.get('paired', False)
        
        groups = self.df[group_col].unique()
        
        if len(groups) != 2:
            return {'error': f'Le t-test nécessite exactement 2 groupes. Trouvés: {len(groups)}'}
        
        group1_data = self.df[self.df[group_col] == groups[0]][value_col].dropna()
        group2_data = self.df[self.df[group_col] == groups[1]][value_col].dropna()
        
        if paired:
            if len(group1_data) != len(group2_data):
                return {'error': 'Pour un t-test apparié, les groupes doivent avoir la même taille'}
            statistic, p_value = ttest_rel(group1_data, group2_data)
            test_type = 'T-test apparié (paired)'
        else:
            statistic, p_value = ttest_ind(group1_data, group2_data)
            test_type = 'T-test indépendant'
        
        # Effect size (Cohen's d)
        pooled_std = np.sqrt((group1_data.std()**2 + group2_data.std()**2) / 2)
        cohens_d = (group1_data.mean() - group2_data.mean()) / pooled_std if pooled_std != 0 else 0
        
        return {
            'test_name': test_type,
            'groups': {
                'group1': {'name': str(groups[0]), 'mean': float(group1_data.mean()), 'std': float(group1_data.std()), 'n': len(group1_data)},
                'group2': {'name': str(groups[1]), 'mean': float(group2_data.mean()), 'std': float(group2_data.std()), 'n': len(group2_data)}
            },
            'statistic': float(statistic),
            'p_value': float(p_value),
            'alpha': alpha,
            'significant': p_value < alpha,
            'cohens_d': float(cohens_d),
            'effect_size': 'petit' if abs(cohens_d) < 0.5 else 'moyen' if abs(cohens_d) < 0.8 else 'grand',
            'interpretation': f"Différence {'significative' if p_value < alpha else 'non significative'} entre les groupes (p={p_value:.4f})"
        }
    
    def _anova_test(self, anova_config, alpha):
        """ANOVA (Analysis of Variance)"""
        group_col = anova_config['group_column']
        value_col = anova_config['value_column']
        
        groups = self.df[group_col].unique()
        group_data = [self.df[self.df[group_col] == group][value_col].dropna() for group in groups]
        
        # F-statistic et p-value
        statistic, p_value = f_oneway(*group_data)
        
        # Statistiques descriptives par groupe
        group_stats = []
        for i, group in enumerate(groups):
            group_stats.append({
                'group': str(group),
                'n': len(group_data[i]),
                'mean': float(group_data[i].mean()),
                'std': float(group_data[i].std()),
                'min': float(group_data[i].min()),
                'max': float(group_data[i].max())
            })
        
        return {
            'test_name': 'ANOVA (One-way)',
            'n_groups': len(groups),
            'group_stats': group_stats,
            'f_statistic': float(statistic),
            'p_value': float(p_value),
            'alpha': alpha,
            'significant': p_value < alpha,
            'interpretation': f"Différence {'significative' if p_value < alpha else 'non significative'} entre les groupes (p={p_value:.4f})",
            'note': 'ANOVA suppose normalité et homogénéité des variances. Utilisez Kruskal-Wallis si ces conditions ne sont pas respectées.'
        }
    
    def _kruskal_test(self, kruskal_config, alpha):
        """Test de Kruskal-Wallis (alternative non-paramétrique à ANOVA)"""
        group_col = kruskal_config['group_column']
        value_col = kruskal_config['value_column']
        
        groups = self.df[group_col].unique()
        group_data = [self.df[self.df[group_col] == group][value_col].dropna() for group in groups]
        
        statistic, p_value = kruskal(*group_data)
        
        # Statistiques descriptives par groupe
        group_stats = []
        for i, group in enumerate(groups):
            group_stats.append({
                'group': str(group),
                'n': len(group_data[i]),
                'median': float(group_data[i].median()),
                'mean': float(group_data[i].mean()),
                'std': float(group_data[i].std())
            })
        
        return {
            'test_name': 'Kruskal-Wallis',
            'n_groups': len(groups),
            'group_stats': group_stats,
            'h_statistic': float(statistic),
            'p_value': float(p_value),
            'alpha': alpha,
            'significant': p_value < alpha,
            'interpretation': f"Différence {'significative' if p_value < alpha else 'non significative'} entre les groupes (p={p_value:.4f})",
            'note': 'Test non-paramétrique, ne suppose pas la normalité des données'
        }
    
    def _chi_square_test(self, chi_config, alpha):
        """Test du Chi-carré d'indépendance"""
        var1 = chi_config['var1']
        var2 = chi_config['var2']
        
        # Table de contingence
        contingency_table = pd.crosstab(self.df[var1], self.df[var2])
        
        # Test du chi-carré
        chi2, p_value, dof, expected_freq = chi2_contingency(contingency_table)
        
        # Cramér's V (mesure de l'intensité de l'association)
        n = contingency_table.sum().sum()
        min_dim = min(contingency_table.shape[0], contingency_table.shape[1]) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0
        
        return {
            'test_name': 'Test du Chi-carré d\'indépendance',
            'variables': [var1, var2],
            'contingency_table': contingency_table.to_dict(),
            'chi2_statistic': float(chi2),
            'p_value': float(p_value),
            'degrees_of_freedom': int(dof),
            'alpha': alpha,
            'significant': p_value < alpha,
            'cramers_v': float(cramers_v),
            'association_strength': 'faible' if cramers_v < 0.3 else 'moyenne' if cramers_v < 0.5 else 'forte',
            'interpretation': f"Association {'significative' if p_value < alpha else 'non significative'} entre {var1} et {var2} (p={p_value:.4f})"
        }
    
    def _correlation_tests(self, config, alpha):
        """Tests de corrélation (Pearson, Spearman)"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return {'error': 'Nécessite au moins 2 colonnes numériques'}
        
        correlation_results = []
        
        for i in range(len(numeric_cols)):
            for j in range(i+1, len(numeric_cols)):
                col1, col2 = numeric_cols[i], numeric_cols[j]
                
                # Données appariées (sans valeurs manquantes)
                data = self.df[[col1, col2]].dropna()
                
                if len(data) < 3:
                    continue
                
                # Corrélation de Pearson
                pearson_r, pearson_p = stats.pearsonr(data[col1], data[col2])
                
                # Corrélation de Spearman (rang)
                spearman_r, spearman_p = stats.spearmanr(data[col1], data[col2])
                
                correlation_results.append({
                    'variable1': col1,
                    'variable2': col2,
                    'n_samples': len(data),
                    'pearson': {
                        'correlation': float(pearson_r),
                        'p_value': float(pearson_p),
                        'significant': pearson_p < alpha
                    },
                    'spearman': {
                        'correlation': float(spearman_r),
                        'p_value': float(spearman_p),
                        'significant': spearman_p < alpha
                    },
                    'interpretation': f"Corrélation {'significative' if pearson_p < alpha else 'non significative'} (Pearson r={pearson_r:.3f}, p={pearson_p:.4f})"
                })
        
        return {
            'test_name': 'Tests de corrélation',
            'alpha': alpha,
            'results': correlation_results[:20],  # Limiter à 20 paires
            'total_pairs_tested': len(correlation_results)
        }
    
    def _levene_test(self, levene_config, alpha):
        """Test de Levene (homogénéité des variances)"""
        group_col = levene_config['group_column']
        value_col = levene_config['value_column']
        
        groups = self.df[group_col].unique()
        group_data = [self.df[self.df[group_col] == group][value_col].dropna() for group in groups]
        
        statistic, p_value = levene(*group_data)
        
        return {
            'test_name': 'Test de Levene',
            'n_groups': len(groups),
            'statistic': float(statistic),
            'p_value': float(p_value),
            'alpha': alpha,
            'homogeneous_variances': p_value > alpha,
            'interpretation': f"Variances {'homogènes' if p_value > alpha else 'hétérogènes'} (p={p_value:.4f})"
        }
    
    def _mann_whitney_test(self, mw_config, alpha):
        """Test de Mann-Whitney U (alternative non-paramétrique au t-test)"""
        group_col = mw_config['group_column']
        value_col = mw_config['value_column']
        
        groups = self.df[group_col].unique()
        
        if len(groups) != 2:
            return {'error': f'Mann-Whitney nécessite 2 groupes. Trouvés: {len(groups)}'}
        
        group1_data = self.df[self.df[group_col] == groups[0]][value_col].dropna()
        group2_data = self.df[self.df[group_col] == groups[1]][value_col].dropna()
        
        statistic, p_value = mannwhitneyu(group1_data, group2_data, alternative='two-sided')
        
        return {
            'test_name': 'Mann-Whitney U',
            'groups': {
                'group1': {'name': str(groups[0]), 'median': float(group1_data.median()), 'n': len(group1_data)},
                'group2': {'name': str(groups[1]), 'median': float(group2_data.median()), 'n': len(group2_data)}
            },
            'u_statistic': float(statistic),
            'p_value': float(p_value),
            'alpha': alpha,
            'significant': p_value < alpha,
            'interpretation': f"Différence {'significative' if p_value < alpha else 'non significative'} entre les groupes (p={p_value:.4f})",
            'note': 'Test non-paramétrique, alternative au t-test'
        }
    
    def _summarize_tests(self, tests, alpha):
        """Résumé de tous les tests effectués"""
        total_tests = len(tests)
        significant_tests = 0
        
        for test_name, test_result in tests.items():
            if isinstance(test_result, dict):
                if test_result.get('significant') == True:
                    significant_tests += 1
                elif 'results' in test_result:  # Pour les tests multiples
                    if isinstance(test_result['results'], list):
                        for result in test_result['results']:
                            if isinstance(result, dict) and result.get('shapiro_wilk', {}).get('is_normal') == False:
                                significant_tests += 1
        
        return {
            'total_tests': total_tests,
            'significant_results': significant_tests,
            'alpha_level': alpha,
            'tests_performed': list(tests.keys())
        }
