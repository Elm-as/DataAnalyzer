# Détection et Conversion Automatique de Types

## 📋 Vue d'ensemble

Le système DataAnalyzer détecte et convertit maintenant **automatiquement** les colonnes booléennes (0/1, true/false, oui/non) après l'import de données.

## ✨ Fonctionnalités

### 1. Détection Automatique (Backend + Frontend)

**Après l'upload du CSV :**
- ✅ Détection automatique des colonnes avec valeurs 0/1
- ✅ Conversion en type `boolean` (true/false)
- ✅ Fonctionne avec 1000+ colonnes sans problème
- ✅ Message de confirmation affiché

**Formats détectés :**
- `0` / `1` (entiers)
- `0.0` / `1.0` (flottants)
- `'0'` / `'1'` (chaînes)
- `true` / `false` (booléens)
- `'true'` / `'false'` (chaînes)
- `yes` / `no` (anglais)
- `oui` / `non` (français)

**Seuil de détection :** 95% des valeurs doivent correspondre au pattern

### 2. Conversion Manuelle (Interface)

**Bouton "Convertir les types" dans DataPreview :**
- 🎯 Sélectionner manuellement les colonnes à convertir
- 🔄 Choisir le type cible (booléen, numérique, texte, date, catégorielle)
- 📊 Prévisualiser les valeurs avant conversion
- ✅ Appliquer la conversion en un clic

**Types disponibles :**
1. **Booléen** (✓) - true/false, 0/1, oui/non
2. **Numérique** (🔢) - Nombres entiers ou décimaux
3. **Texte** (📝) - Chaîne de caractères
4. **Date** (📅) - Date et heure
5. **Catégorielle** (🏷️) - Valeurs discrètes

## 🔧 Architecture Technique

### Backend (`backend/utils/data_validator.py`)

**Classe BooleanDetector :**
```python
class BooleanDetector:
    @staticmethod
    def detect_boolean_columns(df: pd.DataFrame) -> Dict[str, bool]:
        """Détecte toutes les colonnes booléennes dans un DataFrame"""
        
    @staticmethod
    def convert_to_boolean(df: pd.DataFrame, column: str) -> pd.Series:
        """Convertit une colonne en type boolean"""
        
    @staticmethod
    def auto_convert_booleans(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, bool]]:
        """Détecte ET convertit automatiquement toutes les colonnes booléennes"""
```

**Endpoint API :**
```
POST /detect-booleans
Body: { "data": [...] }
Response: {
  "data": [...],                    // Données converties
  "boolean_columns": ["col1", ...], // Liste des colonnes booléennes
  "converted_count": 1417,          // Nombre de colonnes converties
  "conversion_report": {...},       // Détails de conversion
  "quality_after_conversion": {...}, // Qualité après conversion
  "message": "..."                  // Message de confirmation
}
```

### Frontend

**Composants créés/modifiés :**

1. **TypeConverter.tsx** (NOUVEAU)
   - Modal de conversion manuelle
   - Sélection multi-colonnes
   - Choix du type cible
   - Aperçu des valeurs

2. **DataPreview.tsx** (MODIFIÉ)
   - Appel automatique à `/detect-booleans` après détection initiale
   - Bouton "Convertir les types" pour conversion manuelle
   - Badge de confirmation de détection automatique
   - Mise à jour automatique des données et colonnes

3. **backend.ts** (MODIFIÉ)
   - Nouvelle fonction `detectBooleans(data)`

**Workflow :**
```
1. Upload CSV
   ↓
2. DataPreview - Détection initiale (frontend)
   ↓
3. Détection automatique booléens (backend)
   ↓
4. Conversion automatique si colonnes détectées
   ↓
5. (Optionnel) Conversion manuelle via bouton
   ↓
6. Configuration et analyse
```

## 📊 Tests

### Test Automatique

**Fichier:** `test_bool_simple.py`

**Résultats avec disease_symptom_matrix.csv (1419 colonnes) :**
```
✅ 1417 colonnes booléennes détectées
✅ Types convertis: int64 → bool
✅ 2 colonnes object (id, name) inchangées
```

**Commande :**
```bash
python test_bool_simple.py
```

### Test Complet

**Fichier:** `test_boolean_detection.py`

**Tests inclus :**
- Détection de colonnes booléennes
- Conversion automatique
- Validation de la qualité
- Test de l'endpoint `/detect-booleans`

**Commande :**
```bash
python test_boolean_detection.py
```

## 🎯 Cas d'usage

### 1. Dataset médical (disease_symptom_matrix.csv)
- **Problème :** 1417 colonnes de symptômes codées 0/1 traitées comme numériques
- **Solution :** Détection automatique + conversion en boolean
- **Résultat :** Types corrects, analyses adaptées aux données booléennes

### 2. Données de sondage (Oui/Non)
- **Problème :** Réponses texte "oui"/"non" non reconnues comme booléennes
- **Solution :** Détection frontend + backend reconnaît les patterns français
- **Résultat :** Conversion automatique en true/false

### 3. Flags techniques (0/1)
- **Problème :** Colonnes de flags (is_active, has_feature) en int
- **Solution :** Détection automatique dès l'upload
- **Résultat :** Types booléens dès le preview

## 🚀 Utilisation

### Automatique (Recommandé)

1. Uploader un fichier CSV
2. Attendre la détection automatique (badge vert s'affiche)
3. Vérifier les types dans le résumé (carte "Booléennes")
4. Continuer le workflow normalement

### Manuelle (Si nécessaire)

1. Dans DataPreview, cliquer sur **"Convertir les types"**
2. Sélectionner les colonnes à convertir (checkbox)
3. Choisir le type cible pour chaque colonne
4. Cliquer sur **"Convertir (X)"**
5. Les données et types sont mis à jour immédiatement

## 🔍 Indicateurs Visuels

**Dans DataPreview :**
- 🔄 Animation "Détection automatique des colonnes booléennes..."
- ✅ Badge vert "X colonnes booléennes détectées et converties"
- 🟣 Badge "Booléennes" dans le résumé (grille de 5 cartes)
- 🪄 Bouton violet "Convertir les types"

**Dans la table :**
- Icône ✓ pour les colonnes booléennes
- Badge violet "boolean"
- ✅ Checkmark vert si colonne sélectionnée

## ⚙️ Configuration

**Seuil de détection (dataValidator.ts) :**
```typescript
if (booleanCount / nonNullValues.length > 0.95) {
  type = 'boolean';
}
```

**Modifier le seuil :** Changer `0.95` (95%) à une autre valeur (ex: `0.90` pour 90%)

**Patterns personnalisés :** Ajouter dans `BooleanDetector.detect_boolean_columns()` :
```python
valid_values = [0, 1, True, False, '0', '1', 'true', 'false', 
                'yes', 'no', 'oui', 'non', 
                'Y', 'N']  # Ajouter ici
```

## 📈 Performance

**Tests effectués :**
- ✅ 431 lignes × 1419 colonnes (disease_symptom_matrix.csv)
- ✅ Détection en < 2 secondes
- ✅ Conversion en < 1 seconde
- ✅ Pas de ralentissement du frontend

**Optimisations :**
- Détection une seule fois (flag `autoDetectionDone`)
- Conversion backend (pandas plus rapide que JS)
- Mise à jour locale des données (pas de reload)

## 🐛 Dépannage

### Problème : Colonnes booléennes non détectées

**Causes possibles :**
1. Seuil 95% non atteint (valeurs mixtes)
2. Format non reconnu (ex: "Vrai"/"Faux")
3. Backend non lancé

**Solutions :**
1. Utiliser la conversion manuelle
2. Abaisser le seuil dans `dataValidator.ts`
3. Ajouter le format dans `BooleanDetector`

### Problème : Erreur "Cannot read property 'data'"

**Cause :** Backend non démarré ou endpoint `/detect-booleans` non disponible

**Solution :**
```bash
cd backend
python app.py
```

### Problème : Types ne changent pas après conversion

**Cause :** App.tsx ne reçoit pas les données mises à jour

**Solution :** Vérifier que `onDataUpdated` est appelé dans DataPreview

## 📚 Références

**Fichiers créés :**
- `src/components/TypeConverter.tsx` - Composant de conversion manuelle
- `test_bool_simple.py` - Test simple de détection
- `test_boolean_detection.py` - Suite de tests complète

**Fichiers modifiés :**
- `backend/utils/data_validator.py` - Classe BooleanDetector
- `backend/app.py` - Endpoint /detect-booleans
- `src/components/DataPreview.tsx` - Détection auto + bouton
- `src/api/backend.ts` - Fonction detectBooleans
- `src/App.tsx` - Gestion des données mises à jour

**Standards respectés :**
- RFC 4180 (CSV parsing)
- TypeScript strict mode
- React best practices
- Flask REST API conventions
