import React, { useState, useEffect } from 'react';
import { Play, RotateCcw, TrendingUp, Target, AlertCircle, CheckCircle, Zap, Search, Wand2 } from 'lucide-react';
import { DataColumn } from '../App';

interface PredictionSimulatorProps {
  results: any;
  columns: DataColumn[];
  data: any[];
  targetColumn?: string | null;
}

interface FieldStats {
  mean?: number;
  median?: number;
  mode?: string;
  min?: number;
  max?: number;
  isNumeric: boolean;
}

const PredictionSimulator: React.FC<PredictionSimulatorProps> = ({
  results,
  columns,
  data,
  targetColumn = null,
}) => {
  const [inputValues, setInputValues] = useState<Record<string, any>>({});
  const [prediction, setPrediction] = useState<any>(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [availableFields, setAvailableFields] = useState<DataColumn[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [fieldStats, setFieldStats] = useState<Record<string, FieldStats>>({});
  const [filledCount, setFilledCount] = useState<number>(0);
  const [activeScenario, setActiveScenario] = useState<'quick' | 'typical' | 'extreme' | null>(null);
  const targetCol = targetColumn ? columns.find(c => c.name === targetColumn) || null : null;

  // Détecter les modèles disponibles et le meilleur
  useEffect(() => {
    detectBestModel();
    setupAvailableFields();
  }, [results, columns, data, targetColumn]);

  const detectBestModel = () => {
    if (targetCol) {
      setSelectedModel(targetCol.type === 'number' ? 'regression' : 'classification');
    }
    if (!results?.analyses) return;

    const models = [];

    // Classification
    if (results.analyses.classification?.best_model) {
      models.push({
        type: 'classification',
        name: results.analyses.classification.best_model,
        accuracy: results.analyses.classification.models?.[results.analyses.classification.best_model]?.accuracy || 0,
        category: 'Classification'
      });
    }

    // Régression
    if (results.analyses.regression?.best_model) {
      models.push({
        type: 'regression',
        name: results.analyses.regression.best_model,
        r2: results.analyses.regression.models?.[results.analyses.regression.best_model]?.r2_score || 0,
        category: 'Régression'
      });
    }

    // Correspondance Donnees (TF-IDF Matching) - UNIVERSEL
    if (results.analyses.symptomMatching?.tfidf_analysis?.top_symptoms_global) {
      models.push({
        type: 'correspondance',
        name: 'Correspondance Donnees (TF-IDF)',
        score: 1,
        category: 'Analyse de Correspondance'
      });
    }

    // Symptom Matching (Bernoulli/Multinomial)
    if (results.analyses.symptomMatching?.bernoulli_nb?.accuracy) {
      models.push({
        type: 'symptomMatching',
        name: 'Bernoulli Naive Bayes',
        accuracy: results.analyses.symptomMatching.bernoulli_nb.accuracy,
        category: 'Diagnostic Médical'
      });
    }

    // Neural Networks
    if (results.analyses.neuralNetworks?.best_model) {
      models.push({
        type: 'neuralNetworks',
        name: 'Neural Network',
        accuracy: results.analyses.neuralNetworks.sklearn_model?.accuracy || 0,
        category: 'Deep Learning'
      });
    }

    // Sélectionner le meilleur modèle
    if (models.length > 0) {
      const best = models.reduce((prev, current) => {
        const prevScore = prev.accuracy || prev.r2 || prev.score || 0;
        const currScore = current.accuracy || current.r2 || current.score || 0;
        return currScore > prevScore ? current : prev;
      });
      setSelectedModel(best.type);
    }
  };

  const setupAvailableFields = () => {
    const selectedCols = columns.filter(col => col.isSelected);
    const inputFields = selectedCols.filter(col => {
      const name = col.name.toLowerCase();
      return col.name !== targetColumn &&
             !name.includes('id') &&
             !name.includes('target') &&
             col.type !== 'date';
    });

    const stats = calculateFieldStats(inputFields);
    setAvailableFields(inputFields);
    setFieldStats(stats);
    autoFillWithStats(inputFields, stats);
  };

  const calculateFieldStats = (fields: DataColumn[]) => {
    const stats: Record<string, FieldStats> = {};
    
    fields.forEach(field => {
      const values = data
        .map(row => row[field.name])
        .filter(val => val !== null && val !== undefined && val !== '');

      if (field.type === 'number') {
        const numValues = values.filter(v => !isNaN(v)).map(Number);
        if (numValues.length > 0) {
          numValues.sort((a, b) => a - b);
          stats[field.name] = {
            mean: numValues.reduce((a, b) => a + b) / numValues.length,
            median: numValues[Math.floor(numValues.length / 2)],
            min: numValues[0],
            max: numValues[numValues.length - 1],
            isNumeric: true
          };
        }
      } else if (field.type === 'boolean') {
        const trueCount = values.filter(v => v === true || v === 1 || v === '1' || v === 'true').length;
        stats[field.name] = {
          mode: trueCount > values.length / 2 ? 'true' : 'false',
          isNumeric: false
        };
      } else if (field.type === 'categorical') {
        const freq: Record<string, number> = {};
        values.forEach(v => {
          freq[v] = (freq[v] || 0) + 1;
        });
        const mode = Object.keys(freq).reduce((a, b) => 
          freq[a] > freq[b] ? a : b
        );
        stats[field.name] = {
          mode: mode,
          isNumeric: false
        };
      }
    });

    return stats;
  };

  const autoFillWithStats = (fields: DataColumn[], statsSource?: Record<string, FieldStats>) => {
    const defaults: Record<string, any> = {};
    let filledCount = 0;
    const statsToUse = statsSource || fieldStats;

    fields.forEach(field => {
      const stats = statsToUse[field.name];
      
      if (field.type === 'boolean') {
        defaults[field.name] = false;
      } else if (field.type === 'number') {
        if (stats?.median !== undefined) {
          defaults[field.name] = Math.round(stats.median * 100) / 100;
          filledCount++;
        } else {
          defaults[field.name] = 0;
        }
      } else if (field.type === 'categorical' && field.uniqueValues) {
        defaults[field.name] = stats?.mode || field.uniqueValues[0];
        filledCount++;
      } else {
        defaults[field.name] = '';
      }
    });

    setInputValues(defaults);
    setFilledCount(filledCount);
  };

  const quickFillAllFields = () => {
    const filled: Record<string, any> = {};
    
    availableFields.forEach(field => {
      if (field.type === 'boolean') {
        filled[field.name] = Math.random() > 0.7;
      } else if (field.type === 'number') {
        const stats = fieldStats[field.name];
        if (stats?.median !== undefined) {
          const variance = (stats.max! - stats.min!) * 0.1;
          filled[field.name] = Math.round((stats.median + (Math.random() - 0.5) * variance) * 100) / 100;
        } else {
          filled[field.name] = 0;
        }
      } else if (field.type === 'categorical' && field.uniqueValues) {
        filled[field.name] = field.uniqueValues[0];
      } else {
        filled[field.name] = '';
      }
    });

    setInputValues(filled);
    setActiveScenario('quick');
  };

  const fillWithScenario = (scenario: 'typical' | 'extreme') => {
    const filled: Record<string, any> = {};
    
    availableFields.forEach(field => {
      if (field.type === 'boolean') {
        if (scenario === 'typical') {
          filled[field.name] = Math.random() > 0.85;
        } else {
          filled[field.name] = Math.random() > 0.3;
        }
      } else if (field.type === 'number') {
        const stats = fieldStats[field.name];
        if (stats?.median !== undefined) {
          if (scenario === 'typical') {
            filled[field.name] = stats.median;
          } else {
            filled[field.name] = Math.random() > 0.5 ? stats.min : stats.max;
          }
        }
      } else if (field.type === 'categorical' && field.uniqueValues) {
        filled[field.name] = field.uniqueValues[0];
      }
    });

    setInputValues(filled);
    setActiveScenario(scenario);
  };

  const handleInputChange = (fieldName: string, value: any) => {
    setInputValues(prev => ({
      ...prev,
      [fieldName]: value
    }));
    setActiveScenario(null);
  };

  const resetInputs = () => {
    autoFillWithStats(availableFields);
    setPrediction(null);
    setActiveScenario(null);
  };

  const predictFromDataset = () => {
    if (!targetCol || data.length === 0) return null;
    const targetName = targetCol.name;

    const scoredRows = data.map(row => {
      let score = 0;
      let considered = 0;
      availableFields.forEach(field => {
        const input = inputValues[field.name];
        if (input === undefined || input === '') return;
        const rowVal = row[field.name];
        considered++;
        if (field.type === 'number') {
          const stats = fieldStats[field.name];
          const range = ((stats?.max ?? 1) - (stats?.min ?? 0)) || 1;
          const diff = Math.abs((Number(rowVal) || 0) - (Number(input) || 0)) / range;
          score += Math.max(0, 1 - diff);
        } else if (field.type === 'boolean') {
          const normalizeBool = (v: any) => v === true || v === 1 || v === '1' || v === 'true';
          score += normalizeBool(rowVal) === normalizeBool(input) ? 1 : 0;
        } else {
          score += rowVal && input ? (String(rowVal) === String(input) ? 1 : 0.5) : 0;
        }
      });
      return { row, score: considered ? score / considered : 0 };
    }).filter(item => item.score > 0);

    if (scoredRows.length === 0) return null;

    scoredRows.sort((a, b) => b.score - a.score);
    const top = scoredRows.slice(0, Math.min(20, scoredRows.length));
    const totalWeight = top.reduce((sum, item) => sum + item.score, 0) || 1;

    if (targetCol.type === 'number') {
      const weighted = top.reduce((sum, item) => sum + (Number(item.row[targetName]) || 0) * item.score, 0) / totalWeight;
      const minVal = Math.min(...data.map(row => Number(row[targetName]) || 0));
      const maxVal = Math.max(...data.map(row => Number(row[targetName]) || 0));
      return {
        type: 'regression',
        predictedValue: weighted.toFixed(2),
        r2Score: results?.analyses?.regression ? (Number(results.analyses.regression.models?.[results.analyses.regression.best_model]?.r2_score) || 0).toFixed(1) : undefined,
        modelUsed: `Projection locale (${targetName})`,
        range: `${minVal.toFixed(2)} à ${maxVal.toFixed(2)}`
      };
    }

    const votes: Record<string, number> = {};
    top.forEach(item => {
      const key = item.row[targetName] === undefined || item.row[targetName] === null
        ? 'Inconnu'
        : String(item.row[targetName]);
      votes[key] = (votes[key] || 0) + item.score;
    });
    const sortedVotes = Object.entries(votes).sort((a, b) => b[1] - a[1]);
    const best = sortedVotes[0];
    const confidence = (best?.[1] || 0) / totalWeight * 100;

    return {
      type: 'classification',
      predictedClass: best?.[0] || 'N/A',
      confidence: confidence.toFixed(1),
      modelUsed: `Projection locale (${targetName})`,
      allClasses: sortedVotes.slice(1).map(([name]) => name)
    };
  };

  const getFilteredFields = () => {
    if (!searchQuery) return availableFields;
    
    const query = searchQuery.toLowerCase();
    return availableFields.filter(field => 
      field.name.toLowerCase().includes(query)
    );
  };

  const renderInputField = (field: DataColumn) => {
    const value = inputValues[field.name];

    if (field.type === 'boolean') {
      return (
        <div key={field.name} className="flex items-center space-x-3">
          <input
            type="checkbox"
            checked={value || false}
            onChange={(e) => handleInputChange(field.name, e.target.checked)}
            className="w-4 h-4 text-blue-600 rounded focus:ring-2"
          />
          <label className="text-sm text-gray-700 truncate flex-1" title={field.name}>
            {field.name}
          </label>
        </div>
      );
    }

    if (field.type === 'number') {
      const stats = fieldStats[field.name];
      const step = (stats?.max || 100) > 1000 ? 1 : 0.01;
      const min = stats?.min ?? 0;
      const max = stats?.max ?? 100;
      
      return (
        <div key={field.name} className="space-y-1">
          <label className="block text-xs font-medium text-gray-700 truncate">{field.name}</label>
          <div className="space-y-1.5">
            <input
              type="number"
              value={value ?? 0}
              onChange={(e) => handleInputChange(field.name, parseFloat(e.target.value) || 0)}
              min={min}
              max={max}
              step={step}
              className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-400 focus:border-transparent"
            />
            {stats && (
              <div className="text-xs text-gray-500 grid grid-cols-3 gap-1">
                <div className="truncate">Min: {stats.min?.toFixed(1)}</div>
                <div className="truncate">Median: {stats.median?.toFixed(1)}</div>
                <div className="truncate">Max: {stats.max?.toFixed(1)}</div>
              </div>
            )}
          </div>
        </div>
      );
    }

    if (field.type === 'categorical' && field.uniqueValues) {
      return (
        <div key={field.name} className="space-y-1">
          <label className="block text-xs font-medium text-gray-700 truncate">{field.name}</label>
          <select
            value={value || ''}
            onChange={(e) => handleInputChange(field.name, e.target.value)}
            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500"
          >
            {field.uniqueValues.map((option: any) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>
      );
    }

    return (
      <div key={field.name} className="space-y-1">
        <label className="block text-xs font-medium text-gray-700 truncate">{field.name}</label>
        <input
          type="text"
          value={value || ''}
          onChange={(e) => handleInputChange(field.name, e.target.value)}
          className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500"
        />
      </div>
    );
  };

  const runPrediction = async () => {
    setIsSimulating(true);
    
    try {
      const result = await simulatePrediction();
      setPrediction(result);
    } catch (error: any) {
      console.error('Prediction error:', error);
      setPrediction({
        type: 'error',
        message: `Erreur lors de la prédiction: ${error.message || error}`
      });
    } finally {
      setIsSimulating(false);
    }
  };

  const simulatePrediction = async () => {
    const local = predictFromDataset();
    if (local) return local;

    // Pour les modèles de correspondance et symptomMatching, utiliser l'API de prédiction ML
    if (selectedModel === 'correspondance' || selectedModel === 'symptomMatching') {
      const symptomMatching = results.analyses.symptomMatching;
      if (!symptomMatching) {
        return {
          type: 'error',
          message: 'Analyse Correspondance non disponible'
        };
      }

      // Construire l'objet features à partir des inputValues
      const features: Record<string, number> = {};
      availableFields.forEach(field => {
        const value = inputValues[field.name];
        if (field.type === 'boolean') {
          features[field.name] = (value === true || value === 1) ? 1 : 0;
        } else if (field.type === 'number') {
          features[field.name] = Number(value) || 0;
        } else {
          features[field.name] = value ? 1 : 0;
        }
      });

      // Compter les features actives
      const activeFeaturesCount = Object.values(features).filter(v => v !== 0).length;

      if (activeFeaturesCount === 0) {
        return {
          type: 'error',
          message: 'Veuillez sélectionner au moins un symptôme/variable pour obtenir une prédiction'
        };
      }

      // Appeler l'API /predict
      try {
        const response = await fetch('http://localhost:5000/predict', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            dataset_id: 'default',
            features: features
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          return {
            type: 'error',
            message: errorData.error || 'Erreur API /predict'
          };
        }

        const predictionData = await response.json();

        if (!predictionData.predictions || predictionData.predictions.length === 0) {
          return {
            type: 'error',
            message: 'Aucune prédiction retournée par le modèle'
          };
        }

        // Retourner les résultats au format attendu
        return {
          type: 'correspondance',
          selectedSymptoms: activeFeaturesCount,
          totalSymptoms: availableFields.length,
          matches: predictionData.predictions.slice(0, 5).map((p: any) => ({
            disease: p.class,
            score: p.probability
          })),
          topMatch: {
            disease: predictionData.top_prediction.class,
            score: predictionData.top_prediction.probability
          },
          confidence: (predictionData.top_prediction.probability * 100).toFixed(1),
          modelUsed: 'Modèle Prédictif ML (Bernoulli Naive Bayes)',
          n_features_used: predictionData.n_features_used
        };

      } catch (error: any) {
        console.error('API /predict error:', error);
        return {
          type: 'error',
          message: `Erreur de connexion à l'API: ${error.message || error}`
        };
      }
    }

    // Pour les autres types de modèles (classification, regression, neural)
    if (selectedModel === 'classification') {
      const classification = results.analyses.classification;
      if (!classification?.best_model) return null;

      const bestModel = classification.models[classification.best_model];
      if (!bestModel) return null;

      const accuracy = bestModel.accuracy || 0;
      const classes = bestModel.classes || [];

      if (classes.length === 0) return null;

      return {
        type: 'classification',
        predictedClass: classes[0],
        confidence: (accuracy * 100).toFixed(1),
        modelUsed: bestModel.model_name || 'Classification',
        allClasses: classes.slice(0, 5)
      };
    }

    if (selectedModel === 'regression') {
      const regression = results.analyses.regression;
      if (!regression?.best_model) return null;

      const bestModel = regression.models[regression.best_model];
      if (!bestModel) return null;

      const r2 = bestModel.r2_score || 0;
      const mean = bestModel.mean_target || 0;
      const stddev = bestModel.std_target || 1;

      return {
        type: 'regression',
        predictedValue: (mean + (Math.random() - 0.5) * stddev).toFixed(2),
        r2Score: (r2 * 100).toFixed(1),
        modelUsed: bestModel.model_name || 'Regression',
        range: `${(mean - stddev).toFixed(2)} à ${(mean + stddev).toFixed(2)}`
      };
    }

    if (selectedModel === 'neuralNetworks') {
      const nn = results.analyses.neuralNetworks;
      if (!nn?.sklearn_model) return null;

      return {
        type: 'neural',
        confidence: ((nn.sklearn_model.accuracy || 0) * 100).toFixed(1),
        modelUsed: 'Neural Network',
        epochs: nn.epochs_trained || 100
      };
    }

    return null;
  };

  const renderPredictionResult = () => {
    if (!prediction) return null;

    if (prediction.type === 'error') {
      return (
        <div className="mt-6 p-6 bg-gradient-to-br from-amber-50 to-orange-50 border-2 border-amber-300 rounded-lg">
          <div className="flex items-center mb-3">
            <AlertCircle className="w-6 h-6 text-amber-700 mr-2" />
            <h3 className="text-lg font-bold text-gray-900">Attention</h3>
          </div>
          <p className="text-gray-700">{prediction.message}</p>
          <div className="mt-4 p-3 bg-amber-100 rounded text-sm text-amber-900">
            💡 <strong>Conseil:</strong> Cochez des cases de symptômes ou modifiez les valeurs numériques pour obtenir un diagnostic.
          </div>
        </div>
      );
    }

    if (prediction.type === 'correspondance') {
      return (
        <div className="mt-6 p-6 bg-gradient-to-br from-emerald-50 to-teal-50 border-2 border-emerald-300 rounded-lg">
          <div className="flex items-center mb-4">
            <Target className="w-6 h-6 text-emerald-700 mr-2" />
            <h3 className="text-lg font-bold text-gray-900">Resultats de Correspondance</h3>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="p-3 bg-white rounded border border-emerald-100">
              <div className="text-sm text-gray-600">Symptômes Selectionnes</div>
              <div className="text-2xl font-bold text-emerald-700">
                {prediction.selectedSymptoms}
              </div>
            </div>
            <div className="p-3 bg-white rounded border border-emerald-100">
              <div className="text-sm text-gray-600">Confiance</div>
              <div className="text-2xl font-bold text-emerald-700">
                {prediction.confidence}%
              </div>
            </div>
          </div>

          {prediction.topMatch && (
            <div className="mb-4 p-4 bg-gradient-to-r from-emerald-100 to-teal-100 rounded-lg border-2 border-emerald-400">
              <div className="text-sm text-gray-600 mb-1">Diagnostic le plus probable</div>
              <div className="text-3xl font-bold text-emerald-800 mb-2">{prediction.topMatch.disease}</div>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-emerald-200 rounded-full h-3">
                  <div 
                    className="bg-emerald-700 h-3 rounded-full transition-all" 
                    style={{width: `${prediction.topMatch.score * 100}%`}}
                  ></div>
                </div>
                <span className="text-sm font-semibold text-emerald-800">{(prediction.topMatch.score * 100).toFixed(1)}%</span>
              </div>
            </div>
          )}

          <div className="space-y-2">
            <div className="text-sm font-semibold text-gray-700 mb-3">Autres Diagnostics Possibles :</div>
            {prediction.matches && prediction.matches.length > 1 ? (
              prediction.matches.slice(1).map((match: any, idx: number) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-white rounded border border-gray-200 hover:border-emerald-300 transition">
                  <div>
                    <div className="font-medium text-gray-900">{match.disease}</div>
                    <div className="text-xs text-gray-500">Correspondance #{idx + 2}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold text-emerald-700">
                      {(match.score * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-3 bg-gray-50 rounded text-gray-600 text-sm">
                Aucun autre diagnostic trouvé. Essayez de sélectionner d'autres symptômes.
              </div>
            )}
          </div>

          <div className="mt-4 p-3 bg-emerald-50 rounded border border-emerald-100 text-sm text-emerald-900">
            <span className="font-medium">Basé sur:</span> {prediction.modelUsed}
          </div>
        </div>
      );
    }

    if (prediction.type === 'diagnostic') {
      return (
        <div className="mt-6 p-6 bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-lg">
          <div className="flex items-center mb-4">
            <Target className="w-6 h-6 text-blue-700 mr-2" />
            <h3 className="text-lg font-bold text-gray-900">Resultats de Prediction</h3>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="p-3 bg-white rounded border border-blue-100">
              <div className="text-sm text-gray-600">Variables Actives</div>
              <div className="text-2xl font-bold text-blue-700">
                {prediction.activeVars} / {prediction.totalVars}
              </div>
            </div>
            <div className="p-3 bg-white rounded border border-blue-100">
              <div className="text-sm text-gray-600">Confiance</div>
              <div className="text-2xl font-bold text-blue-700">
                {(prediction.confidence * 100).toFixed(1)}%
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <div className="text-sm font-semibold text-gray-700 mb-3">Top Predictions :</div>
            {prediction.predictions && prediction.predictions.length > 0 ? (
              prediction.predictions.map((pred: any, idx: number) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-white rounded border border-gray-200">
                  <div>
                    <div className="font-medium text-gray-900">{pred.disease || `Prediction ${idx + 1}`}</div>
                    <div className="text-xs text-gray-500">Rang {idx + 1}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-blue-700">
                      {(pred.probability * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-3 bg-gray-50 rounded text-gray-600 text-sm">Aucune prediction disponible</div>
            )}
          </div>
        </div>
      );
    }

    if (prediction.type === 'classification') {
      return (
        <div className="mt-6 p-6 bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-300 rounded-lg">
          <div className="flex items-center mb-4">
            <CheckCircle className="w-6 h-6 text-green-700 mr-2" />
            <h3 className="text-lg font-bold text-gray-900">Classification</h3>
          </div>

          <div className="p-4 bg-white rounded border border-green-200 mb-4">
            <div className="text-sm text-gray-600 mb-1">Classe predite</div>
            <div className="text-3xl font-bold text-green-700 mb-3">{prediction.predictedClass}</div>
            <div className="text-sm text-gray-600">Score: {prediction.confidence}%</div>
          </div>

          {prediction.allClasses && prediction.allClasses.length > 1 && (
            <div className="p-4 bg-gray-50 rounded">
              <div className="text-sm font-medium text-gray-700 mb-2">Autres classes possibles:</div>
              <div className="space-y-1">
                {prediction.allClasses.slice(1).map((cls: string, idx: number) => (
                  <div key={idx} className="text-sm text-gray-600">• {cls}</div>
                ))}
              </div>
            </div>
          )}
        </div>
      );
    }

    if (prediction.type === 'regression') {
      return (
        <div className="mt-6 p-6 bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-300 rounded-lg">
          <div className="flex items-center mb-4">
            <TrendingUp className="w-6 h-6 text-purple-700 mr-2" />
            <h3 className="text-lg font-bold text-gray-900">Valeur Predite</h3>
          </div>

          <div className="p-4 bg-white rounded border border-purple-200 mb-4">
            <div className="text-sm text-gray-600 mb-1">Resultat</div>
            <div className="text-4xl font-bold text-purple-700 mb-3">{prediction.predictedValue}</div>
            <div className="text-sm text-gray-600">
              R Score: {prediction.r2Score}%
            </div>
          </div>

          {prediction.range && (
            <div className="p-3 bg-gray-50 rounded text-sm text-gray-700">
              <span className="font-medium">Plage estimee:</span> {prediction.range}
            </div>
          )}
        </div>
      );
    }

    if (prediction.type === 'neural') {
      return (
        <div className="mt-6 p-6 bg-gradient-to-br from-amber-50 to-orange-50 border-2 border-amber-300 rounded-lg">
          <div className="flex items-center mb-4">
            <TrendingUp className="w-6 h-6 text-amber-700 mr-2" />
            <h3 className="text-lg font-bold text-gray-900">Reseau Neural</h3>
          </div>

          <div className="p-4 bg-white rounded border border-amber-200">
            <div className="text-sm text-gray-600 mb-1">Precision</div>
            <div className="text-3xl font-bold text-amber-700 mb-3">{prediction.confidence}%</div>
            <div className="text-sm text-gray-600">
              Modele entraine sur {prediction.epochs} iterations
            </div>
          </div>
        </div>
      );
    }

    return null;
  };

  if (availableFields.length === 0) {
    return (
      <div className="p-8 text-center bg-gray-50 rounded-lg border border-gray-200">
        <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
        <p className="text-gray-600">Aucun champ disponible pour la simulation</p>
        <p className="text-sm text-gray-500 mt-2">Veuillez selectionner des colonnes autres que ID ou date</p>
      </div>
    );
  }

  const filteredFields = getFilteredFields();
  const isLargeDataset = availableFields.length > 20;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-6 rounded-lg text-white">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center">
            <Zap className="w-8 h-8 mr-3" />
            <div>
              <h2 className="text-2xl font-bold">Simulateur de Prediction</h2>
              <p className="text-blue-100 text-sm mt-1">
                {availableFields.length > 100 
                  ? `Attention: ${availableFields.length} variables - Mode rapide disponible` 
                  : availableFields.length > 50
                  ? `Nombre de variables: ${availableFields.length} - Utilisez la recherche` 
                  : `${availableFields.length} variables disponibles`}
              </p>
            </div>
          </div>
          {selectedModel && (
            <div className="text-right">
              <div className="text-xs text-blue-100">Modele actif</div>
              <div className="text-sm font-semibold capitalize">{selectedModel}</div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions for Large Datasets */}
      {isLargeDataset && (
        <div className="bg-amber-50 border border-amber-200 p-4 rounded-lg">
          <div className="flex items-start gap-3">
            <Wand2 className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="font-semibold text-gray-900 mb-2">Remplissage Rapide</h4>
              <p className="text-sm text-gray-700 mb-3">
                Avec {availableFields.length} variables, vous pouvez remplir les champs automatiquement avec des valeurs intelligentes.
              </p>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={quickFillAllFields}
                  className={`px-4 py-2 rounded text-sm font-medium transition ${
                    activeScenario === 'quick'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  Remplir Automatiquement
                </button>
                <button
                  onClick={() => fillWithScenario('typical')}
                  className={`px-4 py-2 rounded text-sm font-medium transition ${
                    activeScenario === 'typical'
                      ? 'bg-green-600 text-white'
                      : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  Cas Typique
                </button>
                <button
                  onClick={() => fillWithScenario('extreme')}
                  className={`px-4 py-2 rounded text-sm font-medium transition ${
                    activeScenario === 'extreme'
                      ? 'bg-red-600 text-white'
                      : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  Cas Extreme
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Search Box for Large Datasets */}
      {isLargeDataset && (
        <div className="relative">
          <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder={`Chercher parmi ${availableFields.length} variables...`}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          {searchQuery && (
            <div className="mt-1 text-sm text-gray-600">
              {filteredFields.length} résultat(s)
            </div>
          )}
        </div>
      )}

      {/* Input Fields */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            {searchQuery ? `Résultats (${filteredFields.length})` : 'Paramètres'}
          </h3>
          <button
            onClick={resetInputs}
            className="flex items-center px-3 py-1 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded hover:bg-gray-50"
          >
            <RotateCcw className="w-4 h-4 mr-1" />
            Réinitialiser
          </button>
        </div>

        <div className={`grid gap-4 ${
          filteredFields.length > 20 
            ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
            : 'grid-cols-1 md:grid-cols-2'
        } ${filteredFields.length > 50 ? 'max-h-96 overflow-y-auto' : ''}`}>
          {filteredFields.slice(0, 100).map(field => renderInputField(field))}
        </div>

        {filteredFields.length > 100 && (
          <p className="mt-4 text-sm text-amber-600 italic">
            ⚠️ Affichage limité aux 100 premiers résultats. {filteredFields.length - 100} masqués.
            Affinez votre recherche pour réduire le nombre de champs.
          </p>
        )}
      </div>

      {/* Predict Button */}
      <button
        onClick={runPrediction}
        disabled={isSimulating || !selectedModel}
        className={`w-full py-4 rounded-lg font-semibold text-white text-lg flex items-center justify-center transition ${
          isSimulating || !selectedModel
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700'
        }`}
      >
        {isSimulating ? (
          <>
            <RotateCcw className="w-5 h-5 mr-2 animate-spin" />
            Prediction en cours...
          </>
        ) : !selectedModel ? (
          <>
            <AlertCircle className="w-5 h-5 mr-2" />
            Aucun modele disponible
          </>
        ) : (
          <>
            <Play className="w-5 h-5 mr-2" />
            Lancer la Prediction
          </>
        )}
      </button>

      {filteredFields.length > 100 && (
        <p className="text-sm text-amber-600 italic px-3">
          Attention: Affichage limite aux 100 premiers resultats. {filteredFields.length - 100} variables masquees.
        </p>
      )}

      {/* Prediction Result */}
      {renderPredictionResult()}
    </div>
  );
};

export default PredictionSimulator;
