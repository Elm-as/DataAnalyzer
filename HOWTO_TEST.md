# 🎯 GUIDE DÉMARRAGE RAPIDE - Version Intégrée

Tout est prêt ! Voici comment tester le système complet.

---

## ✅ Vérification Avant Démarrage

### 1. Vérifier que les modules Python sont installés
```bash
cd "c:\Users\elmas\Desktop\DataAnalyzer"
.\.venv\Scripts\python.exe -c "import pandas; import numpy; print('OK')"
```
Doit afficher: `OK`

### 2. Vérifier les fichiers créés
```bash
# Les fichiers suivants doivent exister:
ls src/utils/csvParser.ts
ls src/utils/dataValidator.ts
ls src/components/DataQualityReport.tsx
ls src/components/ColumnSelector.tsx
ls backend/utils/data_validator.py
```

### 3. Vérifier Node.js est installé
```bash
npm --version
node --version
```

---

## 🚀 LANCER L'APPLICATION

### Option 1: Scripts Windows (Recommandé)

**Terminal 1: Démarrer le Backend**
```bash
cd c:\Users\elmas\Desktop\DataAnalyzer
start-backend.bat
```

**Terminal 2: Démarrer le Frontend**
```bash
cd c:\Users\elmas\Desktop\DataAnalyzer
start-frontend.bat
```

Puis ouvrez: http://localhost:5173

---

### Option 2: Commande Manuelle

**Terminal 1: Backend**
```bash
cd c:\Users\elmas\Desktop\DataAnalyzer\backend
..\\.venv\Scripts\python.exe app.py
```

**Terminal 2: Frontend**
```bash
cd c:\Users\elmas\Desktop\DataAnalyzer
npm run dev
```

---

## 📋 TESTER AVEC disease_symptom_matrix.csv

### Étape 1: Upload du Fichier
1. Allez à http://localhost:5173
2. Cliquez sur **"Importer les données"**
3. Uploadez `disease_symptom_matrix.csv`
   - Fichier: 431 lignes × 1419 colonnes
   - Taille: ~5 MB

### Étape 2: Aperçu des Données
- Le système analyse automatiquement
- Montre les 10 premières lignes
- Détecte les types de colonnes

### Étape 3: Vérifier la Qualité (NOUVEAU!)
- Affiche un rapport détaillé
  - Complétude: 100%
  - N/A: 0%
  - Colonnes problématiques: 0
  - Suggestions: aucune

### Étape 4: Sélectionner Colonnes (NOUVEAU!)
- Liste des 1417 symptômes
- Bouton "✨ Meilleures colonnes" sélectionne automatiquement les 50 meilleures
- Réduction: **1419 → 52 colonnes**

### Étape 5: Configuration
- Vérifier que 52 colonnes sont sélectionnées
- Continuer

### Étape 6: Choisir Analyses
- Sélectionner des analyses
- Le système valide les features automatiquement

### Étape 7: Voir Résultats
- Les analyses s'exécutent
- Résultats affichés

---

## 🧪 TESTS EN LIGNE DE COMMANDE

### Tester le Parser CSV
```bash
cd c:\Users\elmas\Desktop\DataAnalyzer
.\.venv\Scripts\python.exe -c "
import pandas as pd
df = pd.read_csv('disease_symptom_matrix.csv')
print(f'Shape: {df.shape}')
print('OK: CSV charge sans crash')
"
```

### Tester la Validation
```bash
cd c:\Users\elmas\Desktop\DataAnalyzer
.\.venv\Scripts\python.exe test_improvements.py
```
**Résultat attendu**: 5/5 tests PASS

### Tester Complet avec 1419 Colonnes
```bash
cd c:\Users\elmas\Desktop\DataAnalyzer
.\.venv\Scripts\python.exe test_large_csv_complete.py
```
**Résultat attendu**: 
```
✅ Parser CSV (431 × 1419)
✅ Validation qualité
✅ Sélection colonnes (1419 → 52)
✅ Nettoyage données
✅ Endpoints backend
```

---

## 🔍 VÉRIFIER LES ENDPOINTS

### Tester /validate-data
```bash
$data = @{
    "data" = @(@{"col1"=1; "col2"=2})
    "columns" = @("col1", "col2")
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:5000/validate-data" `
    -Method POST -Body $data -ContentType "application/json"

Write-Host $response.Content
```

### Tester /validate-and-clean
```bash
$data = @{
    "data" = @(@{"col1"=1; "col2"=2})
    "config" = @{"remove_empty_columns"=$true}
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://localhost:5000/validate-and-clean" `
    -Method POST -Body $data -ContentType "application/json"

Write-Host $response.Content
```

---

## ✨ FONCTIONNALITÉS NOUVELLES

### 1. DataQualityReport Component
- Affiche les metrics de qualité globales
- Liste les colonnes problématiques
- Suggestions d'amélioration
- Bouton pour supprimer colonnes problématiques

### 2. ColumnSelector Component
- Trie les colonnes par qualité
- Bouton "✨ Meilleures colonnes" pour auto-sélection
- Recherche et filtrage
- Limite à 50 colonnes par défaut

### 3. Endpoints de Validation
- **POST /validate-data**: Valide la qualité
- **POST /validate-and-clean**: Nettoie automatiquement

### 4. Validation dans Analyses
- Régression: Valide features numériques
- Classification: Valide features et target

---

## 🐛 Troubleshooting

### "Le backend ne démarre pas"
```bash
# Vérifier Python
python --version

# Réinstallez les dépendances
pip install -r backend/requirements.txt
```

### "Module not found: dataValidator"
```bash
# Vérifier les fichiers existent
ls src/utils/dataValidator.ts
ls src/utils/csvParser.ts
```

### "Port 5000 ou 5173 déjà utilisé"
```bash
# Trouver le processus
netstat -ano | findstr :5000
netstat -ano | findstr :5173

# Tuer le processus
taskkill /PID <PID> /F
```

### "CORS error"
- Vérifier que backend et frontend tournent
- Vérifier que CORS est activé dans app.py

---

## 📞 Résumé Rapide

| Étape | Commande | Résultat |
|-------|----------|---------|
| Test Python | `test_improvements.py` | 5/5 PASS |
| Test Complet | `test_large_csv_complete.py` | 5/5 PASS |
| Lancer Backend | `python backend/app.py` | Port 5000 |
| Lancer Frontend | `npm run dev` | Port 5173 |
| Upload CSV | Browser 5173 | 1419 colonnes OK |
| Sélect Colonnes | Click "Meilleures" | 50 colonnes sélectionnées |
| Analyse | Choisir analyse | Résultats |

---

## ✅ CHECKLIST

- [ ] Python installé (3.10+)
- [ ] Node.js installé
- [ ] .venv créé avec dépendances
- [ ] Fichiers frontend créés (4 fichiers)
- [ ] Fichiers backend créés/modifiés (5 fichiers)
- [ ] Tests réussis (test_improvements.py)
- [ ] Tests réussis (test_large_csv_complete.py)
- [ ] Backend démarre (port 5000)
- [ ] Frontend démarre (port 5173)
- [ ] CSV 1419 colonnes uploade correctement
- [ ] Colonnes sélectionnées intelligemment
- [ ] Analyses s'exécutent sans erreur

---

## 🎉 Bravo!

Si vous avez suivi ce guide et tous les tests passent:
- ✅ Système complet pour CSV volumineux
- ✅ Validation automatique qualité
- ✅ Sélection intelligente colonnes
- ✅ Nettoyage données
- ✅ Messages d'erreur explicites

**Vous êtes prêt pour la production!** 🚀

---

*Guide créé: 9 décembre 2025*
*Tous les tests: 5/5 PASS ✅*
