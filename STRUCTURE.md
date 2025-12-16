# 📁 Structure du Projet DataAnalyzer

```
DataAnalyzer/
│
├── 📄 README.md                    # Documentation principale
├── 📄 QUICKSTART.md                # Guide de démarrage rapide (5 min)
├── 📄 USER_GUIDE.md                # Guide utilisateur complet
├── 📄 CONFIG_EXAMPLES.md           # Exemples de configuration
├── 📄 package.json                 # Dépendances Node.js
├── 📄 .gitignore                   # Fichiers ignorés par Git
├── 📄 vite.config.ts               # Configuration Vite
├── 📄 tsconfig.json                # Configuration TypeScript
├── 📄 tailwind.config.js           # Configuration TailwindCSS
│
├── 📂 src/                         # Code source Frontend
│   ├── 📄 App.tsx                  # Application principale
│   ├── 📄 main.tsx                 # Point d'entrée
│   ├── 📄 index.css                # Styles globaux
│   │
│   ├── 📂 components/              # Composants React
│   │   ├── FileUpload.tsx          # Import de fichiers
│   │   ├── DataPreview.tsx         # Prévisualisation
│   │   ├── DataConfiguration.tsx   # Configuration colonnes
│   │   ├── AnalysisOptions.tsx     # Sélection analyses
│   │   ├── AnalysisResults.tsx     # Affichage résultats
│   │   └── Sidebar.tsx             # Navigation
│   │
│   └── 📂 api/                     # API Backend
│       └── backend.ts              # Appels API Python
│
├── 📂 backend/                     # Code source Backend Python
│   ├── 📄 app.py                   # API Flask principale
│   ├── 📄 requirements.txt         # Dépendances Python
│   ├── 📄 test_backend.py          # Tests du backend
│   ├── 📄 example_data.csv         # Données d'exemple
│   │
│   ├── 📂 analyses/                # Modules d'analyse
│   │   ├── __init__.py
│   │   ├── regression.py           # 📊 Régression (Linear, Ridge, Lasso, etc.)
│   │   ├── classification.py       # 🎯 Classification (RF, SVM, XGBoost, etc.)
│   │   ├── discriminant.py         # 📈 LDA, QDA
│   │   ├── neural_networks.py      # 🧠 MLP, CNN, RNN, LSTM
│   │   ├── time_series.py          # ⏰ ARIMA, SARIMA, Prophet
│   │   ├── clustering.py           # 🔵 K-Means, DBSCAN, Hierarchical
│   │   ├── data_cleaning.py        # 🧹 Nettoyage de données
│   │   └── advanced_stats.py       # 📐 Tests statistiques
│   │
│   └── 📂 reports/                 # Génération de rapports
│       ├── __init__.py
│       └── pdf_generator.py        # 📑 Rapports PDF A4
│
└── 📂 node_modules/                # Dépendances (généré)
```

## 🎨 Technologies Utilisées

### Frontend (Interface Web)
| Technologie | Version | Usage |
|------------|---------|-------|
| React | 18.3 | Framework UI |
| TypeScript | 5.5 | Typage statique |
| Vite | 5.4 | Build tool |
| TailwindCSS | 3.4 | Styles CSS |
| Lucide React | 0.344 | Icônes |

### Backend (Analyses)
| Bibliothèque | Usage |
|-------------|-------|
| Flask | API REST |
| Pandas | Manipulation données |
| NumPy | Calculs numériques |
| Scikit-learn | Machine Learning |
| TensorFlow/Keras | Deep Learning |
| Statsmodels | Statistiques avancées |
| Prophet | Séries temporelles |
| XGBoost | Gradient Boosting |
| LightGBM | Gradient Boosting léger |
| ReportLab | Génération PDF |

## 📊 Fonctionnalités par Fichier

### Backend - Modules d'Analyse

#### `regression.py` (380 lignes)
**Fonctionnalités** :
- ✅ Régression Linéaire
- ✅ Régression Polynomiale (degree configurable)
- ✅ Ridge Regression (L2 regularization)
- ✅ Lasso Regression (L1 + feature selection)
- ✅ ElasticNet (L1 + L2)
- ✅ Régression Logistique (classification)
- ✅ Cross-validation
- ✅ Métriques : R², RMSE, MAE

#### `classification.py` (450 lignes)
**Fonctionnalités** :
- ✅ K-Nearest Neighbors (k configurable)
- ✅ Support Vector Machine (kernels: rbf, linear, poly)
- ✅ Random Forest (avec feature importance)
- ✅ Decision Tree
- ✅ Naive Bayes (Gaussian)
- ✅ Gradient Boosting
- ✅ XGBoost (si installé)
- ✅ LightGBM (si installé)
- ✅ AdaBoost
- ✅ Métriques : Accuracy, Precision, Recall, F1, Confusion Matrix

#### `discriminant.py` (220 lignes)
**Fonctionnalités** :
- ✅ Linear Discriminant Analysis (avec réduction dimensionalité)
- ✅ Quadratic Discriminant Analysis
- ✅ Explained variance ratio
- ✅ Feature importance par composante
- ✅ Recommandations automatiques (LDA vs QDA)

#### `neural_networks.py` (380 lignes)
**Fonctionnalités** :
- ✅ MLP Sklearn (simple et rapide)
- ✅ Deep MLP avec Keras (architecture profonde)
- ✅ CNN 1D (pour données tabulaires)
- ✅ RNN (Recurrent Neural Networks)
- ✅ LSTM (Long Short-Term Memory)
- ✅ Early stopping
- ✅ Training history

#### `time_series.py` (350 lignes)
**Fonctionnalités** :
- ✅ Tests de stationnarité (ADF)
- ✅ ACF/PACF pour paramètres ARIMA
- ✅ ARIMA (configurable p,d,q)
- ✅ SARIMA (avec saisonnalité)
- ✅ Prophet de Facebook
- ✅ Prévisions futures
- ✅ Métriques : MAPE, AIC, BIC

#### `clustering.py` (280 lignes)
**Fonctionnalités** :
- ✅ K-Means (avec recherche k optimal)
- ✅ DBSCAN (détection de bruit)
- ✅ Hierarchical/Agglomerative
- ✅ Gaussian Mixture Model
- ✅ PCA pour visualisation 2D
- ✅ Métriques : Silhouette, Davies-Bouldin, Calinski-Harabasz

#### `data_cleaning.py` (350 lignes)
**Fonctionnalités** :
- ✅ Suppression doublons
- ✅ Gestion valeurs manquantes (mean, median, mode, KNN, forward/backward fill)
- ✅ Détection outliers (IQR, Z-score)
- ✅ Normalisation (Standard, MinMax, Robust)
- ✅ Encodage catégories (Label, OneHot)
- ✅ Conversion types (date, numérique)
- ✅ Rapport détaillé de nettoyage

#### `advanced_stats.py` (420 lignes)
**Fonctionnalités** :
- ✅ Tests de normalité (Shapiro-Wilk, D'Agostino)
- ✅ T-test (indépendant et apparié)
- ✅ ANOVA (comparaison multi-groupes)
- ✅ Kruskal-Wallis (ANOVA non-paramétrique)
- ✅ Mann-Whitney U (t-test non-paramétrique)
- ✅ Chi-carré d'indépendance
- ✅ Test de Levene (homogénéité variances)
- ✅ Tests de corrélation (Pearson, Spearman)
- ✅ Cramér's V, Cohen's d (effect sizes)

#### `pdf_generator.py` (280 lignes)
**Fonctionnalités** :
- ✅ Génération PDF A4
- ✅ Police 13-14pt (lecture optimale)
- ✅ Noir et blanc (impression économique)
- ✅ Page de garde professionnelle
- ✅ Table des matières
- ✅ Sections par analyse
- ✅ Tableaux de métriques
- ✅ Mise en page automatique

### Frontend - Composants

#### `App.tsx` (170 lignes)
- Navigation entre étapes
- Gestion état global
- Workflow en 5 étapes

#### `FileUpload.tsx`
- Drag & drop fichiers
- Support CSV, XLSX, JSON
- Parsing automatique

#### `DataPreview.tsx`
- Affichage tableau données
- Détection types colonnes
- Validation données

#### `DataConfiguration.tsx`
- Sélection colonnes
- Configuration types
- Marquage en-têtes

#### `AnalysisOptions.tsx`
- Interface sélection analyses
- Progression temps réel
- Lancement analyses

#### `AnalysisResults.tsx`
- Onglets par analyse
- Tableaux métriques
- Visualisations
- Export JSON/PDF

## 📈 Métriques du Projet

**Code Backend** :
- ~2,500 lignes Python
- 8 modules d'analyse
- 50+ algorithmes/méthodes
- 1 générateur PDF

**Code Frontend** :
- ~1,500 lignes TypeScript/React
- 6 composants principaux
- Interface responsive
- Design professionnel

**Documentation** :
- 4 fichiers de documentation
- Exemples de configuration
- Guide utilisateur complet
- README détaillé

**Tests** :
- Script de test automatique
- Validation dépendances
- Test modules d'analyse
- Test API Flask

## 🚀 Commandes Rapides

```bash
# Frontend
npm install              # Installer dépendances
npm run dev              # Démarrer (http://localhost:5173)
npm run build            # Build production
npm run preview          # Prévisualiser build

# Backend
pip install -r requirements.txt    # Installer dépendances
python app.py                      # Démarrer API (port 5000)
python test_backend.py             # Tester backend

# NPM Scripts
npm run backend          # Démarrer backend depuis racine
npm run test-backend     # Tester backend depuis racine
```

## 🎯 Cas d'Usage

| Analyse | Fichier | Temps | Complexité |
|---------|---------|-------|------------|
| Stats descriptives | Frontend | < 1s | ⭐ Facile |
| Corrélations | Frontend | < 2s | ⭐ Facile |
| Régression linéaire | regression.py | ~2s | ⭐⭐ Moyen |
| Random Forest | classification.py | ~5s | ⭐⭐ Moyen |
| Deep Learning | neural_networks.py | ~30s | ⭐⭐⭐ Avancé |
| Séries temporelles | time_series.py | ~10s | ⭐⭐⭐ Avancé |
| Rapport PDF | pdf_generator.py | ~3s | ⭐ Facile |

## 📦 Tailles Approximatives

```
Frontend build:     ~500 KB (gzipped)
Backend API:        Léger (Flask)
Dépendances Python: ~2 GB (avec TensorFlow)
Dépendances Node:   ~300 MB
```

## 🔐 Sécurité & Limitations

- ✅ Données traitées localement
- ✅ Pas de stockage distant
- ✅ Open source, code inspectable
- ⚠️  Limite fichiers : ~1 million lignes
- ⚠️  GPU recommandé pour Deep Learning
- ⚠️  RAM minimale : 8 GB

## 🎓 Niveau Requis

- **Débutant** : Analyses de base, rapports PDF
- **Intermédiaire** : Régression, classification, clustering
- **Avancé** : Deep Learning, séries temporelles, tests stats

## 📚 Prochaines Étapes

1. Lisez `QUICKSTART.md` (5 min)
2. Testez avec `example_data.csv`
3. Consultez `CONFIG_EXAMPLES.md`
4. Lisez `USER_GUIDE.md`
5. Explorez les analyses avancées

---

**Version** : 2.0.0
**Dernière mise à jour** : Novembre 2024
**License** : MIT (usage libre)
