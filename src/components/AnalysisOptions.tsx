import React, { useState } from 'react';
import { ChevronLeft, Play, BarChart3, TrendingUp, Target, AlertTriangle, Layers, Clock, Brain, Network, Calendar, Sparkles, Stethoscope } from 'lucide-react';
import { DataColumn, AnalysisConfig } from '../App';
import { api } from '../api/backend';

interface AnalysisOptionsProps {
  config: AnalysisConfig;
  onConfigUpdated: (config: AnalysisConfig) => void;
  columns: DataColumn[];
  data: any[];
  targetColumn: string | null;
  onAnalysisComplete: (results: any) => void;
  onPrev: () => void;
}

const AnalysisOptions: React.FC<AnalysisOptionsProps> = ({
  config,
  onConfigUpdated,
  columns,
  data,
  targetColumn,
  onAnalysisComplete,
  onPrev,
}) => {
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);

  const selectedColumns = columns.filter(col => col.isSelected);
  const targetCol = targetColumn ? selectedColumns.find(col => col.name === targetColumn) || null : null;
  const featureColumns = selectedColumns.filter(col => col.name !== targetColumn);
  const numericColumns = selectedColumns.filter(col => col.type === 'number');
  const numericFeatures = featureColumns.filter(col => col.type === 'number' || col.type === 'boolean');
  const categoricalFeatures = featureColumns.filter(col => col.type === 'categorical' || col.type === 'string');
  const categoricalColumns = selectedColumns.filter(col => col.type === 'categorical');

  const analysisTypes = [
    {
      key: 'descriptiveStats' as keyof AnalysisConfig,
      name: 'Statistiques descriptives',
      description: 'Moyenne, médiane, écart-type, quartiles pour chaque colonne numérique',
      icon: BarChart3,
      color: 'blue',
      enabled: numericColumns.length > 0,
      estimatedTime: '~2s',
    },
    {
      key: 'correlations' as keyof AnalysisConfig,
      name: 'Corrélations',
      description: 'Matrice de corrélation entre les variables numériques',
      icon: Target,
      color: 'green',
      enabled: numericColumns.length > 1,
      estimatedTime: '~3s',
    },
    {
      key: 'distributions' as keyof AnalysisConfig,
      name: 'Distributions',
      description: 'Histogrammes et analyse de la distribution des données',
      icon: TrendingUp,
      color: 'purple',
      enabled: numericColumns.length > 0,
      estimatedTime: '~4s',
    },
    {
      key: 'outliers' as keyof AnalysisConfig,
      name: 'Détection d\'anomalies',
      description: 'Identification des valeurs aberrantes par méthode IQR',
      icon: AlertTriangle,
      color: 'orange',
      enabled: numericColumns.length > 0,
      estimatedTime: '~3s',
    },
    {
      key: 'clustering' as keyof AnalysisConfig,
      name: 'Clustering',
      description: 'Groupement automatique des données similaires',
      icon: Layers,
      color: 'indigo',
      enabled: numericColumns.length >= 2,
      estimatedTime: '~6s',
    },
    {
      key: 'trends' as keyof AnalysisConfig,
      name: 'Analyse de tendances',
      description: 'Identification des tendances temporelles dans les données',
      icon: Clock,
      color: 'pink',
      enabled: selectedColumns.some(col => col.type === 'date') && numericColumns.length > 0,
      estimatedTime: '~5s',
    },
    {
      key: 'categorical' as keyof AnalysisConfig,
      name: 'Analyse catégorielle',
      description: 'Fréquences, modes et distribution des variables catégorielles',
      icon: Layers,
      color: 'orange',
      enabled: categoricalColumns.length > 0,
      estimatedTime: '~3s',
    },
    {
      key: 'associations' as keyof AnalysisConfig,
      name: 'Tests d\'association',
      description: 'Chi-carré et tests d\'indépendance entre variables catégorielles',
      icon: Target,
      color: 'teal',
      enabled: categoricalColumns.length > 1,
      estimatedTime: '~4s',
    },
    // Analyses avancées (Backend Python)
    {
      key: 'regression' as keyof AnalysisConfig,
      name: 'Régression (ML)',
      description: 'Modèles de régression : Linéaire, Polynomial, Ridge, Lasso, ElasticNet',
      icon: TrendingUp,
      color: 'blue',
      enabled: !!targetCol && targetCol.type === 'number' && numericFeatures.length >= 1,
      estimatedTime: '~10s',
      advanced: true,
    },
    {
      key: 'classification' as keyof AnalysisConfig,
      name: 'Classification (ML)',
      description: 'KNN, SVM, Random Forest, Gradient Boosting, Decision Tree',
      icon: Target,
      color: 'green',
      enabled: !!targetCol && targetCol.type !== 'number' && (numericFeatures.length + categoricalFeatures.length) >= 1,
      estimatedTime: '~12s',
      advanced: true,
    },
    {
      key: 'discriminant' as keyof AnalysisConfig,
      name: 'Analyse Discriminante',
      description: 'LDA et QDA pour classification avec réduction de dimensionalité',
      icon: Layers,
      color: 'purple',
      enabled: !!targetCol && targetCol.type !== 'number' && numericFeatures.length >= 1,
      estimatedTime: '~8s',
      advanced: true,
    },
    {
      key: 'neuralNetworks' as keyof AnalysisConfig,
      name: 'Réseaux de Neurones',
      description: 'MLP, Deep Learning (CNN, RNN, LSTM) si TensorFlow disponible',
      icon: Brain,
      color: 'indigo',
      enabled: !!targetCol && featureColumns.length >= 1,
      estimatedTime: '~15s',
      advanced: true,
    },
    {
      key: 'timeSeries' as keyof AnalysisConfig,
      name: 'Séries Temporelles',
      description: 'ARIMA, SARIMA, Prophet pour prévisions temporelles',
      icon: Calendar,
      color: 'pink',
      enabled: selectedColumns.some(col => col.type === 'date') && numericColumns.length > 0,
      estimatedTime: '~20s',
      advanced: true,
    },
    {
      key: 'advancedClustering' as keyof AnalysisConfig,
      name: 'Clustering Avancé',
      description: 'K-Means, DBSCAN, Hierarchical, GMM avec optimisation automatique',
      icon: Network,
      color: 'orange',
      enabled: numericFeatures.length >= 2,
      estimatedTime: '~12s',
      advanced: true,
    },
    {
      key: 'dataCleaning' as keyof AnalysisConfig,
      name: 'Nettoyage de Données',
      description: 'Détection duplicatas, valeurs manquantes, normalisation, encoding',
      icon: Sparkles,
      color: 'teal',
      enabled: selectedColumns.length > 0,
      estimatedTime: '~8s',
      advanced: true,
    },
    {
      key: 'advancedStats' as keyof AnalysisConfig,
      name: 'Statistiques Avancées',
      description: 'Tests de normalité, t-test, ANOVA, Kruskal-Wallis, Chi-carré',
      icon: BarChart3,
      color: 'indigo',
      enabled: numericFeatures.length >= 2,
      estimatedTime: '~10s',
      advanced: true,
    },
    {
      key: 'symptomMatching' as keyof AnalysisConfig,
      name: 'Diagnostic & Prédiction',
      description: 'Analyse de similarité, TF-IDF et Naive Bayes pour prédiction (fonctionne avec tout type de données)',
      icon: Stethoscope,
      color: 'pink',
      enabled: !!targetCol && featureColumns.length >= 1,
      estimatedTime: '~15s',
      advanced: true,
    },
  ];

  const getColorClasses = (color: string, variant: 'bg' | 'text' | 'border' = 'bg') => {
    const colorMap = {
      blue: { bg: 'bg-blue-50', text: 'text-blue-600', border: 'border-blue-200' },
      green: { bg: 'bg-green-50', text: 'text-green-600', border: 'border-green-200' },
      purple: { bg: 'bg-purple-50', text: 'text-purple-600', border: 'border-purple-200' },
      orange: { bg: 'bg-orange-50', text: 'text-orange-600', border: 'border-orange-200' },
      indigo: { bg: 'bg-indigo-50', text: 'text-indigo-600', border: 'border-indigo-200' },
      pink: { bg: 'bg-pink-50', text: 'text-pink-600', border: 'border-pink-200' },
      teal: { bg: 'bg-teal-50', text: 'text-teal-600', border: 'border-teal-200' },
    };
    return colorMap[color as keyof typeof colorMap]?.[variant] || '';
  };

  const toggleAnalysis = (key: keyof AnalysisConfig) => {
    onConfigUpdated({ ...config, [key]: !config[key] });
  };

  const categoryMaps = React.useMemo(() => {
    const maps: Record<string, Map<string, number>> = {};
    featureColumns
      .filter(col => col.type === 'categorical' || col.type === 'string')
      .forEach(col => {
        const map = new Map<string, number>();
        const values = col.uniqueValues && col.uniqueValues.length > 0
          ? col.uniqueValues
          : Array.from(new Set(data.map(row => row[col.name]).filter(v => v !== undefined && v !== null)));
        values.forEach((val, idx) => map.set(String(val), idx));
        map.set('__missing__', values.length);
        maps[col.name] = map;
      });
    return maps;
  }, [featureColumns, data]);

  const encodeValue = (value: any, col: DataColumn) => {
    if (col.type === 'number') return Number(value) || 0;
    if (col.type === 'boolean') return (value === true || value === 1 || value === '1' || value === 'true') ? 1 : 0;
    const key = value === undefined || value === null || value === '' ? '__missing__' : String(value);
    const map = categoryMaps[col.name];
    if (map) {
      if (!map.has(key)) {
        map.set(key, map.size);
      }
      return map.get(key) ?? 0;
    }
    return typeof value === 'number' ? value : 0;
  };

  const prepareModelingData = () => {
    if (!targetCol) return data;
    return data.map(row => {
      const prepared: Record<string, any> = {};
      featureColumns.forEach(col => {
        prepared[col.name] = encodeValue(row[col.name], col);
      });
      prepared[targetCol.name] = row[targetCol.name];
      return prepared;
    });
  };

  const performAnalysis = async () => {
    setAnalyzing(true);
    setAnalysisProgress(0);

    const results: any = {
      summary: {
        totalRows: data.length,
        selectedColumns: selectedColumns.length,
        numericColumns: numericColumns.length,
        targetColumn: targetCol?.name || null,
        analysisDate: new Date().toISOString(),
      },
      analyses: {},
    };

    const modelingData = prepareModelingData();
    const featureNames = featureColumns.map(c => c.name);
    const numericFeatureNames = numericFeatures.map(c => c.name);

    const enabledAnalyses = Object.entries(config).filter(([_, enabled]) => enabled);
    let completedCount = 0;

    // Séparer les analyses de base et avancées
    const basicAnalysesKeys = ['descriptiveStats', 'correlations', 'distributions', 'outliers', 'categorical', 'associations'];
    const basicEnabled = enabledAnalyses.filter(([key]) => basicAnalysesKeys.includes(key));
    const advancedEnabled = enabledAnalyses.filter(([key]) => !basicAnalysesKeys.includes(key));

    // Helpers de normalisation des sorties backend pour l'UI et le PDF
    const normalizeRegression = (raw: any) => {
      if (!raw || !raw.models) return raw;
      const models: any = {};
      Object.entries(raw.models).forEach(([name, m]: [string, any]) => {
        const tm = m?.test_metrics || m?.metrics || {};
        models[name] = {
          ...m,
          r2_score: typeof tm.r2 === 'number' ? tm.r2 : m?.r2_score,
          rmse: typeof tm.rmse === 'number' ? tm.rmse : m?.rmse,
          mae: typeof tm.mae === 'number' ? tm.mae : m?.mae,
        };
      });
      const best = Object.entries(models)
        .map(([k, v]: [string, any]) => ({ key: k, r2: Number(v.r2_score ?? -Infinity) }))
        .sort((a, b) => b.r2 - a.r2)[0]?.key;
      return { ...raw, models, best_model: raw.best_model || best };
    };

    const normalizeClassification = (raw: any) => {
      if (!raw || !raw.models) return raw;
      const models: any = {};
      Object.entries(raw.models).forEach(([name, m]: [string, any]) => {
        const tm = m?.test_metrics || m?.metrics || {};
        models[name] = {
          ...m,
          accuracy: typeof tm.accuracy === 'number' ? tm.accuracy : m?.accuracy,
          precision: typeof tm.precision === 'number' ? tm.precision : m?.precision,
          recall: typeof tm.recall === 'number' ? tm.recall : m?.recall,
          f1_score: typeof tm.f1 === 'number' ? tm.f1 : (typeof tm.f1_score === 'number' ? tm.f1_score : m?.f1_score),
        };
      });
      const best = Object.entries(models)
        .map(([k, v]: [string, any]) => ({ key: k, acc: Number(v.accuracy ?? -Infinity) }))
        .sort((a, b) => b.acc - a.acc)[0]?.key;
      return { ...raw, models, best_model: raw.best_model || best };
    };

    const normalizeDiscriminant = normalizeClassification;

    const normalizeNeural = (raw: any) => {
      if (!raw) return raw;
      if (raw.task === 'regression') return normalizeRegression(raw);
      return normalizeClassification(raw);
    };

    const normalizeTimeSeries = (raw: any) => {
      if (!raw) return raw;
      const metrics = raw.metrics || {};
      const normalized = {
        ...raw,
        metrics: {
          ...metrics,
          mape: typeof metrics.mape === 'number' ? metrics.mape : metrics.MAPE,
          rmse: typeof metrics.rmse === 'number' ? metrics.rmse : metrics.RMSE,
        },
      };
      return normalized;
    };

    const normalizeClustering = (raw: any) => {
      if (!raw) return raw;
      const models: any = {};
      if (raw.models) {
        Object.entries(raw.models).forEach(([name, m]: [string, any]) => {
          const mt = m?.metrics || {};
          models[name] = {
            ...m,
            silhouette_score: mt.silhouette_score ?? mt.silhouette,
            davies_bouldin_score: mt.davies_bouldin_score ?? mt.davies_bouldin,
          };
        });
      }
      const best = Object.entries(models)
        .map(([k, v]: [string, any]) => ({ key: k, sil: Number(v.silhouette_score ?? -Infinity) }))
        .sort((a, b) => b.sil - a.sil)[0]?.key;
      return { ...raw, models, best_model: raw.best_model || best };
    };

    try {
      // Analyses de base (local)
      for (const [key] of basicEnabled) {
        try {
          switch (key) {
            case 'descriptiveStats':
              results.analyses.descriptiveStats = calculateDescriptiveStats();
              break;
            case 'correlations':
              results.analyses.correlations = calculateCorrelations();
              break;
            case 'distributions':
              results.analyses.distributions = calculateDistributions();
              break;
            case 'outliers':
              results.analyses.outliers = detectOutliers();
              break;
            case 'categorical':
              results.analyses.categorical = analyzeCategorical();
              break;
            case 'associations':
              results.analyses.associations = analyzeAssociations();
              break;
          }
        } catch (err) {
          console.error(`Erreur analyse de base ${key}:`, err);
        }
        completedCount++;
        setAnalysisProgress((completedCount / enabledAnalyses.length) * 100);
      }

      // Analyses avancées (backend)
      for (const [analysisType] of advancedEnabled) {
        try {
          switch (analysisType) {
            case 'regression': {
              if (targetCol && targetCol.type === 'number' && featureNames.length > 0) {
                const featureCols = numericFeatureNames.length > 0 ? numericFeatureNames : featureNames;
                const result = await api.regression(modelingData, {
                  target: targetCol.name,
                  features: featureCols,
                  methods: ['linear', 'polynomial', 'ridge', 'lasso', 'elastic'],
                  test_size: 0.2,
                  cv_folds: 5,
                });
                results.analyses.regression = normalizeRegression(result);
              }
              break;
            }
            case 'classification': {
              if (targetCol && targetCol.type !== 'number' && featureNames.length > 0) {
                const featureCols = numericFeatureNames.length > 0 ? numericFeatureNames : featureNames;
                const result = await api.classification(modelingData, {
                  target: targetCol.name,
                  features: featureCols,
                  methods: ['knn', 'svm', 'random_forest', 'gradient_boosting', 'decision_tree'],
                  test_size: 0.2,
                  cv_folds: 5,
                });
                results.analyses.classification = normalizeClassification(result);
              }
              break;
            }
            case 'discriminant': {
              if (targetCol && targetCol.type !== 'number' && numericFeatureNames.length > 0) {
                const result = await api.discriminant(modelingData, {
                  target: targetCol.name,
                  features: numericFeatureNames,
                  methods: ['lda', 'qda'],
                  test_size: 0.2,
                  cv_folds: 5,
                });
                results.analyses.discriminant = normalizeDiscriminant(result);
              }
              break;
            }
            case 'neuralNetworks': {
              if (targetCol && featureNames.length > 0) {
                const isClassification = targetCol.type !== 'number';
                const featureCols = numericFeatureNames.length > 0 ? numericFeatureNames : featureNames;
                const result = await api.neuralNetworks(modelingData, {
                  target: targetCol.name,
                  features: featureCols,
                  task: isClassification ? 'classification' : 'regression',
                  models: ['mlp'],
                  epochs: 100,
                  batch_size: 32,
                });
                results.analyses.neuralNetworks = normalizeNeural(result);
              }
              break;
            }
            case 'timeSeries': {
              if (selectedColumns.some(col => col.type === 'date') && numericColumns.length > 0) {
                const dateCol = selectedColumns.find(col => col.type === 'date')?.name;
                const valueCol = numericColumns[0].name;
                if (dateCol && valueCol) {
                  const result = await api.timeSeries(data, {
                    date_column: dateCol,
                    value_column: valueCol,
                    models: ['arima', 'sarima'],
                    forecast_periods: 30,
                    test_size: 0.2,
                  });
                  results.analyses.timeSeries = normalizeTimeSeries(result);
                }
              }
              break;
            }
            case 'advancedClustering': {
              if (numericFeatureNames.length >= 2) {
                const result = await api.clusteringAdvanced(modelingData, {
                  features: numericFeatureNames,
                  methods: ['kmeans', 'dbscan', 'hierarchical', 'gmm'],
                  n_clusters: 3,
                  auto_optimize: true,
                });
                results.analyses.clusteringAdvanced = normalizeClustering(result);
              }
              break;
            }
            case 'dataCleaning': {
              const result = await api.dataCleaning(data, {
                remove_duplicates: true,
                handle_missing: {
                  strategy: 'mean',
                  columns: numericColumns.map(c => c.name),
                },
                handle_outliers: {
                  method: 'iqr',
                  columns: numericColumns.map(c => c.name),
                },
                normalize: {
                  method: 'standard',
                  columns: numericColumns.map(c => c.name),
                },
              });
              results.analyses.dataCleaning = result;
              break;
            }
            case 'advancedStats': {
              if (numericFeatureNames.length >= 2) {
                const result = await api.advancedStats(modelingData, {
                  normality_tests: {
                    columns: numericFeatureNames,
                  },
                  correlation_tests: {
                    columns: numericFeatureNames,
                  },
                });
                results.analyses.advancedStats = result;
              }
              break;
            }
            case 'symptomMatching': {
              if (targetCol && featureColumns.length > 0) {
                const result = await api.symptomMatching(data, {
                  disease_column: targetCol.name,
                  symptom_columns: featureColumns.map(c => c.name),
                  model: 'all',
                  test_size: 0.2,
                  top_predictions: 5,
                  dataset_id: 'default'
                });
                results.analyses.symptomMatching = result;
              }
              break;
            }
          }
        } catch (error) {
          console.error(`Erreur lors de l'analyse ${analysisType}:`, error);
          // Continue avec les autres analyses même en cas d'erreur
        }
        completedCount++;
        setAnalysisProgress((completedCount / enabledAnalyses.length) * 100);
      }
    } catch (error) {
      console.error('Erreur générale lors des analyses:', error);
    }

    // Consolidation globale des meilleurs modèles et métriques clés pour le PDF / UI
    try {
      const bestModels: Record<string,string> = {};
      const perf: Array<{domain:string; metric:string; value:number|string}> = [];

      // Régression
      const reg = results.analyses.regression;
      if (reg?.best_model) {
        bestModels.regression = reg.best_model;
        const bm = reg.models?.[reg.best_model];
        const r2 = bm?.r2_score ?? bm?.test_metrics?.r2;
        if (typeof r2 === 'number') perf.push({ domain:'Régression', metric:'R²', value: r2 });
      }

      // Classification
      const cls = results.analyses.classification;
      if (cls?.best_model) {
        bestModels.classification = cls.best_model;
        const bm = cls.models?.[cls.best_model];
        const acc = bm?.accuracy ?? bm?.test_metrics?.accuracy;
        if (typeof acc === 'number') perf.push({ domain:'Classification', metric:'Accuracy', value: acc });
      }

      // Discriminant
      const disc = results.analyses.discriminant;
      if (disc?.best_model) {
        bestModels.discriminant = disc.best_model;
        const bm = disc.models?.[disc.best_model];
        const acc = bm?.accuracy ?? bm?.test_metrics?.accuracy;
        if (typeof acc === 'number') perf.push({ domain:'Discriminant', metric:'Accuracy', value: acc });
      }

      // Réseaux de neurones
      const nn = results.analyses.neuralNetworks;
      if (nn?.best_model) {
        bestModels.neuralNetworks = nn.best_model;
        const bm = nn.models?.[nn.best_model];
        // Choix du metric selon tâche
        if (nn.task === 'regression') {
          const r2 = bm?.r2_score ?? bm?.test_metrics?.r2;
          if (typeof r2 === 'number') perf.push({ domain:'Réseaux de neurones (régr.)', metric:'R²', value: r2 });
        } else {
          const acc = bm?.accuracy ?? bm?.test_metrics?.accuracy;
          if (typeof acc === 'number') perf.push({ domain:'Réseaux de neurones (classif.)', metric:'Accuracy', value: acc });
        }
      }

      // Séries temporelles
      const ts = results.analyses.timeSeries;
      if (ts?.metrics) {
        const mape = ts.metrics.mape;
        const rmse = ts.metrics.rmse;
        if (typeof mape === 'number') perf.push({ domain:'Séries temporelles', metric:'MAPE', value: mape });
        if (typeof rmse === 'number') perf.push({ domain:'Séries temporelles', metric:'RMSE', value: rmse });
      }

      // Clustering (avancé d'abord)
      const clustAdv = results.analyses.advancedClustering;
      const clustBasic = results.analyses.clustering;
      const clust = clustAdv || clustBasic;
      if (clust?.best_model) {
        bestModels.clustering = clust.best_model;
        const bm = clust.models?.[clust.best_model];
        const sil = bm?.silhouette_score ?? bm?.metrics?.silhouette_score;
        if (typeof sil === 'number') perf.push({ domain:'Clustering', metric:'Silhouette', value: sil });
      }

      // Statistiques avancées (exemple: normalité globale si dispo)
      const advStats = results.analyses.advancedStats;
      if (advStats?.normality_tests) {
        const countTests = Object.keys(advStats.normality_tests).length;
        perf.push({ domain:'Statistiques avancées', metric:'Tests normalité', value: countTests });
      }

      // Classement des performances (desc par value si numérique)
      const ranked = perf.slice().sort((a,b) => {
        const av = typeof a.value === 'number' ? a.value : -Infinity;
        const bv = typeof b.value === 'number' ? b.value : -Infinity;
        return bv - av;
      });

      results.summary.bestModels = bestModels;
      results.summary.performance = ranked;
    } catch (e) {
      console.warn('Consolidation globale échouée:', e);
    }

    setAnalyzing(false);
    onAnalysisComplete(results);
  };

  const calculateDescriptiveStats = () => {
    return numericColumns.map(column => {
      const values = data.map(row => row[column.name]).filter(val => val != null && !isNaN(val));
      const sorted = values.sort((a, b) => a - b);
      const n = sorted.length;

      return {
        column: column.name,
        count: n,
        mean: values.reduce((sum, val) => sum + val, 0) / n,
        median: n % 2 === 0 ? (sorted[n/2-1] + sorted[n/2]) / 2 : sorted[Math.floor(n/2)],
        min: Math.min(...values),
        max: Math.max(...values),
        q1: sorted[Math.floor(n * 0.25)],
        q3: sorted[Math.floor(n * 0.75)],
        std: Math.sqrt(values.reduce((sum, val) => sum + Math.pow(val - (values.reduce((s, v) => s + v, 0) / n), 2), 0) / n),
      };
    });
  };

  const calculateCorrelations = () => {
    const matrix: any = {};
    numericColumns.forEach(col1 => {
      matrix[col1.name] = {};
      numericColumns.forEach(col2 => {
        if (col1.name === col2.name) {
          matrix[col1.name][col2.name] = 1;
        } else {
          const values1 = data.map(row => row[col1.name]).filter(val => val != null && !isNaN(val));
          const values2 = data.map(row => row[col2.name]).filter(val => val != null && !isNaN(val));
          
          const n = Math.min(values1.length, values2.length);
          const mean1 = values1.reduce((sum, val) => sum + val, 0) / values1.length;
          const mean2 = values2.reduce((sum, val) => sum + val, 0) / values2.length;
          
          let numerator = 0, denominator1 = 0, denominator2 = 0;
          for (let i = 0; i < n; i++) {
            const diff1 = values1[i] - mean1;
            const diff2 = values2[i] - mean2;
            numerator += diff1 * diff2;
            denominator1 += diff1 * diff1;
            denominator2 += diff2 * diff2;
          }
          
          matrix[col1.name][col2.name] = numerator / Math.sqrt(denominator1 * denominator2) || 0;
        }
      });
    });
    return matrix;
  };

  const calculateDistributions = () => {
    return numericColumns.map(column => {
      const values = data.map(row => row[column.name]).filter(val => val != null && !isNaN(val));
      // Tri optionnel si nécessaire pour d'autres stats
      const min = Math.min(...values);
      const max = Math.max(...values);
      const bins = 10;
      const binSize = (max - min) / bins;
      
      const histogram = Array(bins).fill(0);
      values.forEach(val => {
        const binIndex = Math.min(Math.floor((val - min) / binSize), bins - 1);
        histogram[binIndex]++;
      });

      return {
        column: column.name,
        histogram,
        bins: Array(bins).fill(0).map((_, i) => ({
          start: min + i * binSize,
          end: min + (i + 1) * binSize,
          count: histogram[i],
        })),
      };
    });
  };

  const detectOutliers = () => {
    return numericColumns.map(column => {
      const values = data.map(row => row[column.name]).filter(val => val != null && !isNaN(val));
  values.sort((a, b) => a - b);
  const n = values.length;
      
  const q1 = values[Math.floor(n * 0.25)];
  const q3 = values[Math.floor(n * 0.75)];
      const iqr = q3 - q1;
      const lowerBound = q1 - 1.5 * iqr;
      const upperBound = q3 + 1.5 * iqr;
      
      const outliers = data
        .map((row, index) => ({ value: row[column.name], index }))
        .filter(item => item.value < lowerBound || item.value > upperBound);

      return {
        column: column.name,
        outlierCount: outliers.length,
        outlierPercentage: (outliers.length / data.length) * 100,
        outliers: outliers.slice(0, 10), // Limit to first 10
        bounds: { lower: lowerBound, upper: upperBound },
      };
    });
  };


  const analyzeCategorical = () => {
    return categoricalColumns.map(column => {
      const values = data.map(row => row[column.name]).filter(val => val != null && val !== '');
      const frequencies: { [key: string]: number } = {};
      
      values.forEach(val => {
        const key = val.toString();
        frequencies[key] = (frequencies[key] || 0) + 1;
      });

      const sortedFreqs = Object.entries(frequencies)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 20); // Limit to top 20 categories

      const totalCount = values.length;
      const uniqueCount = Object.keys(frequencies).length;
      const mode = sortedFreqs[0]?.[0];
      const modeFrequency = sortedFreqs[0]?.[1] || 0;

      return {
        column: column.name,
        totalCount,
        uniqueCount,
        mode,
        modeFrequency,
        modePercentage: (modeFrequency / totalCount) * 100,
        frequencies: sortedFreqs.map(([value, count]) => ({
          value,
          count,
          percentage: (count / totalCount) * 100,
        })),
      };
    });
  };

  const analyzeAssociations = () => {
    const associations: any[] = [];
    
    for (let i = 0; i < categoricalColumns.length; i++) {
      for (let j = i + 1; j < categoricalColumns.length; j++) {
        const col1 = categoricalColumns[i];
        const col2 = categoricalColumns[j];
        
        // Create contingency table
        const contingencyTable: { [key: string]: { [key: string]: number } } = {};
        const values1 = new Set<string>();
        const values2 = new Set<string>();
        
        data.forEach(row => {
          const val1 = row[col1.name]?.toString();
          const val2 = row[col2.name]?.toString();
          
          if (val1 && val2) {
            values1.add(val1);
            values2.add(val2);
            
            if (!contingencyTable[val1]) {
              contingencyTable[val1] = {};
            }
            contingencyTable[val1][val2] = (contingencyTable[val1][val2] || 0) + 1;
          }
        });
        
        // Calculate Chi-square (simplified)
        const totalCount = data.length;
        let chiSquare = 0;
        let degreesOfFreedom = (values1.size - 1) * (values2.size - 1);
        
        values1.forEach(v1 => {
          values2.forEach(v2 => {
            const observed = contingencyTable[v1]?.[v2] || 0;
            const rowTotal = Object.values(contingencyTable[v1] || {}).reduce((sum, val) => sum + val, 0);
            const colTotal = Array.from(values1).reduce((sum, val) => sum + (contingencyTable[val]?.[v2] || 0), 0);
            const expected = (rowTotal * colTotal) / totalCount;
            
            if (expected > 0) {
              chiSquare += Math.pow(observed - expected, 2) / expected;
            }
          });
        });
        
        associations.push({
          variable1: col1.name,
          variable2: col2.name,
          chiSquare: chiSquare,
          degreesOfFreedom,
          contingencyTable,
          association: chiSquare > 3.84 ? 'significant' : 'not significant', // p < 0.05 threshold
        });
      }
    }
    
    return associations;
  };

  const selectedAnalysesCount = Object.values(config).filter(Boolean).length;
  const estimatedTotalTime = analysisTypes
    .filter(analysis => config[analysis.key])
    .reduce((total, analysis) => total + parseInt(analysis.estimatedTime.match(/\d+/)?.[0] || '0'), 0);

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="mb-6 lg:mb-8">
        <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2">
          Options d'analyse
        </h2>
        <p className="text-sm sm:text-base text-gray-600">
          Choisissez les types d'analyses à effectuer sur vos données
        </p>
        
        <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="text-xl sm:text-2xl font-bold text-blue-600">{data.length}</div>
            <div className="text-xs sm:text-sm text-blue-800">Lignes de données</div>
          </div>
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="text-xl sm:text-2xl font-bold text-green-600">{selectedColumns.length}</div>
            <div className="text-xs sm:text-sm text-green-800">Colonnes sélectionnées</div>
          </div>
          <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
            <div className="text-xl sm:text-2xl font-bold text-purple-600">{numericColumns.length}</div>
            <div className="text-xs sm:text-sm text-purple-800">Colonnes numériques</div>
          </div>
          <div className="p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
            <div className="text-xs sm:text-sm text-indigo-800">Variable cible</div>
            <div className="text-xl sm:text-2xl font-bold text-indigo-700 truncate">
              {targetCol?.name || 'Aucune sélectionnée'}
            </div>
          </div>
        </div>

        {!targetCol && (
          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-800">
            Sélectionnez une variable cible dans l'étape précédente pour activer les analyses prédictives (régression, classification, simulateur).
          </div>
        )}
      </div>

      {/* Boutons de sélection rapide */}
      <div className="mb-6 flex flex-wrap gap-3">
        <button
          onClick={() => {
            const newConfig = { ...config };
            analysisTypes.forEach(analysis => {
              if (analysis.enabled) newConfig[analysis.key] = true;
            });
            onConfigUpdated(newConfig);
          }}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
        >
          ✓ Tout sélectionner
        </button>
        <button
          onClick={() => {
            const newConfig = { ...config };
            analysisTypes.filter(a => !a.advanced).forEach(analysis => {
              if (analysis.enabled) newConfig[analysis.key] = true;
            });
            onConfigUpdated(newConfig);
          }}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
        >
          Analyses de base
        </button>
        <button
          onClick={() => {
            const newConfig = { ...config };
            analysisTypes.filter(a => a.advanced).forEach(analysis => {
              if (analysis.enabled) newConfig[analysis.key] = true;
            });
            onConfigUpdated(newConfig);
          }}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
        >
          Analyses avancées (ML/DL)
        </button>
        <button
          onClick={() => {
            const newConfig = { ...config };
            Object.keys(newConfig).forEach(key => {
              newConfig[key as keyof AnalysisConfig] = false;
            });
            onConfigUpdated(newConfig);
          }}
          className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm font-medium"
        >
          Tout désélectionner
        </button>
      </div>

      {/* Analyses de base */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Analyses de Base (JavaScript)</h3>
        <div className="space-y-3 sm:space-y-4">
          {analysisTypes.filter(a => !a.advanced).map((analysis) => {
            const Icon = analysis.icon;
            const isSelected = config[analysis.key];
            
            return (
              <div
                key={analysis.key}
                className={`border rounded-lg p-4 sm:p-6 transition-all duration-200 ${
                  analysis.enabled
                    ? isSelected
                      ? `${getColorClasses(analysis.color, 'bg')} ${getColorClasses(analysis.color, 'border')} border-2`
                      : 'border-gray-200 bg-white hover:border-gray-300'
                    : 'border-gray-200 bg-gray-50 opacity-60'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex items-center space-x-3 sm:space-x-4">
                    <div className={`p-2 sm:p-3 rounded-lg ${
                      analysis.enabled 
                        ? isSelected 
                          ? getColorClasses(analysis.color, 'bg')
                          : 'bg-gray-100'
                        : 'bg-gray-100'
                    }`}>
                      <Icon 
                        size={20} 
                        className={
                          analysis.enabled 
                            ? isSelected 
                              ? getColorClasses(analysis.color, 'text')
                              : 'text-gray-600'
                            : 'text-gray-400'
                        } 
                      />
                    </div>

                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <h3 className="text-sm sm:text-base font-semibold text-gray-900">
                          {analysis.name}
                        </h3>
                        <span className="text-xs text-gray-500">{analysis.estimatedTime}</span>
                      </div>
                      <p className="text-xs sm:text-sm text-gray-600 mt-1">
                        {analysis.description}
                      </p>
                      {!analysis.enabled && (
                        <p className="text-xs text-orange-600 mt-1">
                          Conditions non remplies pour cette analyse
                        </p>
                      )}
                    </div>
                  </div>

                  <button
                    onClick={() => analysis.enabled && toggleAnalysis(analysis.key)}
                    disabled={!analysis.enabled}
                    className={`flex-shrink-0 px-4 sm:px-6 py-2 sm:py-3 rounded-lg font-medium transition-colors text-sm sm:text-base ${
                      analysis.enabled
                        ? isSelected
                          ? `${getColorClasses(analysis.color, 'text')} bg-white border-2 ${getColorClasses(analysis.color, 'border')}`
                          : 'text-gray-700 bg-gray-100 hover:bg-gray-200 border-2 border-transparent'
                        : 'text-gray-400 bg-gray-100 cursor-not-allowed'
                    }`}
                  >
                    {isSelected ? 'Activé ✓' : 'Activer'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Analyses avancées */}
      <div className="mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">🧠 Analyses Avancées (Python Backend - ML/DL)</h3>
        <p className="text-sm text-gray-600 mb-4">Ces analyses utilisent scikit-learn, TensorFlow, et d'autres bibliothèques Python puissantes</p>
        <div className="space-y-3 sm:space-y-4">
          {analysisTypes.filter(a => a.advanced).map((analysis) => {
            const Icon = analysis.icon;
            const isSelected = config[analysis.key];
          
          return (
            <div
              key={analysis.key}
              className={`border rounded-lg p-4 sm:p-6 transition-all duration-200 ${
                analysis.enabled
                  ? isSelected
                    ? `${getColorClasses(analysis.color, 'bg')} ${getColorClasses(analysis.color, 'border')} border-2`
                    : 'border-gray-200 bg-white hover:border-gray-300'
                  : 'border-gray-200 bg-gray-50 opacity-60'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center space-x-3 sm:space-x-4">
                  <div className={`p-2 sm:p-3 rounded-lg ${
                    analysis.enabled 
                      ? isSelected 
                        ? getColorClasses(analysis.color, 'bg')
                        : 'bg-gray-100'
                      : 'bg-gray-100'
                  }`}>
                    <Icon 
                      size={20} 
                      className={
                        analysis.enabled 
                          ? isSelected 
                            ? getColorClasses(analysis.color, 'text')
                            : 'text-gray-600'
                          : 'text-gray-400'
                      } 
                    />
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-sm sm:text-base font-semibold text-gray-900">
                        {analysis.name}
                      </h3>
                      <span className="text-xs text-gray-500">{analysis.estimatedTime}</span>
                    </div>
                    <p className="text-xs sm:text-sm text-gray-600 mt-1">
                      {analysis.description}
                    </p>
                    {!analysis.enabled && (
                      <p className="text-xs text-orange-600 mt-1">
                        Conditions non remplies pour cette analyse
                      </p>
                    )}
                  </div>
                </div>

                <button
                  onClick={() => analysis.enabled && toggleAnalysis(analysis.key)}
                  disabled={!analysis.enabled}
                  className={`flex-shrink-0 px-4 sm:px-6 py-2 sm:py-3 rounded-lg font-medium transition-colors text-sm sm:text-base ${
                    analysis.enabled
                      ? isSelected
                        ? `${getColorClasses(analysis.color, 'text')} bg-white border-2 ${getColorClasses(analysis.color, 'border')}`
                        : 'text-gray-700 bg-gray-100 hover:bg-gray-200 border-2 border-transparent'
                      : 'text-gray-400 bg-gray-100 cursor-not-allowed'
                  }`}
                >
                  {isSelected ? 'Activé ✓' : 'Activer'}
                </button>
              </div>
            </div>
          );
        })}
        </div>
      </div>

      {/* Analysis Summary */}
      <div className="mb-6 sm:mb-8 p-4 sm:p-6 bg-white border border-gray-200 rounded-lg">
        <h3 className="text-sm sm:text-base font-semibold text-gray-900 mb-3 sm:mb-4">Résumé de l'analyse</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
          <div>
            <div className="text-xs sm:text-sm text-gray-600 mb-2">Analyses sélectionnées:</div>
            <div className="text-xl sm:text-2xl font-bold text-blue-600">{selectedAnalysesCount}</div>
          </div>
          <div>
            <div className="text-xs sm:text-sm text-gray-600 mb-2">Temps estimé:</div>
            <div className="text-xl sm:text-2xl font-bold text-green-600">~{estimatedTotalTime}s</div>
          </div>
        </div>
      </div>

      {/* Progress Bar (when analyzing) */}
      {analyzing && (
        <div className="mb-6 sm:mb-8 p-4 sm:p-6 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center mb-4">
            <Play size={18} className="sm:w-5 sm:h-5 text-blue-600 mr-3 animate-spin" />
            <div>
              <h3 className="text-sm sm:text-base font-semibold text-blue-900">Analyse en cours...</h3>
              <p className="text-sm text-blue-700">Traitement de vos données</p>
            </div>
          </div>
          <div className="w-full bg-blue-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${analysisProgress}%` }}
            ></div>
          </div>
          <div className="mt-2 text-sm text-blue-700">
            {Math.round(analysisProgress)}% terminé
          </div>
        </div>
      )}

      {selectedAnalysesCount === 0 && !analyzing && (
        <div className="mb-6 sm:mb-8 p-4 sm:p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center">
            <div className="text-yellow-600 mr-3">⚠️</div>
            <div>
              <h3 className="text-sm sm:text-base font-semibold text-yellow-800">
                Aucune analyse sélectionnée
              </h3>
              <p className="text-sm text-yellow-700">
                Veuillez sélectionner au moins une analyse pour continuer
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row justify-between gap-3 sm:gap-0">
        <button
          onClick={onPrev}
          disabled={analyzing}
          className="inline-flex items-center justify-center px-4 sm:px-6 py-2 sm:py-3 border border-gray-300 rounded-lg text-sm sm:text-base font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronLeft size={16} className="sm:w-5 sm:h-5 mr-2" />
          Retour
        </button>

        <button
          onClick={performAnalysis}
          disabled={selectedAnalysesCount === 0 || analyzing}
          className="inline-flex items-center justify-center px-6 sm:px-8 py-2 sm:py-3 border border-transparent text-sm sm:text-base font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {analyzing ? (
            <>
              <div className="animate-spin mr-2">
                <Play size={16} className="sm:w-5 sm:h-5" />
              </div>
              Analyse en cours...
            </>
          ) : (
            <>
              <Play size={16} className="sm:w-5 sm:h-5 mr-2" />
              Lancer l'analyse
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default AnalysisOptions;
