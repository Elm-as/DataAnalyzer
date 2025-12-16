import pandas as pd
import numpy as np
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
import json

try:
    import tensorflow as tf
    from tensorflow import keras
    from keras import layers
    from keras import models
    from keras.callbacks import EarlyStopping
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    # Define dummy classes to avoid NameError
    EarlyStopping = None

class NeuralNetworkAnalyzer:
    def __init__(self, df):
        self.df = df
        
    def perform_analysis(self, config):
        """
        Réseaux de neurones (MLP, CNN, RNN, LSTM)
        config = {
            'target': 'nom_colonne_cible',
            'features': ['col1', 'col2', ...],
            'task': 'classification' or 'regression',
            'methods': ['mlp_sklearn', 'mlp_deep', 'cnn', 'rnn', 'lstm'],
            'test_size': 0.2,
            'epochs': 50,
            'batch_size': 32,
            'hidden_layers': [100, 50],  # Pour sklearn MLP
            'learning_rate': 0.001
        }
        """
        results = {
            'summary': {},
            'models': {}
        }
        
        # Préparation des données
        X = self.df[config['features']].fillna(self.df[config['features']].mean())
        y = self.df[config['target']]
        
        task = config.get('task', 'classification')
        
        # Encoder la variable cible pour classification
        if task == 'classification':
            le = LabelEncoder()
            if y.dtype == 'object':
                y = le.fit_transform(y)
                results['label_mapping'] = dict(zip(le.classes_, le.transform(le.classes_)))
            n_classes = len(np.unique(y))
        else:
            y = y.fillna(y.mean())
            n_classes = None
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=config.get('test_size', 0.2), random_state=42
        )
        
        # Standardisation
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        methods = config.get('methods', ['mlp_sklearn'])
        
        # MLP avec Sklearn (simple et rapide)
        if 'mlp_sklearn' in methods:
            results['models']['mlp_sklearn'] = self._mlp_sklearn(
                X_train_scaled, X_test_scaled, y_train, y_test, config, task, n_classes
            )
        
        # Réseaux profonds avec TensorFlow/Keras
        if TENSORFLOW_AVAILABLE:
            if 'mlp_deep' in methods:
                results['models']['mlp_deep'] = self._mlp_deep(
                    X_train_scaled, X_test_scaled, y_train, y_test, config, task, n_classes
                )
            
            if 'cnn' in methods and task == 'classification':
                results['models']['cnn'] = self._cnn_model(
                    X_train_scaled, X_test_scaled, y_train, y_test, config, n_classes
                )
            
            if 'rnn' in methods:
                results['models']['rnn'] = self._rnn_model(
                    X_train_scaled, X_test_scaled, y_train, y_test, config, task, n_classes
                )
            
            if 'lstm' in methods:
                results['models']['lstm'] = self._lstm_model(
                    X_train_scaled, X_test_scaled, y_train, y_test, config, task, n_classes
                )
        else:
            results['warning'] = 'TensorFlow non installé. Seul MLP sklearn est disponible.'
        
        results['summary'] = self._summarize_results(results['models'], task)
        
        return results
    
    def _mlp_sklearn(self, X_train, X_test, y_train, y_test, config, task, n_classes):
        """Multi-Layer Perceptron avec Sklearn"""
        hidden_layers = tuple(config.get('hidden_layers', [100, 50]))
        max_iter = config.get('epochs', 200)
        learning_rate = config.get('learning_rate', 0.001)
        
        if task == 'classification':
            model = MLPClassifier(
                hidden_layer_sizes=hidden_layers,
                max_iter=max_iter,
                learning_rate_init=learning_rate,
                random_state=42,
                early_stopping=True,
                validation_fraction=0.1
            )
        else:
            model = MLPRegressor(
                hidden_layer_sizes=hidden_layers,
                max_iter=max_iter,
                learning_rate_init=learning_rate,
                random_state=42,
                early_stopping=True,
                validation_fraction=0.1
            )
        
        model.fit(X_train, y_train)
        
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        result = {
            'method': 'Multi-Layer Perceptron (Sklearn)',
            'architecture': {
                'hidden_layers': hidden_layers,
                'n_parameters': sum([w.size for w in model.coefs_]),
                'n_iterations': model.n_iter_
            }
        }
        
        if task == 'classification':
            result['train_metrics'] = {
                'accuracy': float(accuracy_score(y_train, y_pred_train))
            }
            result['test_metrics'] = {
                'accuracy': float(accuracy_score(y_test, y_pred_test))
            }
        else:
            result['train_metrics'] = {
                'r2': float(r2_score(y_train, y_pred_train)),
                'rmse': float(np.sqrt(mean_squared_error(y_train, y_pred_train)))
            }
            result['test_metrics'] = {
                'r2': float(r2_score(y_test, y_pred_test)),
                'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred_test)))
            }
        
        result['predictions_sample'] = y_pred_test[:10].tolist()
        
        return result
    
    def _mlp_deep(self, X_train, X_test, y_train, y_test, config, task, n_classes):
        """MLP profond avec TensorFlow/Keras"""
        input_dim = X_train.shape[1]
        epochs = config.get('epochs', 50)
        batch_size = config.get('batch_size', 32)
        
        # Architecture du réseau
        model = models.Sequential([
            layers.Dense(128, activation='relu', input_shape=(input_dim,)),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
        ])
        
        if task == 'classification':
            model.add(layers.Dense(n_classes, activation='softmax'))
            model.compile(
                optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )
        else:
            model.add(layers.Dense(1))
            model.compile(
                optimizer='adam',
                loss='mse',
                metrics=['mae']
            )
        
        # Early stopping
        early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        
        # Entraînement
        history = model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            callbacks=[early_stop],
            verbose=0
        )
        
        # Évaluation
        train_results = model.evaluate(X_train, y_train, verbose=0)
        test_results = model.evaluate(X_test, y_test, verbose=0)
        
        # Prédictions
        y_pred_test = model.predict(X_test, verbose=0)
        if task == 'classification':
            y_pred_test = np.argmax(y_pred_test, axis=1)
        else:
            y_pred_test = y_pred_test.flatten()
        
        result = {
            'method': 'Deep MLP (TensorFlow/Keras)',
            'architecture': {
                'layers': [
                    {'type': 'Dense', 'units': 128, 'activation': 'relu'},
                    {'type': 'Dropout', 'rate': 0.3},
                    {'type': 'Dense', 'units': 64, 'activation': 'relu'},
                    {'type': 'Dropout', 'rate': 0.2},
                    {'type': 'Dense', 'units': 32, 'activation': 'relu'},
                ],
                'n_parameters': int(model.count_params()),
                'epochs_trained': len(history.history['loss'])
            },
            'training_history': {
                'loss': [float(x) for x in history.history['loss']],
                'val_loss': [float(x) for x in history.history['val_loss']]
            },
            'predictions_sample': y_pred_test[:10].tolist()
        }
        
        if task == 'classification':
            result['train_metrics'] = {'accuracy': float(train_results[1])}
            result['test_metrics'] = {'accuracy': float(test_results[1])}
        else:
            result['train_metrics'] = {'loss': float(train_results[0]), 'mae': float(train_results[1])}
            result['test_metrics'] = {'loss': float(test_results[0]), 'mae': float(test_results[1])}
        
        return result
    
    def _cnn_model(self, X_train, X_test, y_train, y_test, config, n_classes):
        """Convolutional Neural Network (nécessite reshaping des données)"""
        epochs = config.get('epochs', 50)
        batch_size = config.get('batch_size', 32)
        
        # Reshape pour CNN (ajouter dimension)
        X_train_reshaped = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
        X_test_reshaped = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)
        
        model = models.Sequential([
            layers.Conv1D(64, 3, activation='relu', input_shape=(X_train.shape[1], 1)),
            layers.MaxPooling1D(2),
            layers.Conv1D(32, 3, activation='relu'),
            layers.GlobalAveragePooling1D(),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(n_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        
        history = model.fit(
            X_train_reshaped, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            callbacks=[early_stop],
            verbose=0
        )
        
        test_results = model.evaluate(X_test_reshaped, y_test, verbose=0)
        y_pred_test = np.argmax(model.predict(X_test_reshaped, verbose=0), axis=1)
        
        return {
            'method': 'Convolutional Neural Network (CNN)',
            'architecture': {
                'type': '1D CNN',
                'n_parameters': int(model.count_params())
            },
            'test_metrics': {'accuracy': float(test_results[1])},
            'predictions_sample': y_pred_test[:10].tolist()
        }
    
    def _rnn_model(self, X_train, X_test, y_train, y_test, config, task, n_classes):
        """Recurrent Neural Network"""
        epochs = config.get('epochs', 50)
        batch_size = config.get('batch_size', 32)
        
        # Reshape pour RNN
        X_train_reshaped = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
        X_test_reshaped = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)
        
        model = models.Sequential([
            layers.SimpleRNN(64, return_sequences=True, input_shape=(X_train.shape[1], 1)),
            layers.SimpleRNN(32),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.3)
        ])
        
        if task == 'classification':
            model.add(layers.Dense(n_classes, activation='softmax'))
            model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        else:
            model.add(layers.Dense(1))
            model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        
        early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        
        history = model.fit(
            X_train_reshaped, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            callbacks=[early_stop],
            verbose=0
        )
        
        test_results = model.evaluate(X_test_reshaped, y_test, verbose=0)
        
        return {
            'method': 'Recurrent Neural Network (RNN)',
            'architecture': {
                'type': 'SimpleRNN',
                'n_parameters': int(model.count_params())
            },
            'test_metrics': {'accuracy' if task == 'classification' else 'mae': float(test_results[1])}
        }
    
    def _lstm_model(self, X_train, X_test, y_train, y_test, config, task, n_classes):
        """Long Short-Term Memory Network"""
        epochs = config.get('epochs', 50)
        batch_size = config.get('batch_size', 32)
        
        # Reshape pour LSTM
        X_train_reshaped = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
        X_test_reshaped = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)
        
        model = models.Sequential([
            layers.LSTM(64, return_sequences=True, input_shape=(X_train.shape[1], 1)),
            layers.Dropout(0.2),
            layers.LSTM(32),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu')
        ])
        
        if task == 'classification':
            model.add(layers.Dense(n_classes, activation='softmax'))
            model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        else:
            model.add(layers.Dense(1))
            model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        
        early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        
        history = model.fit(
            X_train_reshaped, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            callbacks=[early_stop],
            verbose=0
        )
        
        test_results = model.evaluate(X_test_reshaped, y_test, verbose=0)
        
        return {
            'method': 'Long Short-Term Memory (LSTM)',
            'architecture': {
                'type': 'LSTM',
                'n_parameters': int(model.count_params())
            },
            'test_metrics': {'accuracy' if task == 'classification' else 'mae': float(test_results[1])}
        }
    
    def _summarize_results(self, models, task):
        """Résumé des résultats"""
        if not models:
            return {}
        
        comparison = []
        metric_key = 'accuracy' if task == 'classification' else 'mae'
        
        for name, result in models.items():
            if 'test_metrics' in result and metric_key in result['test_metrics']:
                comparison.append({
                    'model': result['method'],
                    'test_' + metric_key: result['test_metrics'][metric_key]
                })
        
        if task == 'classification':
            comparison.sort(key=lambda x: x['test_accuracy'], reverse=True)
        else:
            comparison.sort(key=lambda x: x['test_mae'])
        
        return {
            'best_model': comparison[0]['model'] if comparison else None,
            'comparison': comparison,
            'task': task
        }
