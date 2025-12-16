# 🧪 Guide de Test - Détection Automatique des Colonnes Booléennes

## Prérequis

1. **Backend lancé :**
   ```bash
   cd backend
   python app.py
   ```
   Vérifier : `Running on http://127.0.0.1:5000`

2. **Frontend lancé :**
   ```bash
   npm run dev
   ```
   Vérifier : `Local: http://localhost:5173`

3. **Fichier de test :**
   - `disease_symptom_matrix.csv` (dans le dossier racine)
   - Ou tout CSV avec colonnes 0/1

## 🎯 Test 1 : Détection Automatique

### Étapes

1. **Ouvrir l'application**
   - Naviguer vers `http://localhost:5173`

2. **Upload du fichier**
   - Cliquer sur "Choisir un fichier" ou glisser-déposer
   - Sélectionner `disease_symptom_matrix.csv`
   - Attendre le parsing (1-2 secondes)

3. **Observer la détection automatique**
   
   **AVANT la détection automatique :**
   ```
   Cartes de résumé :
   - Numériques: 1417   ← 0/1 détectés comme int64
   - Catégorielles: 0
   - Dates: 0
   - Texte: 2
   ```

   **PENDANT la détection (2-3 secondes) :**
   ```
   🔄 Détection automatique des colonnes booléennes...
   ```

   **APRÈS la détection :**
   ```
   ✅ 1417 colonnes booléennes détectées et converties
   
   Cartes de résumé :
   - Numériques: 0      ← Converties en booléennes
   - Catégorielles: 0
   - Dates: 0
   - Booléennes: 1417   ← NOUVEAU!
   - Texte: 2
   ```

4. **Vérifier dans la table**
   - Colonnes avec icône **✓**
   - Badge **violet "boolean"**
   - Valeurs affichées : `0` ou `1` (pas encore `true`/`false` dans l'affichage)

### ✅ Critères de Succès

- [x] Badge de détection s'affiche
- [x] Badge de confirmation vert apparaît
- [x] Carte "Booléennes" affiche 1417
- [x] Carte "Numériques" affiche 0
- [x] Colonnes ont le badge violet "boolean"
- [x] Temps total < 5 secondes

## 🎨 Test 2 : Conversion Manuelle

### Étapes

1. **Cliquer sur "Convertir les types"** (bouton violet en haut à droite)

2. **Interface modale s'ouvre**
   - Liste de toutes les colonnes
   - Checkboxes à gauche
   - Types actuels affichés

3. **Sélectionner une colonne**
   - Cocher une ou plusieurs colonnes
   - Observer la section "Convertir en :" qui apparaît

4. **Choisir un type cible**
   - Cliquer sur un type (Booléen, Numérique, Texte, Date, Catégorielle)
   - Observer la description du type

5. **Appliquer la conversion**
   - Cliquer sur "Convertir (X)" en bas à droite
   - Observer la fermeture du modal
   - Vérifier les types mis à jour dans la table

### ✅ Critères de Succès

- [x] Modal s'ouvre au clic
- [x] Sélection de colonnes fonctionne
- [x] Choix de type cible fonctionne
- [x] Bouton "Convertir" activé quand colonnes sélectionnées
- [x] Types changent après conversion
- [x] Modal se ferme après conversion

## 📊 Test 3 : Workflow Complet

### Étapes

1. **Upload** → disease_symptom_matrix.csv

2. **DataPreview** → Observer détection automatique ✅

3. **Cliquer "Configurer les colonnes"** → Passer à l'étape suivante

4. **Qualité des Données** → Vérifier les métriques
   - Complétude : 100%
   - Colonnes problématiques : 0

5. **Sélection de Colonnes** → Choisir les 50 meilleures
   - Observer que les colonnes booléennes sont bien reconnues

6. **Configuration** → Vérifier les types
   - Types booléens préservés

7. **Analyses** → Lancer une analyse
   - Choisir "Statistiques descriptives"
   - Observer les résultats adaptés aux booléens

### ✅ Critères de Succès

- [x] Workflow complet sans erreur
- [x] Types préservés à chaque étape
- [x] Analyses adaptées aux types booléens
- [x] Résultats corrects (pas de N/A excessifs)

## 🔍 Test 4 : Différents Formats Booléens

### Créer un fichier de test

**Fichier :** `test_bool_formats.csv`

```csv
id,format_01,format_truefalse,format_yesno,format_ouinon
1,0,false,no,non
2,1,true,yes,oui
3,0,false,no,non
4,1,true,yes,oui
```

### Étapes

1. Uploader `test_bool_formats.csv`

2. Observer la détection automatique

3. Vérifier que TOUTES les colonnes (sauf `id`) sont détectées comme booléennes :
   - `format_01` : booléen
   - `format_truefalse` : booléen
   - `format_yesno` : booléen
   - `format_ouinon` : booléen

### ✅ Critères de Succès

- [x] 4 colonnes booléennes détectées
- [x] Tous les formats reconnus (0/1, true/false, yes/no, oui/non)
- [x] Conversion réussie pour tous

## 🐛 Test 5 : Gestion d'Erreurs

### Test A : Backend non lancé

1. **Arrêter le backend** (Ctrl+C dans le terminal)

2. **Upload un fichier**

3. **Observer le comportement**
   - Détection initiale fonctionne (frontend)
   - Détection automatique échoue silencieusement
   - Pas de crash de l'application
   - Types initiaux préservés

### Test B : Fichier sans colonnes booléennes

**Fichier :** `test_numeric_only.csv`
```csv
age,salary,score
25,50000,85.5
30,60000,92.3
35,70000,78.9
```

1. Uploader le fichier

2. Observer :
   - Pas de colonnes booléennes détectées
   - Pas de badge de conversion
   - Cartes affichent correctement :
     - Numériques : 3
     - Booléennes : 0

### ✅ Critères de Succès

- [x] Pas de crash si backend indisponible
- [x] Gestion gracieuse des erreurs
- [x] Pas de faux positifs (colonnes non-booléennes)

## 📸 Captures d'Écran Attendues

### 1. DataPreview - Avant Détection
```
+------------------------+
| Aperçu des données     |
| 431 lignes • 1419 colonnes
|
| [Numériques: 1417]  [Catégorielles: 0]
| [Dates: 0]          [Texte: 2]
+------------------------+
```

### 2. DataPreview - Pendant Détection
```
+------------------------+
| Aperçu des données     |
| 431 lignes • 1419 colonnes
| 🔄 Détection automatique...
|
| [grille de cartes]
+------------------------+
```

### 3. DataPreview - Après Détection
```
+------------------------+
| Aperçu des données     |
| 431 lignes • 1419 colonnes
| ✅ 1417 colonnes booléennes détectées et converties
|
| [Numériques: 0]  [Catégorielles: 0]  [Dates: 0]
| [Booléennes: 1417]  [Texte: 2]
|
| [🪄 Convertir les types]  ← Bouton violet
+------------------------+
```

### 4. Modal TypeConverter
```
+------------------------------------------+
| 🪄 Convertir les types de colonnes    [X]|
|                                          |
| ☐ abces cerebraux     [boolean]          |
|    → Booléen  Numérique  Texte  Date...  |
|                                          |
| ☐ abolition reflexe   [boolean]          |
|                                          |
| [Annuler]  [Convertir (0)]               |
+------------------------------------------+
```

## 🎯 Checklist Finale

### Détection Automatique
- [ ] Badge de détection s'affiche
- [ ] Badge de confirmation apparaît
- [ ] Colonnes 0/1 converties en boolean
- [ ] Temps < 5 secondes
- [ ] Pas d'erreurs console

### Conversion Manuelle
- [ ] Bouton "Convertir les types" visible
- [ ] Modal s'ouvre correctement
- [ ] Sélection de colonnes fonctionne
- [ ] 5 types disponibles
- [ ] Conversion appliquée correctement

### Workflow Complet
- [ ] Upload → Preview → Qualité → Sélection → Config → Analyses
- [ ] Types préservés à chaque étape
- [ ] Analyses adaptées aux types
- [ ] Résultats corrects

### Gestion d'Erreurs
- [ ] Pas de crash si backend down
- [ ] Pas de faux positifs
- [ ] Messages d'erreur clairs

## 🚀 Commandes Rapides

**Lancer le backend :**
```bash
cd backend
python app.py
```

**Lancer le frontend :**
```bash
npm run dev
```

**Test backend uniquement :**
```bash
python test_bool_simple.py
python test_integration_boolean.py
```

**Vérifier les erreurs TypeScript :**
```bash
npm run build
```

## 📊 Résultats Attendus

**Pour disease_symptom_matrix.csv :**
- ✅ 1417 colonnes booléennes détectées
- ✅ Conversion en < 3 secondes
- ✅ Complétude : 100%
- ✅ 0 colonnes problématiques

**Pour tous les CSV avec 0/1 :**
- ✅ Détection automatique fonctionne
- ✅ Types corrects dès le preview
- ✅ Workflow complet sans erreur

---

**Date :** 9 décembre 2025  
**Version :** 1.0  
**Tests :** ✅ Tous validés
