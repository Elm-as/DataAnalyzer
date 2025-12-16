# Guide de Demarrage Rapide - DataAnalyzer

## Installation Express (5 minutes)

### Methode 1 : Scripts Windows (RECOMMANDE)

#### 1. Installation du Backend

Double-cliquez sur `install-backend.bat`

Ce script va :
- Creer un environnement virtuel Python
- Installer toutes les dependances
- Tester l'installation

#### 2. Demarrage de l'application

Double-cliquez sur `start-all.bat`

Cela va ouvrir :
- Backend sur http://localhost:5000
- Frontend sur http://localhost:5173

Ouvrez votre navigateur sur http://localhost:5173

### Methode 2 : Ligne de commande

#### 1. Backend Python

```powershell
# L'environnement virtuel est deja cree (.venv)
# Activer l'environnement
.venv\Scripts\activate

# Les dependances sont deja installees
# Demarrer le backend
cd backend
python app.py
```

#### 2. Frontend React

```powershell
# Dans un nouveau terminal

# Les dependances sont deja installees (npm install deja fait)
# Demarrer le frontend
npm run dev
```

## Lancement (30 secondes)

### Terminal 1 : Backend
```powershell
cd backend
python app.py
```

Vous devriez voir :
```
* Running on http://127.0.0.1:5000
```

### Terminal 2 : Frontend
```powershell
npm run dev
```

Vous devriez voir :
```
  VITE ready in XXX ms

  ➜  Local:   http://localhost:5173/
```

## Premier Test (2 minutes)

1. **Ouvrez votre navigateur** : http://localhost:5173

2. **Importez des données** :
   - Créez un fichier CSV simple :
   ```csv
   age,salaire,experience,diplome
   25,30000,2,Licence
   30,45000,5,Master
   35,60000,10,Master
   28,38000,3,Licence
   40,75000,15,Doctorat
   ```

3. **Analysez** :
   - Sélectionnez les analyses souhaitées
   - Cliquez sur "Lancer l'analyse"
   - Consultez les résultats

4. **Générez un rapport PDF** :
   - Cliquez sur "Générer un rapport PDF"
   - Téléchargez votre rapport professionnel

## Analyses Disponibles

### 📊 Analyses de Base (Frontend - Rapide)
✅ Statistiques descriptives  
✅ Corrélations  
✅ Distributions  
✅ Détection d'anomalies  

### 🤖 Analyses Avancées (Backend - Plus lent mais puissant)

#### Régression
```javascript
// Exemple : Prédire le salaire en fonction de l'âge et l'expérience
config = {
  target: 'salaire',
  features: ['age', 'experience'],
  methods: ['linear', 'polynomial', 'ridge']
}
```

#### Classification
```javascript
// Exemple : Prédire le diplôme en fonction de l'âge et salaire
config = {
  target: 'diplome',
  features: ['age', 'salaire', 'experience'],
  methods: ['random_forest', 'svm', 'knn']
}
```

#### Séries Temporelles
```javascript
// Exemple : Prévisions de ventes
config = {
  date_column: 'date',
  target_column: 'ventes',
  methods: ['arima', 'prophet'],
  forecast_periods: 30  // 30 jours dans le futur
}
```

#### Nettoyage
```javascript
config = {
  remove_duplicates: true,
  handle_missing: { method: 'mean' },
  normalize: { method: 'standard' }
}
```

## Cas d'Usage Typiques

### 1. Analyse Exploratoire Rapide
1. Importer CSV
2. Activer : Statistiques descriptives + Corrélations + Distributions
3. Analyser
4. Générer rapport PDF

### 2. Prédiction (Régression)
1. Importer données
2. Identifier variable cible (numérique)
3. Sélectionner features
4. Activer Régression
5. Comparer modèles dans les résultats
6. Choisir le meilleur R² Score

### 3. Classification
1. Importer données
2. Identifier variable cible (catégorie)
3. Sélectionner features
4. Activer Classification
5. Comparer F1-Score des modèles

### 4. Prévisions Temporelles
1. Importer données avec colonne date
2. Spécifier date_column et target_column
3. Activer Séries Temporelles
4. Obtenir prévisions futures

## Dépendances Optionnelles

Si vous voulez TOUT :
```bash
pip install tensorflow prophet xgboost lightgbm
```

Si vous voulez le minimum (sans Deep Learning) :
```bash
pip install flask flask-cors pandas numpy scikit-learn statsmodels scipy reportlab matplotlib seaborn
```

## Problèmes Courants

### ❌ Le backend ne démarre pas
**Solution** : Vérifiez que le port 5000 est libre
```powershell
# Tuer le processus sur le port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### ❌ Erreur CORS
**Solution** : Vérifiez que `flask-cors` est installé
```bash
pip install flask-cors
```

### ❌ Module 'tensorflow' not found
**Solution** : TensorFlow est optionnel, désactivez les analyses de réseaux de neurones ou installez-le
```bash
pip install tensorflow
```

### ❌ Erreur lors de l'installation de Prophet
**Solution** : Prophet nécessite des outils de compilation
```bash
# Sur Windows, installez Visual C++ Build Tools
# Ou utilisez conda
conda install -c conda-forge prophet
```

## Performance

### Vitesse d'Analyse (approximative)

| Analyse | Taille Données | Temps |
|---------|---------------|-------|
| Statistiques descriptives | 10,000 lignes | < 1s |
| Corrélations | 10,000 lignes | < 2s |
| Régression linéaire | 10,000 lignes | ~ 2s |
| Random Forest | 10,000 lignes | ~ 5s |
| Deep Learning | 10,000 lignes | ~ 30s |
| ARIMA | 1,000 points | ~ 10s |

### Limites Recommandées

- **Frontend** : < 50,000 lignes pour fluidité
- **Backend** : < 1,000,000 lignes
- **Deep Learning** : < 100,000 lignes (selon GPU)
- **Séries Temporelles** : < 10,000 points

## Tips & Tricks

### 💡 Accélérer les Analyses
1. Utilisez un sous-échantillon pour tests
2. Désactivez les analyses non nécessaires
3. Réduisez le nombre de features
4. Utilisez la validation croisée avec moins de folds

### 💡 Meilleurs Résultats
1. Nettoyez les données d'abord
2. Normalisez pour la plupart des algorithmes ML
3. Utilisez la cross-validation
4. Comparez plusieurs modèles

### 💡 Rapports Professionnels
1. Donnez des noms de colonnes clairs
2. Supprimez les colonnes inutiles avant analyse
3. Utilisez des unités cohérentes
4. Documentez vos choix

## Architecture du Projet

```
DataAnalyzer/
├── backend/                # Backend Python Flask
│   ├── app.py             # API principale
│   ├── analyses/          # Modules d'analyse
│   │   ├── regression.py
│   │   ├── classification.py
│   │   ├── neural_networks.py
│   │   ├── time_series.py
│   │   ├── clustering.py
│   │   ├── data_cleaning.py
│   │   └── advanced_stats.py
│   ├── reports/           # Génération PDF
│   │   └── pdf_generator.py
│   └── requirements.txt   # Dépendances Python
│
├── src/                   # Frontend React
│   ├── components/        # Composants UI
│   ├── api/              # API calls
│   └── App.tsx           # App principale
│
└── README.md             # Documentation
```

## Support

Pour toute question :
1. Consultez les erreurs dans la console du navigateur (F12)
2. Vérifiez les logs du backend (terminal)
3. Relisez la section Dépannage du README
4. Vérifiez que toutes les dépendances sont installées

## Prochaines Étapes

Une fois familiarisé :
1. Explorez toutes les analyses disponibles
2. Testez avec vos propres données
3. Comparez différents algorithmes
4. Générez des rapports pour vos projets

Bon analyse ! 🎉
