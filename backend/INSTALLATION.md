# Guide d'installation du Backend

## Problème courant sur Windows

Si vous rencontrez l'erreur "Unknown compiler" lors de l'installation, c'est que Python 3.14 est trop récent et nécessite un compilateur C.

## Solutions

### Solution 1 : Utiliser Python 3.11 ou 3.12 (RECOMMANDÉ)

1. Désinstallez Python 3.14
2. Téléchargez Python 3.11 ou 3.12 depuis python.org
3. Installez et réessayez

### Solution 2 : Installation simplifiée (sans deep learning)

```powershell
# Installer les dépendances de base seulement
pip install flask flask-cors pandas numpy scipy scikit-learn statsmodels reportlab matplotlib seaborn openpyxl python-dateutil joblib
```

Cette commande installe toutes les bibliothèques essentielles sauf TensorFlow, Prophet, XGBoost et LightGBM.

### Solution 3 : Installation avec wheels précompilés

Téléchargez les wheels (.whl) depuis https://www.lfd.uci.edu/~gohlke/pythonlibs/

```powershell
# Exemple pour numpy
pip install numpy-1.26.4-cp312-cp312-win_amd64.whl
```

### Solution 4 : Installer Visual Studio Build Tools

1. Téléchargez "Build Tools for Visual Studio" depuis microsoft.com
2. Installez "Desktop development with C++"
3. Réessayez l'installation

## Installation par étapes

### Étape 1 : Dépendances de base (obligatoires)

```powershell
pip install flask flask-cors
pip install pandas numpy scipy
pip install scikit-learn statsmodels
pip install reportlab matplotlib seaborn
pip install openpyxl python-dateutil joblib
```

### Étape 2 : Dépendances avancées (optionnelles)

```powershell
# Pour le deep learning (nécessite beaucoup d'espace)
pip install tensorflow keras

# Pour les séries temporelles avancées
pip install prophet

# Pour les algorithmes de boosting
pip install xgboost lightgbm
```

## Vérification de l'installation

```powershell
python test_backend.py
```

Ce script vérifie quelles bibliothèques sont installées.

## Démarrage du backend

```powershell
python app.py
```

Le serveur devrait démarrer sur http://localhost:5000

## Fonctionnalités disponibles selon les dépendances

### Avec installation de base :
- Régression (linéaire, polynomial, Ridge, Lasso, ElasticNet, logistique)
- Classification (KNN, SVM, Random Forest, Decision Tree, Naive Bayes, Gradient Boosting, AdaBoost)
- Analyse discriminante (LDA, QDA)
- Clustering (K-Means, DBSCAN, Hierarchical, GMM)
- Nettoyage de données
- Tests statistiques avancés
- Rapports PDF

### Avec TensorFlow/Keras :
- Réseaux de neurones profonds (MLP, CNN, RNN, LSTM)

### Avec Prophet :
- Prévisions de séries temporelles avancées

### Avec XGBoost/LightGBM :
- Algorithmes de boosting optimisés

## Troubleshooting

### Erreur : "No module named 'flask'"
```powershell
pip install flask
```

### Erreur : "Microsoft Visual C++ required"
Installez Visual Studio Build Tools ou utilisez Python 3.11/3.12

### Erreur : Port 5000 déjà utilisé
Modifiez le port dans `app.py` :
```python
app.run(debug=True, port=5001)  # Changez 5001 par un autre port
```

### Erreur : CORS
Vérifiez que flask-cors est installé :
```powershell
pip install flask-cors
```

## Installation réussie

Vous devriez voir :
```
* Running on http://127.0.0.1:5000
* Restarting with stat
* Debugger is active!
```

Les analyses avancées sont maintenant disponibles dans l'interface web.
