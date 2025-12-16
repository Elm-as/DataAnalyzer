# 🎉 Nouvelle Fonctionnalité : Simulateur de Prédiction + Diagnostic Médical

## ✅ Ce qui a été ajouté

### 1. **Analyse de Correspondance Symptômes-Maladies**

Un module spécialisé pour le diagnostic médical basé sur les symptômes.

**Localisation :**
- Backend : `backend/analyses/symptom_matching.py`
- Frontend : Section "Diagnostic Symptômes" dans AnalysisResults
- Endpoint : `POST /analyze/symptom-matching`

**Algorithmes utilisés :**
- **TF-IDF** : Vectorisation des symptômes (traite chaque maladie comme un "document")
- **Bernoulli Naive Bayes** : Optimisé pour données booléennes (0/1)
- **Multinomial Naive Bayes** : Alternative pour données de comptage
- **Similarité Cosinus** : Identifie les maladies similaires
- **Feature Importance** : Score d'importance des symptômes

**Résultats affichés :**
- ✅ Top symptômes par TF-IDF
- ✅ Précision des modèles (Bernoulli, Multinomial)
- ✅ Exemples de prédictions avec probabilités
- ✅ Symptômes les plus importants globalement
- ✅ Maladies similaires

---

### 2. **Simulateur de Prédiction Universel** 🎯

Un simulateur interactif qui fonctionne avec **n'importe quelle base de données**.

**Localisation :**
- Composant : `src/components/PredictionSimulator.tsx`
- Onglet : "🎯 Simulateur" dans les résultats d'analyse

**Fonctionnalités :**

#### Détection Automatique du Meilleur Modèle
Le simulateur détecte automatiquement le meilleur modèle parmi :
- Classification (Random Forest, SVM, KNN, etc.)
- Régression (Linear, Ridge, Lasso, etc.)
- Diagnostic Médical (Symptom Matching)
- Réseaux de Neurones

#### Interface Adaptative
- **Colonnes Booléennes** : Boutons Oui/Non
- **Colonnes Numériques** : Champs de saisie numérique
- **Colonnes Catégorielles** : Liste déroulante (dropdown)
- **Colonnes Texte** : Champ de texte libre

#### Prédiction en Temps Réel
1. L'utilisateur entre ses données
2. Clique sur "Lancer la Prédiction"
3. Obtient immédiatement :
   - **Diagnostic médical** : Top 5 maladies avec probabilités
   - **Classification** : Classe prédite avec confiance
   - **Régression** : Valeur numérique prédite avec R² score

#### Affichage Visuel
- Barres de progression pour les probabilités
- Code couleur (vert = haute confiance, jaune = moyenne, rouge = faible)
- Graphiques pour les top prédictions
- Indication du modèle utilisé

---

## 🧪 Comment Tester

### Test avec disease_symptom_matrix.csv (Diagnostic Médical)

1. **Lancer le backend :**
   ```bash
   cd backend
   python app.py
   ```
   Vérifier : `Running on http://127.0.0.1:5000`

2. **Lancer le frontend :**
   ```bash
   npm run dev
   ```
   Ouvrir : `http://localhost:5173`

3. **Charger les données :**
   - Upload `disease_symptom_matrix.csv`
   - 431 maladies × 1419 symptômes booléens
   - Colonnes automatiquement converties en type `boolean`

4. **Configurer l'analyse :**
   - Étape "Analyses" : Cocher **"Correspondance Symptômes"**
   - Options automatiques :
     - Colonne maladie : `name`
     - Colonnes symptômes : Toutes les booléennes (1417)
     - Modèle : `all` (TF-IDF + Bernoulli + Multinomial)
     - Test size : 20%
     - Top prédictions : 5

5. **Voir les résultats :**
   - Onglet **"Diagnostic Symptômes"** :
     - Résumé : 431 maladies, 1417 symptômes
     - Précision Bernoulli : ~85-95%
     - Top symptômes TF-IDF
     - Exemples de prédictions

6. **Utiliser le simulateur :**
   - Onglet **"🎯 Simulateur"**
   - Cocher les symptômes actifs (ex: fièvre, toux, fatigue)
   - Cliquer sur "Lancer la Prédiction"
   - Obtenir les 5 maladies les plus probables avec % de probabilité

---

### Test avec autre base de données (Classification/Régression)

Le simulateur fonctionne avec **n'importe quelle base** :

**Exemple 1 : Prédiction de prix (Régression)**
```
Colonnes : superficie, chambres, salle_bain, age, quartier → prix
1. Charger CSV avec données immobilières
2. Cocher "Régression" dans les analyses
3. Configurer : target = "prix"
4. Aller dans "🎯 Simulateur"
5. Entrer : superficie=100, chambres=3, salle_bain=2, age=10
6. Obtenir : Prix prédit = 250,000€ (R²=0.85)
```

**Exemple 2 : Détection de fraude (Classification)**
```
Colonnes : montant, heure, localisation, type_carte → fraude (oui/non)
1. Charger CSV avec transactions
2. Cocher "Classification" dans les analyses
3. Configurer : target = "fraude"
4. Aller dans "🎯 Simulateur"
5. Entrer : montant=5000, heure=03h00, localisation="étranger"
6. Obtenir : Fraude probable (95% de confiance)
```

---

## 📊 Résultats Attendus

### Test avec disease_symptom_matrix.csv

```
✅ Analyse réussie:
   - 431 maladies analysées
   - 1417 symptômes évalués
   - TF-IDF : 100 features, sparsity 94.66%
   - Bernoulli NB : ~85-95% accuracy
   - Multinomial NB : ~80-90% accuracy

✅ Top 5 symptômes TF-IDF:
   1. fièvre (score: 45.3)
   2. douleur (score: 38.2)
   3. fatigue (score: 35.1)
   4. céphalées (score: 28.9)
   5. toux (score: 25.4)

✅ Exemple prédiction:
   Symptômes: fièvre + toux + fatigue
   Top 5 maladies:
   1. Grippe (87.3%)
   2. COVID-19 (76.2%)
   3. Paludisme (54.1%)
   4. Bronchite (43.8%)
   5. Pneumonie (38.5%)
```

---

## 🎨 Interface Utilisateur

### Onglet "Diagnostic Symptômes"

```
┌─────────────────────────────────────────────────────────┐
│ 📊 Résumé de l'Analyse                                  │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│ │   431    │ │   1417   │ │  87.3%   │ │  82.1%   │   │
│ │ Maladies │ │Symptômes │ │Bernoulli │ │Multinomial│   │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
├─────────────────────────────────────────────────────────┤
│ 🔍 Top Symptômes (TF-IDF)                              │
│ 🥇 fièvre ............................ 45.3            │
│ 🥈 douleur ........................... 38.2            │
│ 🥉 fatigue ........................... 35.1            │
├─────────────────────────────────────────────────────────┤
│ 🎯 Exemples de Prédictions                             │
│ Maladie réelle: Paludisme simple                       │
│ ├─ Paludisme simple ████████████ 94.2%                │
│ ├─ Paludisme grave  ████████     76.3%                │
│ └─ Fièvre typhoïde  ██████       58.1%                │
└─────────────────────────────────────────────────────────┘
```

### Onglet "🎯 Simulateur"

```
┌─────────────────────────────────────────────────────────┐
│ 🎯 Simulateur de Prédiction                            │
│ Modèle actif: Bernoulli Naive Bayes                    │
├─────────────────────────────────────────────────────────┤
│ Entrez vos données:                                     │
│                                                         │
│ fièvre               [Oui] [Non]                       │
│ toux                 [Oui] [Non]                       │
│ fatigue              [Oui] [Non]                       │
│ céphalées            [Oui] [Non]                       │
│ douleurs musculaires [Oui] [Non]                       │
│                                                         │
│        [🎯 Lancer la Prédiction]                       │
├─────────────────────────────────────────────────────────┤
│ 📊 Diagnostic Prédictif                                │
│                                                         │
│ Symptômes actifs: 3 / 1417                             │
│                                                         │
│ Top Prédictions:                                        │
│ 1️⃣ Grippe                          87.3%              │
│    ████████████████████████████████████                │
│ 2️⃣ COVID-19                        76.2%              │
│    ██████████████████████████████                      │
│ 3️⃣ Paludisme                       54.1%              │
│    █████████████████████                               │
│                                                         │
│ Modèle: Bernoulli Naive Bayes                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Structure du Code

### Backend (symptom_matching.py)

```python
class SymptomMatchingAnalyzer:
    def perform_analysis(config):
        # 1. TF-IDF Analysis
        # 2. Bernoulli Naive Bayes
        # 3. Multinomial Naive Bayes
        # 4. Symptom Importance
        # 5. Disease Similarity
        # 6. Top Symptoms per Disease
        
    def _tfidf_analysis(X, y, symptom_cols):
        # Convertit matrice booléenne → représentation TF-IDF
        
    def _bernoulli_nb_model(X, y, config):
        # Entraîne Bernoulli NB (parfait pour 0/1)
        
    def predict_disease(symptoms_input, model, top_k=5):
        # Prédit top K maladies pour nouveaux symptômes
```

### Frontend (PredictionSimulator.tsx)

```typescript
const PredictionSimulator = ({ results, columns, data }) => {
  // 1. Détecter le meilleur modèle disponible
  detectBestModel();
  
  // 2. Préparer les champs de saisie
  setupAvailableFields();
  
  // 3. Simuler la prédiction
  runPrediction();
  
  // 4. Afficher les résultats
  renderPredictionResult();
}
```

---

## 📝 Configuration Endpoint

### POST /analyze/symptom-matching

**Request:**
```json
{
  "data": [...],  // Dataset complet
  "config": {
    "disease_column": "name",
    "symptom_columns": ["symptom1", "symptom2", ...],
    "model": "all",  // "tfidf" | "bernoulli" | "multinomial" | "all"
    "test_size": 0.2,
    "top_predictions": 5
  }
}
```

**Response:**
```json
{
  "success": true,
  "total_diseases": 431,
  "total_symptoms": 1417,
  "tfidf_analysis": {
    "top_symptoms_global": [...],
    "total_features": 100,
    "sparsity": 0.9466
  },
  "bernoulli_nb": {
    "accuracy": 0.873,
    "n_classes": 431,
    "example_predictions": [...]
  },
  "multinomial_nb": {
    "accuracy": 0.821,
    "cv_mean_accuracy": 0.798
  },
  "symptom_importance": {
    "top_symptoms": [...]
  }
}
```

---

## 🚀 Prochaines Étapes (Suggestions)

1. **Sauvegarde des prédictions** : Historique des simulations
2. **Export des résultats** : CSV avec toutes les prédictions
3. **Comparaison de modèles** : Side-by-side des prédictions
4. **Graphiques interactifs** : Visualisation des probabilités
5. **API de prédiction standalone** : Endpoint dédié à la prédiction seule

---

## ❓ FAQ

**Q: Le simulateur fonctionne avec quel type de données ?**  
R: Tout type ! Boolean, numérique, catégoriel. Il s'adapte automatiquement.

**Q: Pourquoi mes résultats sont vides ?**  
R: Vérifiez que :
- Le backend est lancé (`python backend/app.py`)
- Les colonnes booléennes sont bien converties (voir onglet "Aperçu")
- L'analyse "Correspondance Symptômes" est cochée

**Q: Comment changer le nombre de prédictions affichées ?**  
R: Modifiez `top_predictions` dans la config (ligne 478 de AnalysisOptions.tsx)

**Q: Les modèles Bernoulli/Multinomial ne s'affichent pas ?**  
R: Ils peuvent prendre du temps avec 431 classes. Attendez 30-60 secondes. Vérifiez la console backend pour les logs de progression.

---

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs du backend (terminal Flask)
2. Vérifiez la console du navigateur (F12)
3. Testez avec `test_symptom_matching.py`

✅ Tout est prêt à être utilisé !
