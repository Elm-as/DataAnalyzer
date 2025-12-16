# 🧪 GUIDE DE TEST RAPIDE - Simulateur ML

## ⚡ Test en 5 Minutes

### 1️⃣ Lancer le Backend (Terminal 1)
```powershell
cd backend
python app.py
```

**Vérifier**: Doit afficher `Running on http://127.0.0.1:5000`

---

### 2️⃣ Lancer le Frontend (Terminal 2)
```powershell
npm run dev
```

**Vérifier**: Doit afficher `Local: http://localhost:5173`

---

### 3️⃣ Ouvrir l'Application
- Navigateur: `http://localhost:5173`
- Uploader `disease_symptom_matrix.csv`

---

### 4️⃣ Lancer l'Analyse "Correspondance Donnees"

**IMPORTANT** ⚠️
1. Sélectionner "Correspondance Donnees"
2. Cliquer "Options avancées"
3. **Modèle**: Choisir `all` ou `bernoulli`
4. Cliquer "Lancer l'analyse"
5. Attendre (~15 secondes)

**Vérifier dans la console backend**:
```
[BERNOULLI] Modele Bernoulli Naive Bayes...
[WARNING] Beaucoup de classes (428) pour peu de samples (431)
[INFO] Entraînement du modèle sans validation
```

---

### 5️⃣ Aller dans le Simulateur
- Cliquer sur l'onglet "Simulateur"
- Voir: "Modele actif: correspondance"

---

### 6️⃣ Remplir les Symptômes

**Option A - Remplissage automatique** (RECOMMANDÉ):
1. Cliquer "Remplir Automatiquement"
2. Ou "Cas Typique"

**Option B - Manuel**:
1. Chercher "fievre" → Cocher les cases
2. Chercher "fatigue" → Cocher
3. Chercher "cephalee" → Cocher

---

### 7️⃣ Lancer la Prédiction
1. Cliquer "Lancer la Prediction"
2. Attendre (~1 seconde)

---

### 8️⃣ Vérifier les Résultats

**Vous devez voir**:
```
Diagnostic le plus probable
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Mononucléose infectieuse
94.7% de confiance
[████████████████████░░] 94.7%

Modèle utilisé: Modèle Prédictif ML (Bernoulli Naive Bayes)

Autres diagnostics possibles:
• Mucoviscidose - 3.7%
• Maladie de Hirschsprung - 1.6%
• Maladie des griffes du chat - 0.0%
• Paludisme simple - 0.0%
```

**Si vous voyez des probabilités comme 94.7%, 3.7%, etc. → ✅ C'EST BON !**

---

## 🔍 Vérifications Backend

### Console Backend (Terminal 1)

**Lors de l'analyse**:
```
[BACKEND] Analyzer stocké pour dataset default
  - Modèle: <class 'sklearn.naive_bayes.BernoulliNB'>
  - Features: 1417
  - Classes: 428
```

**Lors de la prédiction**:
```
[PREDICT] Prédiction pour dataset default
  - X_test shape: (1, 1417)
  - Features fournies: 38/1417
  - Valeurs non-nulles: 38
  - Top prédiction: {'class': 'Mononucléose infectieuse', 'probability': 0.9474}
```

✅ **Si vous voyez ces messages → Tout fonctionne !**

---

## ❌ Problèmes Courants

### Problème 1: "Aucun modèle entraîné"
**Cause**: L'analyse n'a pas été lancée avec `model='all'` ou `model='bernoulli'`

**Solution**:
1. Relancer l'analyse "Correspondance Donnees"
2. Options avancées → Modèle: `all`

---

### Problème 2: "Aucune maladie ne correspond"
**Cause**: Aucun symptôme sélectionné

**Solution**:
1. Cliquer "Remplir Automatiquement"
2. Ou cocher manuellement des cases

---

### Problème 3: Backend pas lancé
**Erreur**: `Erreur de connexion à l'API`

**Solution**:
```powershell
cd backend
python app.py
```

---

### Problème 4: Scores tous identiques (33%, 33%, 33%)
**Cause**: Ancien code (comptage) utilisé au lieu de ML

**Solution**:
1. Vérifier que le build est à jour:
   ```powershell
   npm run build
   ```
2. Relancer `npm run dev`
3. F5 dans le navigateur

---

## 🧪 Test Python (Sans Frontend)

Si vous voulez tester juste le backend:

```powershell
python test_ml_prediction.py
```

**Résultat attendu**:
```
Top 5 Prédictions:
1. Mononucléose infectieuse: 94.74%
2. Mucoviscidose: 3.70%
3. Maladie de Hirschsprung: 1.56%
...
✅ Tout fonctionne !
```

---

## 📊 Différence AVANT/APRÈS

### AVANT (Comptage)
```
Paludisme: 33%
Grippe: 33%
COVID-19: 33%
❌ Scores identiques
```

### APRÈS (ML)
```
Mononucléose: 94.7%
Mucoviscidose: 3.7%
Hirschsprung: 1.6%
✅ Scores différenciés
```

**Si vous voyez des scores différenciés → Le ML fonctionne !** ✅

---

## 🎯 Checklist Finale

- [ ] Backend lancé (port 5000)
- [ ] Frontend lancé (port 5173)
- [ ] disease_symptom_matrix.csv uploadé
- [ ] Analyse "Correspondance Donnees" avec `model=all`
- [ ] Simulateur affiche "Modele actif: correspondance"
- [ ] Remplissage automatique cliqué
- [ ] Prédiction lancée
- [ ] Résultats affichent **94.7%** ou autre probabilité ML
- [ ] Console backend affiche `[PREDICT]` logs

**Si tout est coché → 🎉 Succès !**

---

## 💡 Astuce

Pour voir les logs backend en détail:

**Terminal backend**:
```python
# Dans backend/app.py, la fonction predict() affiche:
print(f"[PREDICT] Prédiction pour dataset {dataset_id}")
print(f"  - Top prédiction: {result['top_prediction']}")
```

**Vous devez voir**:
```
[PREDICT] Prédiction pour dataset default
  - X_test shape: (1, 1417)
  - Features fournies: 38/1417
  - Top prédiction: {'class': 'Mononucléose infectieuse', 'probability': 0.9474}
```

---

## 📞 Support

Si quelque chose ne fonctionne pas:

1. Vérifier les erreurs dans:
   - Console backend (Terminal 1)
   - Console navigateur (F12)
   - Console frontend (Terminal 2)

2. Fichiers à vérifier:
   - `backend/app.py` (endpoint /predict)
   - `src/components/PredictionSimulator.tsx` (simulatePrediction)

3. Relire `SIMULATEUR_V2_ML.md` pour les détails techniques

---

**Bonne chance ! 🚀**
