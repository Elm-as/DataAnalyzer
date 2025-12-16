# DataAnalyzer - Analyseur de Données Complet

Un outil d'analyse de données puissant et complet qui permet d'effectuer des analyses statistiques avancées, du machine learning, et du deep learning sans avoir besoin d'écrire du code.

## 🚀 Fonctionnalités

### Analyses de Base (Frontend - JavaScript)
- **Statistiques descriptives** : Moyenne, médiane, écart-type, quartiles
- **Corrélations** : Matrice de corrélation entre variables
- **Distributions** : Histogrammes et analyse de distribution
- **Détection d'anomalies** : Identification des valeurs aberrantes (IQR)
- **Analyse catégorielle** : Fréquences et modes
- **Tests d'association** : Chi-carré entre variables catégorielles

### Analyses Avancées (Backend - Python)

#### 1. Régression
- **Régression linéaire** : Modèle de base
- **Régression polynomiale** : Relations non-linéaires
- **Ridge Regression (L2)** : Régularisation L2
- **Lasso Regression (L1)** : Sélection de features automatique
- **ElasticNet** : Combinaison L1 + L2
- **Régression logistique** : Classification binaire/multi-classe

#### 2. Classification
- **K-Nearest Neighbors (KNN)** : Classification basée sur la proximité
- **Support Vector Machine (SVM)** : Séparation par hyperplan optimal
- **Random Forest** : Ensemble de decision trees
- **Decision Tree** : Arbre de décision
- **Naive Bayes** : Classification probabiliste
- **Gradient Boosting** : Boosting gradient
- **XGBoost** : Extreme Gradient Boosting
- **LightGBM** : Gradient Boosting léger et rapide
- **AdaBoost** : Adaptive Boosting

#### 3. Analyse Discriminante
- **LDA (Linear Discriminant Analysis)** : Analyse discriminante linéaire
- **QDA (Quadratic Discriminant Analysis)** : Analyse discriminante quadratique

#### 4. Réseaux de Neurones
- **MLP (Multi-Layer Perceptron)** : Réseau de neurones classique
- **Deep MLP** : Réseau profond avec Keras/TensorFlow
- **CNN (Convolutional Neural Network)** : Réseaux convolutifs
- **RNN (Recurrent Neural Network)** : Réseaux récurrents
- **LSTM (Long Short-Term Memory)** : Mémoire à long terme

#### 5. Séries Temporelles
- **ARIMA** : AutoRegressive Integrated Moving Average
- **SARIMA** : ARIMA saisonnier
- **Prophet** : Modèle de Facebook pour séries temporelles

#### 6. Clustering Avancé
- **K-Means** : Clustering par centres
- **DBSCAN** : Clustering basé sur la densité
- **Hierarchical Clustering** : Clustering hiérarchique
- **Gaussian Mixture Model (GMM)** : Modèle de mélange gaussien

#### 7. Nettoyage de Données
- Suppression des doublons
- Gestion des valeurs manquantes (mean, median, mode, KNN, forward/backward fill)
- Détection et traitement des valeurs aberrantes (IQR, Z-score)
- Normalisation (StandardScaler, MinMaxScaler, RobustScaler)
- Encodage des variables catégorielles (Label Encoding, One-Hot Encoding)
- Conversion de types (dates, nombres)

#### 8. Tests Statistiques Avancés
- **Tests de normalité** : Shapiro-Wilk, D'Agostino
- **T-test** : Test t de Student (indépendant et apparié)
- **ANOVA** : Analyse de variance
- **Kruskal-Wallis** : Alternative non-paramétrique à ANOVA
- **Mann-Whitney U** : Alternative non-paramétrique au t-test
- **Chi-carré** : Test d'indépendance
- **Test de Levene** : Homogénéité des variances
- **Tests de corrélation** : Pearson, Spearman

### Génération de Rapports
- **Format PDF A4**
- **Police 13-14 pt** pour une lecture optimale
- **Noir et blanc** pour impression économique
- Sections détaillées pour chaque analyse
- Tableaux de métriques et résultats
- Interprétations automatiques

## 📋 Installation

### Prérequis
- Node.js (v16 ou supérieur)
- Python 3.8 ou supérieur
- npm ou yarn

### Installation du Frontend

```bash
cd DataAnalyzer
npm install
```

### Installation du Backend

```bash
cd backend
pip install -r requirements.txt
```

## 🎯 Démarrage

### 1. Démarrer le Backend Python

```bash
cd backend
python app.py
```

Le backend sera accessible sur `http://localhost:5000`

### 2. Démarrer le Frontend React

```bash
npm run dev
```

Le frontend sera accessible sur `http://localhost:5173`

## 📖 Utilisation

### Étape 1: Importer vos données
- Formats supportés : CSV, Excel (XLSX), JSON
- Glissez-déposez ou cliquez pour sélectionner
- Détection automatique des colonnes et types

### Étape 2: Prévisualiser
- Vérifiez que vos données sont correctement chargées
- Visualisez les premières lignes
- Validation automatique

### Étape 3: Configuration
- Sélectionnez les colonnes à analyser
- Définissez les types de données (nombre, texte, date, catégorie)
- Marquez les colonnes d'en-tête si nécessaire

### Étape 4: Choisir les analyses
- **Analyses rapides** : Statistiques descriptives de base
- **Analyses avancées** : Machine Learning et Deep Learning
- Combinez plusieurs analyses selon vos besoins

### Étape 5: Résultats
- Visualisez tous les résultats dans une interface interactive
- Onglets séparés par type d'analyse
- Téléchargez les résultats en JSON
- **Générez un rapport PDF professionnel**

## 🔧 Configuration des Analyses

### Régression - Exemple de configuration

```json
{
  "target": "prix",
  "features": ["superficie", "chambres", "age"],
  "methods": ["linear", "polynomial", "ridge", "lasso"],
  "polynomial_degree": 2,
  "test_size": 0.2
}
```

### Classification - Exemple

```json
{
  "target": "categorie",
  "features": ["var1", "var2", "var3"],
  "methods": ["random_forest", "xgboost", "svm"],
  "test_size": 0.2,
  "cv_folds": 5
}
```

### Séries Temporelles - Exemple

```json
{
  "date_column": "date",
  "target_column": "ventes",
  "methods": ["arima", "sarima", "prophet"],
  "forecast_periods": 30,
  "arima_order": [1, 1, 1]
}
```

### Nettoyage - Exemple

```json
{
  "remove_duplicates": true,
  "handle_missing": {
    "method": "knn",
    "threshold": 0.5
  },
  "handle_outliers": {
    "method": "iqr",
    "action": "cap"
  },
  "normalize": {
    "method": "standard"
  },
  "encode_categorical": {
    "method": "onehot"
  }
}
```

## 📊 Métriques et Évaluation

### Régression
- **R² Score** : Coefficient de détermination
- **RMSE** : Root Mean Squared Error
- **MAE** : Mean Absolute Error
- **Cross-validation** : Validation croisée

### Classification
- **Accuracy** : Précision globale
- **Precision** : Précision par classe
- **Recall** : Rappel
- **F1-Score** : Moyenne harmonique
- **Confusion Matrix** : Matrice de confusion
- **ROC-AUC** : Aire sous la courbe ROC

### Clustering
- **Silhouette Score** : Qualité du clustering
- **Davies-Bouldin Index** : Séparation des clusters
- **Calinski-Harabasz Score** : Ratio variance

### Séries Temporelles
- **MAPE** : Mean Absolute Percentage Error
- **AIC/BIC** : Critères d'information
- **Prévisions** : Intervalles de confiance

## 🎨 Interprétation des Résultats

**IMPORTANT** : Cet outil génère les résultats et métriques. L'interprétation et la compréhension des résultats restent la responsabilité de l'utilisateur (Data Scientist ou étudiant).

Les métriques fournies vous permettent de :
- Comparer différents modèles
- Identifier le meilleur algorithme pour vos données
- Comprendre les relations dans vos données
- Prendre des décisions basées sur les données

## 🚀 Bonnes Pratiques

### Préparation des Données
1. Nettoyez vos données avant l'analyse
2. Vérifiez les valeurs manquantes
3. Supprimez les doublons
4. Normalisez si nécessaire

### Sélection des Modèles
1. Commencez par des modèles simples
2. Augmentez la complexité progressivement
3. Utilisez la validation croisée
4. Comparez plusieurs algorithmes

### Évaluation
1. Ne vous fiez pas qu'à une seule métrique
2. Visualisez les résultats
3. Testez sur des données non vues
4. Validez avec un expert du domaine

## 📝 Génération de Rapports PDF

Les rapports PDF incluent :
- Page de garde avec informations générales
- Table des matières
- Résumé exécutif
- Sections détaillées pour chaque analyse
- Tableaux de métriques
- Mise en page professionnelle A4
- Format noir et blanc pour impression

Pour générer un rapport :
1. Effectuez vos analyses
2. Cliquez sur "Générer un rapport PDF"
3. Le PDF sera téléchargé automatiquement

## 🔍 Dépannage

### Le backend ne démarre pas
```bash
# Vérifiez que Python est installé
python --version

# Réinstallez les dépendances
pip install -r requirements.txt --upgrade
```

### Erreur TensorFlow
```bash
# TensorFlow est optionnel, peut être désactivé
# Ou installez une version compatible
pip install tensorflow==2.15.0
```

### Erreur Prophet
```bash
# Prophet nécessite des dépendances spécifiques
pip install prophet

# Sur Windows, peut nécessiter Visual C++
```

## 📦 Technologies Utilisées

### Frontend
- React 18
- TypeScript
- TailwindCSS
- Vite
- Lucide React (icônes)

### Backend
- Flask (API REST)
- Pandas (manipulation de données)
- NumPy (calculs numériques)
- Scikit-learn (Machine Learning)
- TensorFlow/Keras (Deep Learning)
- Statsmodels (statistiques avancées)
- Prophet (séries temporelles)
- ReportLab (génération PDF)
- XGBoost & LightGBM (boosting avancé)

## 🤝 Contribution

Ce projet est conçu pour accélérer l'analyse de données. Les contributions sont bienvenues pour ajouter :
- Nouveaux algorithmes
- Nouvelles visualisations
- Améliorations des rapports
- Optimisations de performance

## 📄 Licence

Ce projet est fourni tel quel pour l'analyse de données. L'utilisateur est responsable de l'interprétation des résultats.

## 🎓 Pour les Étudiants et Data Scientists

Cet outil vous permet de :
- **Gagner du temps** sur les tâches répétitives
- **Comparer rapidement** plusieurs algorithmes
- **Expérimenter** avec différentes approches
- **Générer des rapports** professionnels

**MAIS** : Vous devez comprendre et interpréter les résultats vous-même. C'est votre valeur ajoutée en tant que Data Scientist !

---

**Version** : 2.0.0  
**Dernière mise à jour** : Novembre 2024
