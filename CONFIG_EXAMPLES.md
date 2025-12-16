# Exemples de Configuration pour les Analyses

## 1. Régression - Prédiction de Prix Immobilier

```json
{
  "target": "prix",
  "features": ["superficie", "nb_chambres", "age_maison", "distance_centre"],
  "methods": ["linear", "polynomial", "ridge", "lasso", "elastic"],
  "polynomial_degree": 2,
  "test_size": 0.2,
  "cv_folds": 5,
  "ridge_alpha": 1.0,
  "lasso_alpha": 0.1
}
```

**Interprétation** :
- Compare 5 modèles de régression
- Polynomiale degree 2 pour relations non-linéaires
- 20% des données pour test
- Cross-validation sur 5 folds

## 2. Classification - Détection de Churn

```json
{
  "target": "a_quitte",
  "features": ["duree_abonnement", "montant_total", "nb_appels", "satisfaction"],
  "methods": ["random_forest", "xgboost", "lightgbm", "svm", "knn"],
  "test_size": 0.25,
  "cv_folds": 10,
  "rf_n_estimators": 200,
  "xgb_n_estimators": 100,
  "xgb_learning_rate": 0.1,
  "knn_neighbors": 7
}
```

**Utilisation** :
- Identifie les clients susceptibles de partir
- Compare 5 algorithmes
- Random Forest avec 200 arbres pour robustesse

## 3. Analyse Discriminante - Segmentation Client

```json
{
  "target": "segment_client",
  "features": ["age", "revenu", "score_credit", "nb_produits"],
  "methods": ["lda", "qda"],
  "test_size": 0.2,
  "cv_folds": 5,
  "n_components": 2
}
```

**Quand utiliser** :
- Classification avec réduction de dimensionalité
- LDA si variances égales entre groupes
- QDA si variances différentes

## 4. Réseaux de Neurones - Classification Image/Texte

```json
{
  "target": "categorie",
  "features": ["feature1", "feature2", "...", "feature100"],
  "task": "classification",
  "methods": ["mlp_deep", "cnn", "lstm"],
  "epochs": 50,
  "batch_size": 32,
  "learning_rate": 0.001,
  "test_size": 0.2
}
```

**Note** :
- MLP pour données tabulaires
- CNN pour données avec structure spatiale
- LSTM pour séquences temporelles
- Nécessite TensorFlow installé

## 5. Séries Temporelles - Prévision de Ventes

```json
{
  "date_column": "date",
  "target_column": "ventes",
  "methods": ["arima", "sarima", "prophet"],
  "forecast_periods": 30,
  "arima_order": [1, 1, 1],
  "sarima_order": [1, 1, 1],
  "sarima_seasonal_order": [1, 1, 1, 12],
  "test_size": 0.2
}
```

**Paramètres ARIMA** :
- p : ordre autorégressif (1-3 généralement)
- d : ordre de différenciation (1-2)
- q : ordre moyenne mobile (1-3)

**Saisonnalité SARIMA** :
- P, D, Q : comme ARIMA mais pour saisonnalité
- s : période (12 pour mensuel, 7 pour hebdo)

## 6. Clustering - Segmentation RFM

```json
{
  "features": ["recence", "frequence", "montant"],
  "methods": ["kmeans", "dbscan", "hierarchical", "gmm"],
  "n_clusters": 4,
  "eps": 0.5,
  "min_samples": 5,
  "linkage": "ward",
  "find_optimal_k": true
}
```

**Choix de méthode** :
- K-Means : rapide, clusters sphériques
- DBSCAN : détecte formes arbitraires + bruit
- Hierarchical : dendrogramme
- GMM : probabilités d'appartenance

## 7. Nettoyage de Données - Pipeline Complet

```json
{
  "remove_duplicates": true,
  "handle_missing": {
    "method": "knn",
    "threshold": 0.5
  },
  "handle_outliers": {
    "method": "iqr",
    "columns": ["prix", "age", "salaire"],
    "action": "cap"
  },
  "normalize": {
    "method": "standard",
    "columns": ["feature1", "feature2"]
  },
  "encode_categorical": {
    "method": "onehot",
    "columns": ["ville", "categorie"]
  },
  "convert_types": {
    "date_columns": ["date_achat", "date_naissance"],
    "numeric_columns": ["code_postal", "telephone"]
  }
}
```

**Ordre recommandé** :
1. Conversion de types
2. Suppression doublons
3. Gestion valeurs manquantes
4. Détection outliers
5. Normalisation
6. Encodage catégories

## 8. Tests Statistiques - Comparaison Groupes

```json
{
  "tests": ["normality", "ttest", "anova", "levene"],
  "ttest": {
    "group_column": "groupe",
    "value_column": "score",
    "paired": false
  },
  "anova": {
    "group_column": "traitement",
    "value_column": "resultat"
  },
  "levene": {
    "group_column": "groupe",
    "value_column": "variance"
  },
  "alpha": 0.05
}
```

**Tests disponibles** :
- normality : Shapiro-Wilk, D'Agostino
- ttest : comparaison 2 groupes
- anova : comparaison 3+ groupes
- kruskal : ANOVA non-paramétrique
- mann_whitney : t-test non-paramétrique
- chi_square : indépendance catégories
- correlation_test : Pearson, Spearman

## Configuration Multi-Analyses

```json
{
  "analyses": {
    "cleaning": {
      "enabled": true,
      "config": { /* config nettoyage */ }
    },
    "exploratory": {
      "enabled": true,
      "descriptive_stats": true,
      "correlations": true,
      "distributions": true
    },
    "modeling": {
      "enabled": true,
      "regression": { /* config régression */ },
      "classification": { /* config classification */ }
    },
    "validation": {
      "enabled": true,
      "statistical_tests": { /* config tests */ }
    }
  },
  "report": {
    "format": "pdf",
    "include_visualizations": true,
    "language": "fr"
  }
}
```

## Bonnes Pratiques de Configuration

### Pour la Régression
✅ Testez plusieurs modèles
✅ Utilisez polynomial si relation non-linéaire
✅ Ridge/Lasso si multicollinéarité
✅ Cross-validation minimale : 5 folds

### Pour la Classification
✅ Équilibrez vos classes si possible
✅ Utilisez F1-score si classes déséquilibrées
✅ Random Forest comme baseline
✅ XGBoost/LightGBM pour performance max

### Pour les Séries Temporelles
✅ Vérifiez stationnarité (test ADF)
✅ Commencez avec ARIMA(1,1,1)
✅ Prophet pour tendances + saisonnalité complexe
✅ Gardez 20% pour validation

### Pour le Clustering
✅ Normalisez TOUJOURS les données
✅ Utilisez find_optimal_k pour K-Means
✅ DBSCAN si clusters de formes irrégulières
✅ Validez avec Silhouette Score

### Pour le Nettoyage
✅ Toujours sauvegarder données originales
✅ Documentez chaque transformation
✅ Vérifiez résultats après chaque étape
✅ KNN imputation > mean pour données MCAR

## Métriques Cibles

### Régression
- **R² > 0.7** : Bon modèle
- **R² > 0.5** : Acceptable
- **R² < 0.3** : Mauvais, chercher autres features

### Classification
- **Accuracy > 0.9** : Excellent
- **Accuracy > 0.8** : Bon
- **F1-Score** : Plus important qu'accuracy si déséquilibré

### Clustering
- **Silhouette > 0.7** : Excellent
- **Silhouette > 0.5** : Bon
- **Silhouette > 0.25** : Acceptable

### Séries Temporelles
- **MAPE < 10%** : Excellent
- **MAPE < 20%** : Bon
- **MAPE < 30%** : Acceptable

---

Adaptez ces configurations à vos besoins spécifiques !
