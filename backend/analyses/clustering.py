import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from sklearn.decomposition import PCA

class ClusteringAnalyzer:
    def __init__(self, df):
        self.df = df
        
    def perform_analysis(self, config):
        """
        Clustering avancé (K-Means, DBSCAN, Hierarchical, GMM)
        config = {
            'features': ['col1', 'col2', ...],
            'methods': ['kmeans', 'dbscan', 'hierarchical', 'gmm'],
            'n_clusters': 3,  # Pour K-Means, Hierarchical, GMM
            'eps': 0.5,  # Pour DBSCAN
            'min_samples': 5,  # Pour DBSCAN
            'linkage': 'ward',  # Pour Hierarchical
            'find_optimal_k': True  # Recherche automatique du nombre optimal de clusters
        }
        """
        results = {
            'summary': {},
            'models': {}
        }
        
        # Préparation des données
        X = self.df[config['features']].fillna(self.df[config['features']].mean())
        
        # Standardisation (important pour le clustering)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Recherche du nombre optimal de clusters
        if config.get('find_optimal_k', False):
            results['optimal_k'] = self._find_optimal_k(X_scaled, max_k=10)
        
        methods = config.get('methods', ['kmeans'])
        
        # K-Means
        if 'kmeans' in methods:
            results['models']['kmeans'] = self._kmeans_clustering(
                X_scaled, config
            )
        
        # DBSCAN
        if 'dbscan' in methods:
            results['models']['dbscan'] = self._dbscan_clustering(
                X_scaled, config
            )
        
        # Hierarchical Clustering
        if 'hierarchical' in methods:
            results['models']['hierarchical'] = self._hierarchical_clustering(
                X_scaled, config
            )
        
        # Gaussian Mixture Model
        if 'gmm' in methods:
            results['models']['gmm'] = self._gmm_clustering(
                X_scaled, config
            )
        
        # Visualisation PCA (réduction à 2D pour visualisation)
        results['visualization'] = self._pca_visualization(X_scaled, results['models'])
        
        # Comparaison des modèles
        results['summary'] = self._compare_clustering_models(results['models'])
        
        return results
    
    def _find_optimal_k(self, X, max_k=10):
        """Méthode du coude (Elbow Method) pour trouver le k optimal"""
        inertias = []
        silhouette_scores = []
        k_range = range(2, min(max_k + 1, len(X)))
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)
            
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(X, labels))
        
        # Trouver le meilleur k (silhouette score max)
        best_k_idx = np.argmax(silhouette_scores)
        best_k = list(k_range)[best_k_idx]
        
        return {
            'k_range': list(k_range),
            'inertias': inertias,
            'silhouette_scores': silhouette_scores,
            'recommended_k': int(best_k),
            'best_silhouette': float(silhouette_scores[best_k_idx])
        }
    
    def _kmeans_clustering(self, X, config):
        """K-Means Clustering"""
        n_clusters = config.get('n_clusters', 3)
        
        model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = model.fit_predict(X)
        
        # Métriques de qualité
        silhouette = silhouette_score(X, labels)
        davies_bouldin = davies_bouldin_score(X, labels)
        calinski_harabasz = calinski_harabasz_score(X, labels)
        
        # Taille des clusters
        unique, counts = np.unique(labels, return_counts=True)
        cluster_sizes = dict(zip(unique.tolist(), counts.tolist()))
        
        # Centres des clusters
        centers = model.cluster_centers_
        
        return {
            'method': 'K-Means',
            'n_clusters': n_clusters,
            'labels': labels.tolist(),
            'cluster_sizes': cluster_sizes,
            'cluster_centers': centers.tolist(),
            'inertia': float(model.inertia_),
            'metrics': {
                'silhouette_score': float(silhouette),
                'davies_bouldin_index': float(davies_bouldin),
                'calinski_harabasz_score': float(calinski_harabasz)
            },
            'interpretation': {
                'silhouette': 'Excellent' if silhouette > 0.7 else 'Bon' if silhouette > 0.5 else 'Acceptable' if silhouette > 0.25 else 'Faible'
            }
        }
    
    def _dbscan_clustering(self, X, config):
        """DBSCAN - Density-Based Spatial Clustering"""
        eps = config.get('eps', 0.5)
        min_samples = config.get('min_samples', 5)
        
        model = DBSCAN(eps=eps, min_samples=min_samples)
        labels = model.fit_predict(X)
        
        # Nombre de clusters (sans compter le bruit: label=-1)
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = list(labels).count(-1)
        
        # Taille des clusters
        unique, counts = np.unique(labels, return_counts=True)
        cluster_sizes = dict(zip(unique.tolist(), counts.tolist()))
        
        # Métriques (seulement si on a au moins 2 clusters et pas tous les points comme bruit)
        if n_clusters >= 2 and n_noise < len(labels):
            # Filtrer les points de bruit pour le calcul du silhouette score
            mask = labels != -1
            if sum(mask) > 0:
                silhouette = silhouette_score(X[mask], labels[mask])
            else:
                silhouette = None
        else:
            silhouette = None
        
        return {
            'method': 'DBSCAN',
            'parameters': {
                'eps': eps,
                'min_samples': min_samples
            },
            'n_clusters': n_clusters,
            'n_noise_points': n_noise,
            'noise_percentage': float(n_noise / len(labels) * 100),
            'labels': labels.tolist(),
            'cluster_sizes': cluster_sizes,
            'metrics': {
                'silhouette_score': float(silhouette) if silhouette is not None else None
            },
            'interpretation': 'DBSCAN identifie les clusters de densité et détecte les points aberrants comme bruit'
        }
    
    def _hierarchical_clustering(self, X, config):
        """Hierarchical/Agglomerative Clustering"""
        n_clusters = config.get('n_clusters', 3)
        linkage = config.get('linkage', 'ward')
        
        model = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage)
        labels = model.fit_predict(X)
        
        # Métriques de qualité
        silhouette = silhouette_score(X, labels)
        davies_bouldin = davies_bouldin_score(X, labels)
        calinski_harabasz = calinski_harabasz_score(X, labels)
        
        # Taille des clusters
        unique, counts = np.unique(labels, return_counts=True)
        cluster_sizes = dict(zip(unique.tolist(), counts.tolist()))
        
        return {
            'method': 'Hierarchical Clustering',
            'n_clusters': n_clusters,
            'linkage': linkage,
            'labels': labels.tolist(),
            'cluster_sizes': cluster_sizes,
            'metrics': {
                'silhouette_score': float(silhouette),
                'davies_bouldin_index': float(davies_bouldin),
                'calinski_harabasz_score': float(calinski_harabasz)
            },
            'interpretation': {
                'linkage_method': f'Méthode de liaison: {linkage}',
                'silhouette': 'Excellent' if silhouette > 0.7 else 'Bon' if silhouette > 0.5 else 'Acceptable' if silhouette > 0.25 else 'Faible'
            }
        }
    
    def _gmm_clustering(self, X, config):
        """Gaussian Mixture Model"""
        n_components = config.get('n_clusters', 3)
        
        model = GaussianMixture(n_components=n_components, random_state=42)
        model.fit(X)
        labels = model.predict(X)
        probabilities = model.predict_proba(X)
        
        # Métriques de qualité
        silhouette = silhouette_score(X, labels)
        davies_bouldin = davies_bouldin_score(X, labels)
        
        # Taille des clusters
        unique, counts = np.unique(labels, return_counts=True)
        cluster_sizes = dict(zip(unique.tolist(), counts.tolist()))
        
        # Moyennes et covariances
        means = model.means_
        
        return {
            'method': 'Gaussian Mixture Model',
            'n_components': n_components,
            'labels': labels.tolist(),
            'probabilities_sample': probabilities[:10].tolist(),
            'cluster_sizes': cluster_sizes,
            'cluster_means': means.tolist(),
            'aic': float(model.aic(X)),
            'bic': float(model.bic(X)),
            'log_likelihood': float(model.score(X) * len(X)),
            'metrics': {
                'silhouette_score': float(silhouette),
                'davies_bouldin_index': float(davies_bouldin)
            },
            'interpretation': 'GMM est un modèle probabiliste qui suppose que les données proviennent de plusieurs distributions gaussiennes'
        }
    
    def _pca_visualization(self, X, models):
        """Réduction à 2D avec PCA pour visualisation"""
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X)
        
        visualization_data = {
            'pca_coordinates': X_pca.tolist(),
            'explained_variance_ratio': pca.explained_variance_ratio_.tolist(),
            'total_variance_explained': float(sum(pca.explained_variance_ratio_))
        }
        
        # Ajouter les labels de chaque modèle pour visualisation
        for model_name, model_result in models.items():
            if 'labels' in model_result:
                visualization_data[f'{model_name}_labels'] = model_result['labels']
        
        return visualization_data
    
    def _compare_clustering_models(self, models):
        """Compare les performances des différents modèles de clustering"""
        comparison = []
        
        for name, model_result in models.items():
            if 'metrics' in model_result and model_result['metrics'].get('silhouette_score') is not None:
                comparison.append({
                    'model': model_result['method'],
                    'silhouette_score': model_result['metrics']['silhouette_score'],
                    'n_clusters': model_result.get('n_clusters', model_result.get('n_components'))
                })
        
        # Trier par silhouette score (plus haut = meilleur)
        if comparison:
            comparison.sort(key=lambda x: x['silhouette_score'], reverse=True)
            
            return {
                'best_model': comparison[0]['model'],
                'comparison': comparison,
                'recommendation': f"Le modèle {comparison[0]['model']} a la meilleure qualité de clustering avec un Silhouette Score de {comparison[0]['silhouette_score']:.3f}"
            }
        else:
            return {
                'best_model': None,
                'comparison': [],
                'recommendation': 'Aucune métrique de silhouette disponible'
            }
