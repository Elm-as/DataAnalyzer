"""
Analyse de correspondance symptômes-maladies
Utilise TF-IDF, similarité cosinus et modèles probabilistes
Parfait pour diagnostic médical basé sur symptômes
"""
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')


class SymptomMatchingAnalyzer:
    """
    Analyseur spécialisé pour le matching symptômes → maladies
    Utilise TF-IDF et similarité pour recommandation de diagnostic
    """
    
    def __init__(self, df):
        self.df = df.copy()
        self.trained_model = None  # Modèle ML entraîné
        self.feature_names = None  # Noms des colonnes features
        self.target_column = None  # Nom de la colonne cible
        self.classes_ = None  # Classes possibles (maladies)
        
    def perform_analysis(self, config):
        """
        Effectue l'analyse de matching symptômes-maladies
        
        Config attendue:
        {
            'disease_column': 'name',  # Colonne avec nom de la maladie
            'id_column': 'id',  # Colonne ID (optionnel)
            'symptom_columns': [...],  # Liste des colonnes de symptômes (ou 'auto')
            'test_size': 0.2,
            'model': 'tfidf',  # 'tfidf', 'bernoulli', 'multinomial', 'all'
            'top_predictions': 5,  # Nombre de maladies à retourner
            'similarity_threshold': 0.3  # Seuil de similarité minimum
        }
        """
        results = {
            'success': False,
            'model_type': config.get('model', 'tfidf'),
            'disease_column': config.get('disease_column', 'name'),
            'total_diseases': 0,
            'total_symptoms': 0,
            'tfidf_analysis': None,
            'bernoulli_nb': None,
            'multinomial_nb': None,
            'symptom_importance': None,
            'disease_similarity': None,
            'top_symptoms_per_disease': None,
            'recommendations': None
        }
        
        try:
            disease_col = config.get('disease_column', 'name')
            id_col = config.get('id_column', 'id')
            
            print(f"\n[CONFIG] Configuration recue:")
            print(f"  - Disease column: {disease_col}")
            print(f"  - ID column: {id_col}")
            print(f"  - DataFrame shape: {self.df.shape}")
            print(f"  - DataFrame columns: {list(self.df.columns[:10])}... (total: {len(self.df.columns)})")
            
            # Identifier les colonnes de symptômes
            symptom_cols = config.get('symptom_columns', 'auto')
            # Convertir en liste si c'est un array/tuple
            if isinstance(symptom_cols, np.ndarray):
                symptom_cols = symptom_cols.tolist()
            elif isinstance(symptom_cols, tuple):
                symptom_cols = list(symptom_cols)
            
            # Si pas de symptom_cols spécifiées ou 'auto', les détecter
            if not isinstance(symptom_cols, list) or symptom_cols == 'auto':
                # Exclure id, name/disease_name, target, etc.
                exclude_cols = [disease_col, 'name']
                if id_col and id_col in self.df.columns:
                    exclude_cols.append(id_col)
                # Ajouter autres colonnes non-numériques au exclus
                for col in self.df.columns:
                    if col in exclude_cols:
                        continue
                    # Si la colonne n'est pas booléenne/numérique, l'exclure
                    try:
                        # Vérifier si on peut la convertir en nombres
                        pd.to_numeric(self.df[col], errors='coerce')
                        # Si on arrive ici, c'est convertible
                    except:
                        # C'est du texte, on l'exclut
                        if col not in exclude_cols:
                            exclude_cols.append(col)
                
                symptom_cols = [col for col in self.df.columns if col not in exclude_cols]
            
            print(f"  - Symptom columns detected: {len(symptom_cols)} colonnes")
            
            results['total_diseases'] = len(self.df)
            results['total_symptoms'] = len(symptom_cols)
            
            print(f"\n[ANALYSIS] Analyse de {results['total_diseases']} maladies avec {results['total_symptoms']} symptomes")
            
            # Extraire la matrice de symptômes (booléens)
            X = self.df[symptom_cols].values
            y = self.df[disease_col].values
            
            # Stocker pour prédictions ultérieures
            self.feature_names = symptom_cols
            self.target_column = disease_col
            
            print(f"  - X shape: {X.shape}, dtype: {X.dtype}")
            print(f"  - y shape: {y.shape}, unique values: {len(np.unique(y))}")
            
            # 1. Analyse TF-IDF
            if config.get('model') in ['tfidf', 'all']:
                print("\n[TFIDF] Analyse TF-IDF...")
                results['tfidf_analysis'] = self._tfidf_analysis(X, y, symptom_cols, disease_col)
            
            # 2. Modèle Bernoulli Naive Bayes (parfait pour données booléennes)
            if config.get('model') in ['bernoulli', 'all']:
                print("\n[BERNOULLI] Modele Bernoulli Naive Bayes...")
                results['bernoulli_nb'] = self._bernoulli_nb_model(X, y, config)
            
            # 3. Modèle Multinomial Naive Bayes
            if config.get('model') in ['multinomial', 'all']:
                print("\n[MULTINOMIAL] Modele Multinomial Naive Bayes...")
                results['multinomial_nb'] = self._multinomial_nb_model(X, y, config)
            
            # 4. Importance des symptômes
            print("\n[IMPORTANCE] Calcul de l'importance des symptomes...")
            results['symptom_importance'] = self._calculate_symptom_importance(X, symptom_cols)
            
            # 5. Similarité entre maladies
            print("\n[SIMILARITY] Calcul de la similarite entre maladies...")
            results['disease_similarity'] = self._calculate_disease_similarity(X, y, config)
            
            # 6. Top symptômes par maladie
            print("\n[TOPSYMPTOMS] Top symptomes par maladie...")
            results['top_symptoms_per_disease'] = self._top_symptoms_per_disease(
                self.df, symptom_cols, disease_col, top_n=10
            )
            
            results['success'] = True
            print("\n[SUCCESS] Analyse terminee avec succes!")
            
        except Exception as e:
            results['error'] = str(e)
            print(f"\n[ERROR] Erreur: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return results
    
    def _tfidf_analysis(self, X, y, symptom_cols, disease_col):
        """
        Analyse TF-IDF des symptômes/features
        Fonctionne avec tous types de données (booléenne, numérique, catégorique)
        """
        # Déterminer le type de données
        is_boolean = np.all((X == 0) | (X == 1) | (X == True) | (X == False))
        
        if is_boolean:
            # ✅ BOOLÉEN: Traiter directement comme matrice binaire
            symptom_frequency = X.sum(axis=0)  
            symptom_variance = X.var(axis=0)
        else:
            # ✅ NUMÉRIQUE/CATÉGORIQUE: Normaliser d'abord
            # Convertir en float et normaliser
            X_numeric = X.astype(float)
            # Normaliser entre 0 et 1
            X_min = np.nanmin(X_numeric, axis=0)
            X_max = np.nanmax(X_numeric, axis=0)
            X_normalized = np.zeros_like(X_numeric)
            for j in range(X_numeric.shape[1]):
                if X_max[j] > X_min[j]:
                    X_normalized[:, j] = (X_numeric[:, j] - X_min[j]) / (X_max[j] - X_min[j])
                else:
                    X_normalized[:, j] = 0
            
            # Fréquence = moyenne des valeurs normalisées
            symptom_frequency = X_normalized.mean(axis=0) * 100
            symptom_variance = X_normalized.var(axis=0)
        
        # Calcul des scores
        n_diseases = X.shape[0]
        tfidf_scores = []
        
        for j, symptom in enumerate(symptom_cols):
            freq = symptom_frequency[j]
            var = symptom_variance[j]
            # TF-IDF: fréquence × variance
            score = (freq / 100) * var * 100 if is_boolean else freq * var
            tfidf_scores.append({
                'symptom': str(symptom),
                'frequency': float(freq),
                'frequency_pct': round(float(freq), 2) if not is_boolean else round(100 * freq / n_diseases, 2),
                'variance': round(float(var), 4),
                'tfidf_score': round(float(score), 4)
            })
        
        # Trier par score TF-IDF
        tfidf_scores.sort(key=lambda x: x['tfidf_score'], reverse=True)
        
        return {
            'analysis_type': f'TF-IDF Analysis ({"Boolean" if is_boolean else "Numeric/Categorical"} Matrix)',
            'total_symptoms': len(symptom_cols),
            'total_diseases': X.shape[0],
            'top_symptoms_global': tfidf_scores[:20],
            'data_type': 'boolean' if is_boolean else 'numeric',
            'note': 'Importance des features basée sur fréquence et variance'
        }
    
    def _bernoulli_nb_model(self, X, y, config):
        """
        Bernoulli Naive Bayes - Parfait pour features binaires (0/1)
        Idéal pour symptômes booléens ou autres données binarisées
        """
        test_size = config.get('test_size', 0.2)
        n_classes = len(np.unique(y))
        
        if n_classes < 2:
            return {'error': 'Pas assez de classes differentes pour entrainer un modele'}
        
        # Convertir en données binaires si nécessaire
        X_binary = X.copy()
        is_boolean = np.all((X == 0) | (X == 1))
        
        if not is_boolean:
            # Binariser avec le seuil de la médiane par colonne
            for col in range(X_binary.shape[1]):
                col_median = np.median(X_binary[:, col])
                X_binary[:, col] = (X_binary[:, col] > col_median).astype(int)
        
        # Pour les datasets avec trop de classes uniques et peu d'echantillons,
        # on ne peut pas faire de split stratifié
        if n_classes > len(y) * 0.9:
            # Chaque classe a moins de 2 samples en moyenne
            # MAIS on entraîne quand même le modèle pour les prédictions !
            print(f"   [WARNING] Beaucoup de classes ({n_classes}) pour peu de samples ({len(y)})")
            print(f"   [INFO] Entraînement du modèle sans validation (pas de train/test split)")
            
            # Entraîner sur TOUTES les données (pas de split)
            X_binary = (X > 0).astype(int)
            model = BernoulliNB(alpha=1.0, fit_prior=True)
            model.fit(X_binary, y)
            
            # Sauvegarder le modèle pour prédictions futures
            self.trained_model = model
            self.classes_ = model.classes_
            
            return {
                'model_name': 'Bernoulli Naive Bayes',
                'note': 'Modèle entraîné sur toutes les données (pas de validation croisée)',
                'n_classes': n_classes,
                'n_samples': len(y),
                'accuracy': None,
                'train_samples': len(y),
                'test_samples': 0,
                'model_trained': True
            }
        
        # Split - attention à stratify avec bcp de classes et peu d'samples
        use_stratify = False
        if n_classes < len(y) / 2:  # Si assez de samples par classe
            use_stratify = True
        
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X_binary, y, test_size=test_size, random_state=42, 
                stratify=y if use_stratify else None
            )
        except ValueError as e:
            # Si split échoue, retourner erreur gracieusement
            return {
                'model_name': 'Bernoulli Naive Bayes',
                'note': f'Split echec: {str(e)}',
                'n_classes': n_classes,
                'n_samples': len(y),
                'accuracy': None
            }
        
        # Modèle Bernoulli
        model = BernoulliNB(alpha=1.0, fit_prior=True)
        model.fit(X_train, y_train)
        
        # Sauvegarder le modèle pour prédictions futures
        self.trained_model = model
        self.classes_ = model.classes_
        
        # Prédictions
        y_pred = model.predict(X_test)
        
        # Métriques
        accuracy = accuracy_score(y_test, y_pred)
        
        # Probabilités pour top prédictions
        y_proba = model.predict_proba(X_test)
        
        # Top prédictions sur quelques exemples
        top_k = config.get('top_predictions', 5)
        example_predictions = []
        for i in range(min(5, len(y_test))):
            top_indices = y_proba[i].argsort()[-top_k:][::-1]
            example_predictions.append({
                'true_disease': y_test[i],
                'top_predictions': [
                    {
                        'disease': model.classes_[idx],
                        'probability': round(float(y_proba[i][idx]), 4)
                    }
                    for idx in top_indices
                ]
            })
        
        return {
            'model_name': 'Bernoulli Naive Bayes',
            'accuracy': round(accuracy, 4),
            'test_size': test_size,
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'n_classes': len(model.classes_),
            'example_predictions': example_predictions,
            'class_distribution': {
                str(cls): int(np.sum(y_train == cls))
                for cls in model.classes_[:10]  # Top 10 classes
            }
        }
    
    def _multinomial_nb_model(self, X, y, config):
        """
        Multinomial Naive Bayes
        Fonctionne avec des comptages (0, 1, 2, ...)
        Pour données non-binaires, on normalise et scale
        """
        test_size = config.get('test_size', 0.2)
        n_classes = len(np.unique(y))
        
        if n_classes < 2:
            return {'error': 'Pas assez de classes differentes'}
        
        # Pour les datasets avec trop de classes uniques et peu d'echantillons,
        # on ne peut pas faire de validation croisée
        if n_classes > len(y) * 0.9:
            return {
                'model_name': 'Multinomial Naive Bayes',
                'note': 'Trop de classes uniques relatives aux echantillons - modele non applicable',
                'n_classes': n_classes,
                'n_samples': len(y),
                'accuracy': None
            }
        
        # Préparer les données pour Multinomial
        X_scaled = X.copy().astype(float)
        
        # Vérifier si déjà binaire/entière
        is_boolean = np.all((X_scaled == 0) | (X_scaled == 1))
        
        if not is_boolean:
            # Normaliser à [0, 1] puis scale en counts
            min_vals = np.min(X_scaled, axis=0)
            max_vals = np.max(X_scaled, axis=0)
            
            for col in range(X_scaled.shape[1]):
                if max_vals[col] - min_vals[col] > 0:
                    # Normaliser
                    X_scaled[:, col] = (X_scaled[:, col] - min_vals[col]) / (max_vals[col] - min_vals[col])
            
            # Multiplier par 100 pour avoir des "counts"
            X_scaled = np.round(X_scaled * 100).astype(int)
        
        # Split
        use_stratify = False
        if n_classes < len(y) / 2:
            use_stratify = True
        
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=test_size, random_state=42, 
                stratify=y if use_stratify else None
            )
        except ValueError as e:
            return {
                'model_name': 'Multinomial Naive Bayes',
                'note': f'Split echec: {str(e)}',
                'n_classes': n_classes,
                'n_samples': len(y),
                'accuracy': None
            }
        
        model = MultinomialNB(alpha=1.0, fit_prior=True)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train, y_train, cv=min(5, len(np.unique(y_train))))
        
        return {
            'model_name': 'Multinomial Naive Bayes',
            'accuracy': round(accuracy, 4),
            'cv_mean_accuracy': round(cv_scores.mean(), 4),
            'cv_std': round(cv_scores.std(), 4),
            'test_size': test_size,
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'n_classes': len(model.classes_)
        }
    
    def _calculate_symptom_importance(self, X, symptom_cols):
        """
        Calcule l'importance de chaque symptôme
        Basé sur la fréquence et la distribution
        """
        symptom_freq = X.sum(axis=0)
        symptom_variance = X.var(axis=0)
        n_diseases = X.shape[0]
        
        importance_scores = []
        for i, symptom in enumerate(symptom_cols):
            freq = symptom_freq[i]
            var = symptom_variance[i]
            importance = (freq / n_diseases) * var * 100
            
            importance_scores.append({
                'symptom': symptom,
                'frequency': int(freq),
                'frequency_pct': round(100 * freq / n_diseases, 2),
                'variance': round(float(var), 4),
                'importance_score': round(float(importance), 4)
            })
        
        # Trier par importance
        importance_scores.sort(key=lambda x: x['importance_score'], reverse=True)
        
        return {
            'top_symptoms': importance_scores[:20],
            'bottom_symptoms': importance_scores[-20:],
            'total_symptoms': len(symptom_cols),
            'analysis': 'Fréquence × Variance'
        }
    
    def _calculate_disease_similarity(self, X, y, config):
        """
        Calcule la similarité cosinus entre maladies
        Aide à identifier les maladies avec profils symptomatiques similaires
        """
        # Similarité cosinus
        similarity_matrix = cosine_similarity(X)
        
        # Top paires de maladies similaires
        similar_pairs = []
        for i in range(len(y)):
            for j in range(i+1, len(y)):
                sim_score = similarity_matrix[i][j]
                if sim_score > config.get('similarity_threshold', 0.3):
                    similar_pairs.append({
                        'disease_1': y[i],
                        'disease_2': y[j],
                        'similarity': round(float(sim_score), 4)
                    })
        
        # Trier par similarité
        similar_pairs.sort(key=lambda x: x['similarity'], reverse=True)
        
        return {
            'top_20_similar_pairs': similar_pairs[:20],
            'total_similar_pairs': len(similar_pairs),
            'similarity_threshold': config.get('similarity_threshold', 0.3),
            'matrix_shape': similarity_matrix.shape
        }
    
    def _top_symptoms_per_disease(self, df, symptom_cols, disease_col, top_n=10):
        """
        Pour chaque maladie, liste les top symptômes les plus fréquents
        """
        disease_profiles = []
        
        for disease in df[disease_col].unique()[:20]:  # Top 20 maladies
            disease_data = df[df[disease_col] == disease]
            symptom_counts = disease_data[symptom_cols].sum()
            
            # Top symptômes pour cette maladie
            top_symptoms = symptom_counts.nlargest(top_n)
            
            disease_profiles.append({
                'disease': disease,
                'total_symptom_count': int(symptom_counts.sum()),
                'top_symptoms': [
                    {
                        'symptom': symptom,
                        'count': int(count)
                    }
                    for symptom, count in top_symptoms.items()
                ]
            })
        
        return disease_profiles
    
    def predict_disease(self, symptoms_input, model, symptom_cols, top_k=5):
        """
        Prédire la maladie en fonction d'une liste de symptômes
        
        Args:
            symptoms_input: Liste de symptômes (noms de colonnes)
            model: Modèle entraîné
            symptom_cols: Liste de toutes les colonnes de symptômes
            top_k: Nombre de prédictions à retourner
        
        Returns:
            Liste des top_k maladies avec probabilités
        """
        # Créer un vecteur binaire
        symptom_vector = np.zeros((1, len(symptom_cols)))
        for symptom in symptoms_input:
            if symptom in symptom_cols:
                idx = symptom_cols.index(symptom)
                symptom_vector[0, idx] = 1
        
        # Prédire
        probabilities = model.predict_proba(symptom_vector)[0]
        top_indices = probabilities.argsort()[-top_k:][::-1]
        
        predictions = [
            {
                'disease': model.classes_[idx],
                'probability': round(float(probabilities[idx]), 4)
            }
            for idx in top_indices
        ]
        
        return predictions
