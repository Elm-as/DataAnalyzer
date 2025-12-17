import pandas as pd
import numpy as np
from datetime import datetime
import json

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    from statsmodels.tsa.stattools import adfuller, acf, pacf
    from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

class TimeSeriesAnalyzer:
    def __init__(self, df):
        self.df = df
        
    def perform_analysis(self, config):
        """
        Analyse de séries temporelles (ARIMA, SARIMA, Prophet)
        config = {
            'date_column': 'nom_colonne_date',
            'target_column': 'nom_colonne_cible',
            'methods': ['arima', 'sarima', 'prophet'],
            'forecast_periods': 30,
            'arima_order': (1, 1, 1),  # (p, d, q)
            'sarima_order': (1, 1, 1),  # (p, d, q)
            'sarima_seasonal_order': (1, 1, 1, 12),  # (P, D, Q, s)
            'test_size': 0.2
        }
        """
        results = {
            'summary': {},
            'models': {},
            'diagnostics': {}
        }
        
        if not STATSMODELS_AVAILABLE:
            results['error'] = 'statsmodels non installé. Installation requise: pip install statsmodels'
            return results
        
        # Préparation des données
        df = self.df.copy()
        df[config['date_column']] = pd.to_datetime(df[config['date_column']])
        df = df.sort_values(config['date_column'])
        df = df.set_index(config['date_column'])
        
        # Série temporelle
        ts = df[config['target_column']].dropna()
        
        # Tests de stationnarité
        results['diagnostics']['stationarity'] = self._test_stationarity(ts)
        
        # ACF et PACF pour déterminer les paramètres ARIMA
        results['diagnostics']['acf_pacf'] = self._calculate_acf_pacf(ts)
        
        # Split train/test
        test_size = int(len(ts) * config.get('test_size', 0.2))
        train = ts[:-test_size] if test_size > 0 else ts
        test = ts[-test_size:] if test_size > 0 else None
        
        methods = config.get('methods', ['arima'])
        
        # ARIMA
        if 'arima' in methods:
            results['models']['arima'] = self._arima_model(
                train, test, config
            )
        
        # SARIMA
        if 'sarima' in methods:
            results['models']['sarima'] = self._sarima_model(
                train, test, config
            )
        
        # Prophet
        if 'prophet' in methods and PROPHET_AVAILABLE:
            # Reconvertir pour Prophet (besoin d'un DataFrame avec colonnes 'ds' et 'y')
            df_prophet = df[[config['target_column']]].reset_index()
            df_prophet.columns = ['ds', 'y']
            
            train_prophet = df_prophet[:-test_size] if test_size > 0 else df_prophet
            test_prophet = df_prophet[-test_size:] if test_size > 0 else None
            
            results['models']['prophet'] = self._prophet_model(
                train_prophet, test_prophet, config
            )
        elif 'prophet' in methods:
            results['models']['prophet'] = {
                'error': 'Prophet non installé. Installation: pip install prophet'
            }
        
        # Comparaison des modèles
        results['summary'] = self._compare_time_series_models(results['models'])
        
        return results
    
    def _test_stationarity(self, ts):
        """Test de Dickey-Fuller augmenté pour la stationnarité"""
        result = adfuller(ts.dropna())
        
        return {
            'adf_statistic': float(result[0]),
            'p_value': float(result[1]),
            'n_lags': int(result[2]),
            'n_observations': int(result[3]),
            'critical_values': {k: float(v) for k, v in result[4].items()},
            'is_stationary': result[1] < 0.05,
            'interpretation': 'Série stationnaire' if result[1] < 0.05 else 'Série non-stationnaire (différenciation nécessaire)'
        }
    
    def _calculate_acf_pacf(self, ts, nlags=40):
        """Calcul ACF et PACF pour déterminer les paramètres ARIMA"""
        acf_values = acf(ts.dropna(), nlags=min(nlags, len(ts)//2 - 1))
        pacf_values = pacf(ts.dropna(), nlags=min(nlags, len(ts)//2 - 1))
        
        return {
            'acf': acf_values.tolist(),
            'pacf': pacf_values.tolist(),
            'suggested_p': int(np.argmax(np.abs(pacf_values[1:]) < 0.2) + 1),  # Premier lag non significatif
            'suggested_q': int(np.argmax(np.abs(acf_values[1:]) < 0.2) + 1)
        }
    
    def _arima_model(self, train, test, config):
        """Modèle ARIMA"""
        order = config.get('arima_order', (1, 1, 1))
        forecast_periods = config.get('forecast_periods', 30)
        
        try:
            # Entraînement
            model = ARIMA(train, order=order)
            fitted_model = model.fit()
            
            # Prédictions sur le test set
            if test is not None and len(test) > 0:
                predictions = fitted_model.forecast(steps=len(test))
                
                # Calcul des métriques
                mse = np.mean((test - predictions) ** 2)
                rmse = np.sqrt(mse)
                mae = np.mean(np.abs(test - predictions))
                mape = np.mean(np.abs((test - predictions) / test)) * 100
                
                test_metrics = {
                    'mse': float(mse),
                    'rmse': float(rmse),
                    'mae': float(mae),
                    'mape': float(mape)
                }
                test_index = test.index.astype(str).tolist()
            else:
                predictions = None
                test_metrics = None
                test_index = None
            
            # Prévisions futures
            forecast_obj = fitted_model.get_forecast(steps=forecast_periods)
            future_forecast = forecast_obj.predicted_mean
            conf_int = forecast_obj.conf_int(alpha=0.05) if hasattr(forecast_obj, "conf_int") else None
            
            # Résumé du modèle
            return {
                'method': f'ARIMA{order}',
                'order': order,
                'aic': float(fitted_model.aic),
                'bic': float(fitted_model.bic),
                'test_metrics': test_metrics,
                'test_predictions': predictions.tolist() if predictions is not None else None,
                'test_actual': test.tolist() if test is not None else None,
                'test_index': test_index,
                'forecast': {
                    'values': future_forecast.tolist(),
                    'lower_bound': conf_int.iloc[:, 0].tolist() if conf_int is not None else None,
                    'upper_bound': conf_int.iloc[:, 1].tolist() if conf_int is not None else None,
                    'periods': forecast_periods
                },
                'model_summary': {
                    'parameters': fitted_model.params.to_dict(),
                    'p_values': fitted_model.pvalues.to_dict()
                },
                'residuals_stats': {
                    'mean': float(fitted_model.resid.mean()),
                    'std': float(fitted_model.resid.std())
                }
            }
        except Exception as e:
            return {
                'method': f'ARIMA{order}',
                'error': str(e)
            }
    
    def _sarima_model(self, train, test, config):
        """Modèle SARIMA (ARIMA saisonnier)"""
        order = config.get('sarima_order', (1, 1, 1))
        seasonal_order = config.get('sarima_seasonal_order', (1, 1, 1, 12))
        forecast_periods = config.get('forecast_periods', 30)
        
        try:
            # Entraînement
            model = SARIMAX(train, order=order, seasonal_order=seasonal_order)
            fitted_model = model.fit(disp=False)
            
            # Prédictions sur le test set
            if test is not None and len(test) > 0:
                predictions = fitted_model.forecast(steps=len(test))
                
                # Calcul des métriques
                mse = np.mean((test - predictions) ** 2)
                rmse = np.sqrt(mse)
                mae = np.mean(np.abs(test - predictions))
                mape = np.mean(np.abs((test - predictions) / test)) * 100
                
                test_metrics = {
                    'mse': float(mse),
                    'rmse': float(rmse),
                    'mae': float(mae),
                    'mape': float(mape)
                }
                test_index = test.index.astype(str).tolist()
            else:
                predictions = None
                test_metrics = None
                test_index = None
            
            # Prévisions futures
            forecast_obj = fitted_model.get_forecast(steps=forecast_periods)
            future_forecast = forecast_obj.predicted_mean
            conf_int = forecast_obj.conf_int(alpha=0.05) if hasattr(forecast_obj, "conf_int") else None
            
            return {
                'method': f'SARIMA{order}x{seasonal_order}',
                'order': order,
                'seasonal_order': seasonal_order,
                'aic': float(fitted_model.aic),
                'bic': float(fitted_model.bic),
                'test_metrics': test_metrics,
                'test_predictions': predictions.tolist() if predictions is not None else None,
                'test_actual': test.tolist() if test is not None else None,
                'test_index': test_index,
                'forecast': {
                    'values': future_forecast.tolist(),
                    'lower_bound': conf_int.iloc[:, 0].tolist() if conf_int is not None else None,
                    'upper_bound': conf_int.iloc[:, 1].tolist() if conf_int is not None else None,
                    'periods': forecast_periods
                },
                'model_summary': {
                    'parameters': fitted_model.params.to_dict(),
                    'p_values': fitted_model.pvalues.to_dict()
                },
                'residuals_stats': {
                    'mean': float(fitted_model.resid.mean()),
                    'std': float(fitted_model.resid.std())
                }
            }
        except Exception as e:
            return {
                'method': f'SARIMA{order}x{seasonal_order}',
                'error': str(e)
            }
    
    def _prophet_model(self, train_df, test_df, config):
        """Modèle Prophet de Facebook"""
        forecast_periods = config.get('forecast_periods', 30)
        
        try:
            # Entraînement
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False
            )
            model.fit(train_df)
            
            # Prédictions sur le test set
            if test_df is not None and len(test_df) > 0:
                forecast_test = model.predict(test_df[['ds']])
                predictions = forecast_test['yhat'].values
                actual = test_df['y'].values
                
                # Calcul des métriques
                mse = np.mean((actual - predictions) ** 2)
                rmse = np.sqrt(mse)
                mae = np.mean(np.abs(actual - predictions))
                mape = np.mean(np.abs((actual - predictions) / actual)) * 100
                
                test_metrics = {
                    'mse': float(mse),
                    'rmse': float(rmse),
                    'mae': float(mae),
                    'mape': float(mape)
                }
            else:
                test_metrics = None
            
            # Prévisions futures
            future = model.make_future_dataframe(periods=forecast_periods)
            forecast = model.predict(future)
            
            # Récupérer uniquement les prévisions futures
            future_forecast = forecast.tail(forecast_periods)
            
            return {
                'method': 'Prophet',
                'test_metrics': test_metrics,
                'forecast': {
                    'values': future_forecast['yhat'].tolist(),
                    'lower_bound': future_forecast['yhat_lower'].tolist(),
                    'upper_bound': future_forecast['yhat_upper'].tolist(),
                    'periods': forecast_periods
                },
                'components': {
                    'trend': forecast['trend'].tail(forecast_periods).tolist(),
                    'yearly': forecast['yearly'].tail(forecast_periods).tolist() if 'yearly' in forecast.columns else None,
                    'weekly': forecast['weekly'].tail(forecast_periods).tolist() if 'weekly' in forecast.columns else None
                }
            }
        except Exception as e:
            return {
                'method': 'Prophet',
                'error': str(e)
            }
    
    def _compare_time_series_models(self, models):
        """Compare les performances des modèles de séries temporelles"""
        comparison = []
        
        for name, model_result in models.items():
            if 'error' not in model_result and model_result.get('test_metrics'):
                comparison.append({
                    'model': model_result['method'],
                    'rmse': model_result['test_metrics']['rmse'],
                    'mae': model_result['test_metrics']['mae'],
                    'mape': model_result['test_metrics']['mape'],
                    'aic': model_result.get('aic'),
                    'bic': model_result.get('bic')
                })
        
        # Trier par RMSE (plus bas = meilleur)
        if comparison:
            comparison.sort(key=lambda x: x['rmse'])
            
            return {
                'best_model': comparison[0]['model'],
                'comparison': comparison,
                'recommendation': f"Le modèle {comparison[0]['model']} a la meilleure performance avec RMSE={comparison[0]['rmse']:.4f}"
            }
        else:
            return {
                'best_model': None,
                'comparison': [],
                'recommendation': 'Aucune métrique de test disponible'
            }
