import React, { useState } from 'react';
import { ChevronLeft, Download, RefreshCw, BarChart3, TrendingUp, AlertTriangle, Target, Eye, FileText, Layers, Copy, Stethoscope, Zap } from 'lucide-react';
import { DataColumn } from '../App';
import { api } from '../api/backend';
import PredictionSimulator from './PredictionSimulator';

interface AnalysisResultsProps {
  results: any;
  columns: DataColumn[];
  data: any[];
  onPrev: () => void;
  onReset: () => void;
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({
  results,
  columns,
  data,
  onPrev,
  onReset,
}) => {
  const [activeTab, setActiveTab] = useState('overview');

  // Helpers robustes pour lire des métriques, quelle que soit la structure renvoyée par le backend
  const pick = (obj: any, keys: string[]) => {
    if (!obj) return undefined;
    for (const k of keys) {
      const v = obj?.[k];
      if (v !== undefined && v !== null && !(typeof v === 'number' && Number.isNaN(v))) return v;
      const mv = obj?.metrics?.[k];
      if (mv !== undefined && mv !== null && !(typeof mv === 'number' && Number.isNaN(mv))) return mv;
    }
    return undefined;
  };

  const getR2 = (m: any) => pick(m, ['r2_score', 'r2', 'R2', 'R2_score']);
  const getRMSE = (m: any) => pick(m, ['rmse', 'RMSE', 'root_mean_squared_error', 'root_mse']);
  const getMAE = (m: any) => pick(m, ['mae', 'MAE', 'mean_absolute_error']);

  const getAccuracy = (m: any) => pick(m, ['accuracy', 'acc', 'Accuracy']);
  const getPrecision = (m: any) => pick(m, ['precision', 'Precision', 'macro_precision', 'micro_precision']);
  const getRecall = (m: any) => pick(m, ['recall', 'Recall', 'sensitivity']);
  const getF1 = (m: any) => pick(m, ['f1_score', 'f1', 'F1', 'F1_score']);

  const getSilhouette = (m: any) => pick(m, ['silhouette_score', 'silhouette', 'sil_score']);
  const getDaviesBouldin = (m: any) => pick(m, ['davies_bouldin_score', 'davies_bouldin', 'db_index']);
  const getNClusters = (m: any) => pick(m, ['n_clusters', 'nClusters', 'clusters']);
  const getMAPE = (m: any) => pick(m, ['mape', 'MAPE', 'mean_absolute_percentage_error']);

  if (!results) {
    return (
      <div className="p-8 text-center">
        <div className="text-gray-500">Aucun résultat disponible</div>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', name: 'Vue d\'ensemble', icon: Eye },
    { id: 'descriptive', name: 'Statistiques', icon: BarChart3, available: results.analyses.descriptiveStats },
    { id: 'correlations', name: 'Corrélations', icon: Target, available: results.analyses.correlations },
    { id: 'distributions', name: 'Distributions', icon: TrendingUp, available: results.analyses.distributions },
    { id: 'outliers', name: 'Anomalies', icon: AlertTriangle, available: results.analyses.outliers },
    { id: 'categorical', name: 'Catégorielles', icon: Layers, available: results.analyses.categorical },
    { id: 'associations', name: 'Associations', icon: Target, available: results.analyses.associations },
    { id: 'regression', name: 'Régression', icon: TrendingUp, available: results.analyses.regression },
    { id: 'classification', name: 'Classification', icon: Target, available: results.analyses.classification },
    { id: 'discriminant', name: 'Analyse Discriminante', icon: Layers, available: results.analyses.discriminant },
    { id: 'neuralNetworks', name: 'Réseaux de Neurones', icon: BarChart3, available: results.analyses.neuralNetworks },
    { id: 'timeSeries', name: 'Séries Temporelles', icon: TrendingUp, available: results.analyses.timeSeries },
    { id: 'clustering', name: 'Clustering Avancé', icon: Target, available: results.analyses.clusteringAdvanced },
    { id: 'symptomMatching', name: 'Correspondance Donnees', icon: Stethoscope, available: results.analyses.symptomMatching },
    { id: 'simulator', name: 'Simulateur', icon: Zap, available: true },
  ].filter(tab => tab.id === 'overview' || tab.id === 'simulator' || tab.available);

  const formatNumber = (num: number, decimals = 2) => {
    return isNaN(num) ? 'N/A' : num.toFixed(decimals);
  };

  const formatPercentage = (num: number) => {
    return isNaN(num) ? 'N/A' : `${num.toFixed(1)}%`;
  };

  const getCorrelationColor = (value: number) => {
    const abs = Math.abs(value);
    if (abs > 0.7) return 'bg-red-500';
    if (abs > 0.5) return 'bg-orange-400';
    if (abs > 0.3) return 'bg-yellow-400';
    return 'bg-green-400';
  };

  const getCorrelationIntensity = (value: number) => {
    const abs = Math.abs(value);
    return Math.round(abs * 100);
  };

  const renderOverview = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <div className="p-6 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="text-xl sm:text-2xl font-bold text-blue-600">{results.summary.totalRows.toLocaleString()}</div>
          <div className="text-xs sm:text-sm text-blue-800">Lignes analysées</div>
        </div>
        <div className="p-6 bg-green-50 border border-green-200 rounded-lg">
          <div className="text-xl sm:text-2xl font-bold text-green-600">{results.summary.selectedColumns}</div>
          <div className="text-xs sm:text-sm text-green-800">Colonnes traitées</div>
        </div>
        <div className="p-6 bg-purple-50 border border-purple-200 rounded-lg">
          <div className="text-xl sm:text-2xl font-bold text-purple-600">{results.summary.numericColumns}</div>
          <div className="text-xs sm:text-sm text-purple-800">Variables numériques</div>
        </div>
        <div className="p-6 bg-orange-50 border border-orange-200 rounded-lg">
          <div className="text-xl sm:text-2xl font-bold text-orange-600">{Object.keys(results.analyses).length}</div>
          <div className="text-xs sm:text-sm text-orange-800">Analyses effectuées</div>
        </div>
      </div>

      <div className="p-4 sm:p-6 bg-white border border-gray-200 rounded-lg">
        <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-4">Résumé des analyses</h3>
        <div className="space-y-3">
          {Object.keys(results.analyses).map(analysisType => (
            <div key={analysisType} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-sm sm:text-base font-medium text-gray-900 capitalize">
                  {analysisType.replace(/([A-Z])/g, ' $1').toLowerCase()}
                </span>
              </div>
              <span className="text-sm text-green-600 font-medium">✓ Terminé</span>
            </div>
          ))}
        </div>
      </div>

      <div className="p-4 sm:p-6 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg">
        <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-2">🎯 Points clés</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          {results.analyses.descriptiveStats && (
            <li>• {results.analyses.descriptiveStats.length} variables numériques analysées</li>
          )}
          {results.analyses.correlations && (
            <li>• Matrice de corrélation calculée pour identifier les relations entre variables</li>
          )}
          {results.analyses.outliers && (
            <li>• Détection d'anomalies effectuée sur toutes les colonnes numériques</li>
          )}
          {results.analyses.distributions && (
            <li>• Analyse des distributions pour comprendre la répartition des données</li>
          )}
          {results.analyses.categorical && (
            <li>• Analyse des fréquences et modes des variables catégorielles</li>
          )}
          {results.analyses.associations && (
            <li>• Tests d'association Chi-carré entre variables catégorielles</li>
          )}
        </ul>
      </div>

      {(results.summary?.bestModels || results.summary?.performance) && (
        <div className="p-4 sm:p-6 bg-white border border-gray-200 rounded-lg">
          <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-4">Synthèse</h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {results.summary?.bestModels && (
              <div>
                <h4 className="text-sm sm:text-base font-semibold text-gray-800 mb-2">Meilleurs modèles</h4>
                <div className="space-y-2">
                  {Object.entries(results.summary.bestModels).map(([domain, model]: [string, any]) => (
                    <div key={domain} className="flex items-center justify-between bg-gray-50 border border-gray-200 rounded p-2">
                      <span className="text-xs sm:text-sm font-medium text-gray-700 capitalize">{domain.replace(/([A-Z])/g, ' $1')}</span>
                      <span className="text-xs sm:text-sm font-semibold text-gray-900">{String(model)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {results.summary?.performance && (
              <div>
                <h4 className="text-sm sm:text-base font-semibold text-gray-800 mb-2">Indicateurs clés</h4>
                <div className="space-y-2">
                  {results.summary.performance.slice(0, 6).map((item: any, idx: number) => {
                    const formatMetricValue = (metric: string, value: any) => {
                      if (typeof value !== 'number') return String(value);
                      const m = metric.toLowerCase();
                      if (m === 'accuracy') return `${(value <= 1 ? value * 100 : value).toFixed(2)}%`;
                      if (m === 'mape') return `${value.toFixed(2)}%`;
                      return value.toFixed(4);
                    };
                    return (
                      <div key={idx} className="flex items-center justify-between bg-gray-50 border border-gray-200 rounded p-2">
                        <div className="text-xs sm:text-sm text-gray-700">
                          <span className="font-medium">{item.domain}</span> • <span className="uppercase text-gray-600">{item.metric}</span>
                        </div>
                        <div className="text-xs sm:text-sm font-semibold text-gray-900">
                          {formatMetricValue(item.metric, item.value)}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );

  const buildSummaryText = () => {
    const lines: string[] = [];
    lines.push(`Résumé de l'analyse (${new Date(results.summary.analysisDate).toLocaleString()})`);
    lines.push(`- Lignes: ${results.summary.totalRows}`);
    lines.push(`- Colonnes sélectionnées: ${results.summary.selectedColumns}`);
    if (results.summary?.bestModels) {
      lines.push('\nMeilleurs modèles:');
      for (const [k, v] of Object.entries(results.summary.bestModels)) {
        lines.push(`• ${k}: ${String(v)}`);
      }
    }
    if (results.summary?.performance?.length) {
      lines.push('\nIndicateurs clés:');
      for (const item of results.summary.performance.slice(0, 10)) {
        const domain = item.domain || '';
        const metric = item.metric || '';
        let value = item.value;
        if (typeof value === 'number') {
          const m = String(metric).toLowerCase();
          if (m === 'accuracy') value = `${(value <= 1 ? value * 100 : value).toFixed(2)}%`;
          else if (m === 'mape') value = `${value.toFixed(2)}%`;
          else value = value.toFixed(4);
        }
        lines.push(`• ${domain} — ${metric}: ${value}`);
      }
    }
    // Fallbacks si bestModels/performance vides: tirer des infos des analyses de base/avancées
    const analyses = results.analyses || {};
    // Clustering avancé
    if (analyses.advancedClustering?.best_model && (!results.summary?.bestModels || Object.keys(results.summary.bestModels).length === 0)) {
      lines.push('\nClustering:');
      lines.push(`• Meilleur modèle: ${String(analyses.advancedClustering.best_model)}`);
    }
    // Séries temporelles
    if (analyses.timeSeries?.metrics) {
      const mape = analyses.timeSeries.metrics.mape;
      const rmse = analyses.timeSeries.metrics.rmse;
      lines.push('\nSéries temporelles:');
      if (typeof mape === 'number') lines.push(`• MAPE: ${mape.toFixed(2)}%`);
      if (typeof rmse === 'number') lines.push(`• RMSE: ${rmse.toFixed(4)}`);
    }
    // Corrélations (meilleure corrélation absolue)
    if (analyses.correlations) {
      let bestPair = '';
      let bestVal = 0;
      const corr = analyses.correlations as Record<string, Record<string, number>>;
      const cols = Object.keys(corr);
      for (let i = 0; i < cols.length; i++) {
        for (let j = i + 1; j < cols.length; j++) {
          const a = cols[i];
          const b = cols[j];
          const v = Math.abs(corr[a]?.[b] ?? 0);
          if (v > bestVal) { bestVal = v; bestPair = `${a} ~ ${b}`; }
        }
      }
      if (bestPair) {
        lines.push('\nCorrélations:');
        lines.push(`• Plus forte corrélation: ${bestPair} (|r|=${bestVal.toFixed(3)})`);
      }
    }
    // Outliers (colonne la plus affectée)
    if (analyses.outliers?.length) {
      const arr = analyses.outliers as Array<any>;
      const top = arr.slice().sort((a,b) => (b.outlierPercentage || 0) - (a.outlierPercentage || 0))[0];
      if (top) {
        lines.push('\nAnomalies:');
        lines.push(`• Colonne la plus affectée: ${top.column} (${(top.outlierPercentage || 0).toFixed(1)}%)`);
      }
    }
    // Statistiques avancées: résumé
    if (analyses.advancedStats?.summary) {
      const s = analyses.advancedStats.summary;
      lines.push('\nStatistiques avancées:');
      if (typeof s.total_tests === 'number') lines.push(`• Familles de tests: ${s.total_tests}`);
      if (typeof s.significant_results === 'number') lines.push(`• Résultats significatifs: ${s.significant_results}`);
      if (s.tests_performed?.length) lines.push(`• Tests: ${s.tests_performed.join(', ')}`);
    }
    return lines.join('\n');
  };

  const copySummary = async () => {
    try {
      const text = buildSummaryText();
      await navigator.clipboard.writeText(text);
      alert('Synthèse copiée dans le presse-papiers.');
    } catch (e) {
      console.error('Copie impossible', e);
      alert('Impossible de copier la synthèse.');
    }
  };

  const renderDescriptiveStats = () => (
    <div className="space-y-6">
      <div className="p-4 sm:p-6 bg-white border border-gray-200 rounded-lg">
        <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-4">Statistiques descriptives</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-2 sm:px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Variable</th>
                <th className="px-2 sm:px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nb</th>
                <th className="px-2 sm:px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Moyenne</th>
                <th className="px-2 sm:px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Médiane</th>
                <th className="px-2 sm:px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Écart-type</th>
                <th className="px-2 sm:px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Min</th>
                <th className="px-2 sm:px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Max</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {results.analyses.descriptiveStats.map((stat: any, index: number) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-2 sm:px-4 py-3 text-xs sm:text-sm font-medium text-gray-900">{stat.column}</td>
                  <td className="px-2 sm:px-4 py-3 text-xs sm:text-sm text-gray-600">{stat.count.toLocaleString()}</td>
                  <td className="px-2 sm:px-4 py-3 text-xs sm:text-sm text-gray-600">{formatNumber(stat.mean)}</td>
                  <td className="px-2 sm:px-4 py-3 text-xs sm:text-sm text-gray-600">{formatNumber(stat.median)}</td>
                  <td className="px-2 sm:px-4 py-3 text-xs sm:text-sm text-gray-600">{formatNumber(stat.std)}</td>
                  <td className="px-2 sm:px-4 py-3 text-xs sm:text-sm text-gray-600">{formatNumber(stat.min)}</td>
                  <td className="px-2 sm:px-4 py-3 text-xs sm:text-sm text-gray-600">{formatNumber(stat.max)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        {results.analyses.descriptiveStats.map((stat: any, index: number) => (
          <div key={index} className="p-4 sm:p-6 bg-white border border-gray-200 rounded-lg">
            <h4 className="text-sm sm:text-base font-semibold text-gray-900 mb-4">{stat.column}</h4>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-xs sm:text-sm text-gray-600">Quartile 1 (Q1)</span>
                <span className="text-xs sm:text-sm font-medium">{formatNumber(stat.q1)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs sm:text-sm text-gray-600">Quartile 3 (Q3)</span>
                <span className="text-xs sm:text-sm font-medium">{formatNumber(stat.q3)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs sm:text-sm text-gray-600">IQR (Q3-Q1)</span>
                <span className="text-xs sm:text-sm font-medium">{formatNumber(stat.q3 - stat.q1)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderCorrelations = () => (
    <div className="space-y-6">
      <div className="p-4 sm:p-6 bg-white border border-gray-200 rounded-lg">
        <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-4">Matrice de corrélation</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr>
                <th className="p-1 sm:p-2"></th>
                {Object.keys(results.analyses.correlations).map((col) => (
                  <th key={col} className="p-1 sm:p-2 text-xs font-medium text-gray-500 transform -rotate-45 origin-bottom-left">
                    <div className="w-16 sm:w-20 text-left">{col}</div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Object.entries(results.analyses.correlations).map(([row, correlations]: [string, any]) => (
                <tr key={row}>
                  <td className="p-1 sm:p-2 font-medium text-gray-900 text-xs sm:text-sm">{row}</td>
                  {Object.entries(correlations).map(([col, value]: [string, any]) => (
                    <td key={col} className="p-0.5 sm:p-1">
                      <div 
                        className={`w-8 h-8 sm:w-12 sm:h-12 rounded-lg flex items-center justify-center text-white text-xs font-bold ${getCorrelationColor(value)}`}
                        style={{ opacity: getCorrelationIntensity(value) / 100 }}
                        title={`${row} vs ${col}: ${formatNumber(value, 3)}`}
                      >
                        <span className="hidden sm:inline">{formatNumber(value, 2)}</span>
                        <span className="sm:hidden">{formatNumber(value, 1)}</span>
                      </div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4 text-sm text-gray-600">
          <p><strong>Légende:</strong> Rouge = forte corrélation (|r| {'>'} 0.7), Orange = corrélation modérée (|r| {'>'} 0.5), Jaune = corrélation faible (|r| {'>'} 0.3), Vert = pas de corrélation</p>
        </div>
      </div>
    </div>
  );

  const renderDistributions = () => (
    <div className="space-y-6">
      {results.analyses.distributions.map((dist: any, index: number) => (
        <div key={index} className="p-4 sm:p-6 bg-white border border-gray-200 rounded-lg">
          <h4 className="text-sm sm:text-base font-semibold text-gray-900 mb-4">{dist.column} - Distribution</h4>
          <div className="space-y-4">
            <div className="grid grid-cols-10 gap-0.5 sm:gap-1 h-32 sm:h-40">
              {dist.bins.map((bin: any, binIndex: number) => {
                const maxCount = Math.max(...dist.bins.map((b: any) => b.count));
                const height = (bin.count / maxCount) * 100;
                return (
                  <div key={binIndex} className="flex flex-col justify-end">
                    <div 
                      className="bg-blue-500 rounded-t-sm transition-all duration-300 hover:bg-blue-600"
                      style={{ height: `${height}%` }}
                      title={`${formatNumber(bin.start)} - ${formatNumber(bin.end)}: ${bin.count} valeurs`}
                    ></div>
                    <div className="text-xs text-gray-500 mt-1 transform -rotate-45 origin-top hidden sm:block">
                      {formatNumber(bin.start, 1)}
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="text-sm text-gray-600">
              <p>Histogramme montrant la distribution des valeurs en 10 intervalles</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  const renderOutliers = () => (
    <div className="space-y-6">
      {results.analyses.outliers.map((outlierData: any, index: number) => (
        <div key={index} className="p-4 sm:p-6 bg-white border border-gray-200 rounded-lg">
          <h4 className="text-sm sm:text-base font-semibold text-gray-900 mb-4">{outlierData.column} - Détection d'anomalies</h4>
          
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 mb-6">
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="text-xl sm:text-2xl font-bold text-red-600">{outlierData.outlierCount}</div>
              <div className="text-xs sm:text-sm text-red-800">Valeurs aberrantes</div>
            </div>
            <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
              <div className="text-xl sm:text-2xl font-bold text-orange-600">{formatPercentage(outlierData.outlierPercentage)}</div>
              <div className="text-xs sm:text-sm text-orange-800">Pourcentage d'anomalies</div>
            </div>
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="text-xl sm:text-2xl font-bold text-blue-600">IQR</div>
              <div className="text-xs sm:text-sm text-blue-800">Méthode utilisée</div>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <h5 className="text-sm sm:text-base font-medium text-gray-900 mb-2">Limites de détection</h5>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <div className="p-3 bg-gray-50 rounded-lg">
                  <span className="text-xs sm:text-sm text-gray-600">Limite inférieure:</span>
                  <div className="text-sm sm:text-base font-medium">{formatNumber(outlierData.bounds.lower)}</div>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <span className="text-xs sm:text-sm text-gray-600">Limite supérieure:</span>
                  <div className="text-sm sm:text-base font-medium">{formatNumber(outlierData.bounds.upper)}</div>
                </div>
              </div>
            </div>

            {outlierData.outliers.length > 0 && (
              <div>
                <h5 className="text-sm sm:text-base font-medium text-gray-900 mb-2">Exemples de valeurs aberrantes</h5>
                <div className="grid grid-cols-3 sm:grid-cols-5 gap-2">
                  {outlierData.outliers.slice(0, 10).map((outlier: any, outIndex: number) => (
                    <div key={outIndex} className="p-2 bg-red-50 border border-red-200 rounded text-center">
                      <div className="text-sm font-medium text-red-800">{formatNumber(outlier.value)}</div>
                      <div className="text-xs text-red-600">Ligne {outlier.index + 1}</div>
                    </div>
                  ))}
                </div>
                {outlierData.outliers.length > 10 && (
                  <p className="text-sm text-gray-600 mt-2">
                    ... et {outlierData.outliers.length - 10} autres valeurs aberrantes
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );

  const renderCategorical = () => (
    <div className="space-y-6">
      {results.analyses.categorical.map((catData: any, index: number) => (
        <div key={index} className="p-6 bg-white border border-gray-200 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-4">{catData.column} - Analyse catégorielle</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">{catData.totalCount.toLocaleString()}</div>
              <div className="text-sm text-orange-800">Total d'observations</div>
            </div>
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{catData.uniqueCount}</div>
              <div className="text-sm text-blue-800">Catégories uniques</div>
            </div>
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="text-lg font-bold text-green-600 truncate">{catData.mode}</div>
              <div className="text-sm text-green-800">Mode (plus fréquent)</div>
            </div>
            <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{formatPercentage(catData.modePercentage)}</div>
              <div className="text-sm text-purple-800">Fréquence du mode</div>
            </div>
          </div>

          <div className="space-y-4">
            <h5 className="font-medium text-gray-900">Distribution des fréquences</h5>
            <div className="space-y-2">
              {catData.frequencies.slice(0, 10).map((freq: any, freqIndex: number) => (
                <div key={freqIndex} className="flex items-center space-x-4">
                  <div className="w-32 text-sm font-medium text-gray-900 truncate">
                    {freq.value}
                  </div>
                  <div className="flex-1 bg-gray-200 rounded-full h-4 relative">
                    <div 
                      className="bg-orange-500 h-4 rounded-full transition-all duration-300"
                      style={{ width: `${Math.min(freq.percentage, 100)}%` }}
                    ></div>
                    <div className="absolute inset-0 flex items-center justify-center text-xs font-medium text-gray-700">
                      {freq.count} ({formatPercentage(freq.percentage)})
                    </div>
                  </div>
                </div>
              ))}
              {catData.frequencies.length > 10 && (
                <p className="text-sm text-gray-600">
                  ... et {catData.frequencies.length - 10} autres catégories
                </p>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  const renderAssociations = () => (
    <div className="space-y-6">
      <div className="p-6 bg-white border border-gray-200 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Tests d'association (Chi-carré)</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Variable 1</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Variable 2</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Chi-carré</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ddl</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Association</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {results.analyses.associations.map((assoc: any, index: number) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{assoc.variable1}</td>
                  <td className="px-4 py-3 font-medium text-gray-900">{assoc.variable2}</td>
                  <td className="px-4 py-3 text-gray-600">{formatNumber(assoc.chiSquare)}</td>
                  <td className="px-4 py-3 text-gray-600">{assoc.degreesOfFreedom}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      assoc.association === 'significant' 
                        ? 'bg-red-100 text-red-800' 
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {assoc.association === 'significant' ? '⚠️ Significative' : '✅ Non significative'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4 text-sm text-gray-600">
          <p><strong>Note:</strong> Une association significative (p {'<'} 0.05) indique que les deux variables ne sont pas indépendantes.</p>
        </div>
      </div>

      {results.analyses.associations.slice(0, 3).map((assoc: any, index: number) => (
        <div key={index} className="p-6 bg-white border border-gray-200 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-4">
            Tableau de contingence: {assoc.variable1} × {assoc.variable2}
          </h4>
          <div className="overflow-x-auto">
            <table className="min-w-full border border-gray-300">
              <thead>
                <tr className="bg-gray-50">
                  <th className="border border-gray-300 px-3 py-2 text-left font-medium text-gray-900">
                    {assoc.variable1} \ {assoc.variable2}
                  </th>
                  {Object.keys(Object.values(assoc.contingencyTable)[0] || {}).slice(0, 5).map((col: string) => (
                    <th key={col} className="border border-gray-300 px-3 py-2 text-center font-medium text-gray-900">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Object.entries(assoc.contingencyTable).slice(0, 5).map(([row, values]: [string, any]) => (
                  <tr key={row}>
                    <td className="border border-gray-300 px-3 py-2 font-medium text-gray-900">{row}</td>
                    {Object.entries(values).slice(0, 5).map(([col, count]: [string, any]) => (
                      <td key={col} className="border border-gray-300 px-3 py-2 text-center text-gray-600">
                        {count}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );

  const exportResults = async () => {
    try {
      // Générer le PDF via le backend
      await api.generateReport(results, {
        includeCharts: true,
        includeStatistics: true,
        format: 'A4'
      });
      
      // Le téléchargement se fait automatiquement dans api.generateReport
      console.log('Rapport PDF généré avec succès');
    } catch (error) {
      console.error('Erreur lors de la génération du rapport:', error);
      alert('Erreur lors de la génération du rapport PDF. Veuillez réessayer.');
    }
  };

  // Rendu pour Régression
  const renderRegression = () => {
    const data = results.analyses.regression;
    if (!data || !data.models) return <div>Aucune donnée de régression</div>;
    const bestModelR2 = data.best_model ? Number(getR2(data.best_model)) : NaN;
    const bestModelRMSE = data.best_model ? Number(getRMSE(data.best_model)) : NaN;

    return (
      <div className="space-y-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Comparaison des Modèles</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Modèle</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">R² Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">RMSE</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">MAE</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {Object.entries(data.models).map(([modelName, modelData]: [string, any]) => {
                  const r2 = Number(getR2(modelData));
                  const rmse = Number(getRMSE(modelData));
                  const mae = Number(getMAE(modelData));
                  return (
                  <tr key={modelName} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {modelName.replace(/_/g, ' ').toUpperCase()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      <span className={`px-2 py-1 rounded ${r2 > 0.8 ? 'bg-green-100 text-green-800' : r2 > 0.6 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}`}>
                        {formatNumber(r2, 4)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {formatNumber(rmse)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {formatNumber(mae)}
                    </td>
                  </tr>
                );})}
              </tbody>
            </table>
          </div>
        </div>

        {data.best_model && (
          <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">🏆 Meilleur Modèle</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white p-4 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{data.best_model.model}</div>
                <div className="text-sm text-gray-600">Modèle recommandé</div>
              </div>
              <div className="bg-white p-4 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{formatNumber(bestModelR2, 4)}</div>
                <div className="text-sm text-gray-600">Score R²</div>
              </div>
              <div className="bg-white p-4 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{formatNumber(bestModelRMSE)}</div>
                <div className="text-sm text-gray-600">RMSE</div>
              </div>
            </div>
            <div className="mt-4 p-4 bg-white rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">💡 Interprétation</h4>
              <p className="text-sm text-gray-700">
                {bestModelR2 > 0.8 
                  ? "Excellent modèle ! Le modèle explique plus de 80% de la variance des données."
                  : bestModelR2 > 0.6
                  ? "Bon modèle. Le modèle explique entre 60% et 80% de la variance."
                  : "Modèle acceptable, mais pourrait être amélioré. Considérez d'autres features ou méthodes."}
              </p>
            </div>
          </div>
        )}
      </div>
    );
  };

  // Rendu pour Classification
  const renderClassification = () => {
    const data = results.analyses.classification;
    if (!data || !data.models) return <div>Aucune donnée de classification</div>;

    return (
      <div className="space-y-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance des Classifieurs</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Modèle</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Accuracy</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Precision</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Recall</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">F1-Score</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {Object.entries(data.models).map(([modelName, modelData]: [string, any]) => (
                  <tr key={modelName} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {modelName.replace(/_/g, ' ').toUpperCase()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded text-sm ${modelData.accuracy > 0.9 ? 'bg-green-100 text-green-800' : modelData.accuracy > 0.7 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}`}>
                        {formatPercentage(modelData.accuracy * 100)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {formatPercentage(modelData.precision * 100)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {formatPercentage(modelData.recall * 100)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {formatPercentage(modelData.f1_score * 100)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {data.best_model && (
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">🎯 Meilleur Classifieur</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white p-4 rounded-lg col-span-2 md:col-span-1">
                <div className="text-xl font-bold text-purple-600">{data.best_model.model}</div>
                <div className="text-sm text-gray-600">Modèle optimal</div>
              </div>
              <div className="bg-white p-4 rounded-lg">
                <div className="text-2xl font-bold text-green-600">{formatPercentage(data.best_model.accuracy * 100)}</div>
                <div className="text-sm text-gray-600">Accuracy</div>
              </div>
              <div className="bg-white p-4 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{formatPercentage(data.best_model.precision * 100)}</div>
                <div className="text-sm text-gray-600">Precision</div>
              </div>
              <div className="bg-white p-4 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">{formatPercentage(data.best_model.f1_score * 100)}</div>
                <div className="text-sm text-gray-600">F1-Score</div>
              </div>
            </div>
            
            {data.best_model.confusion_matrix && (
              <div className="mt-4 p-4 bg-white rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-3">Matrice de Confusion</h4>
                <div className="overflow-x-auto">
                  <table className="min-w-full border border-gray-300">
                    <tbody>
                      {data.best_model.confusion_matrix.map((row: number[], i: number) => (
                        <tr key={i}>
                          {row.map((cell: number, j: number) => (
                            <td key={j} className={`border border-gray-300 p-3 text-center font-medium ${i === j ? 'bg-green-100 text-green-800' : 'bg-red-50 text-red-600'}`}>
                              {cell}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  // Rendu pour Analyse Discriminante
  const renderDiscriminant = () => {
    const data = results.analyses.discriminant;
    if (!data || !data.models) return <div>Aucune donnée d'analyse discriminante</div>;

    return (
      <div className="space-y-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">LDA vs QDA</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {Object.entries(data.models).map(([modelName, modelData]: [string, any]) => (
              <div key={modelName} className="border border-gray-200 rounded-lg p-4">
                <h4 className="text-md font-semibold text-gray-800 mb-3">
                  {modelName === 'lda' ? 'Linear Discriminant Analysis' : 'Quadratic Discriminant Analysis'}
                </h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Accuracy:</span>
                    <span className="text-sm font-semibold text-gray-900">{formatPercentage(modelData.accuracy * 100)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Precision:</span>
                    <span className="text-sm font-semibold text-gray-900">{formatPercentage(modelData.precision * 100)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Recall:</span>
                    <span className="text-sm font-semibold text-gray-900">{formatPercentage(modelData.recall * 100)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">F1-Score:</span>
                    <span className="text-sm font-semibold text-gray-900">{formatPercentage(modelData.f1_score * 100)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {data.best_model && (
          <div className="bg-gradient-to-r from-indigo-50 to-blue-50 border border-indigo-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">🔬 Recommandation</h3>
            <p className="text-gray-700">
              <strong>{data.best_model.model.toUpperCase()}</strong> est recommandé avec une accuracy de <strong>{formatPercentage(data.best_model.accuracy * 100)}</strong>
            </p>
          </div>
        )}
      </div>
    );
  };

  // Rendu pour Réseaux de Neurones
  const renderNeuralNetworks = () => {
    const data = results.analyses.neuralNetworks;
    if (!data || !data.models) return <div>Aucune donnée de réseaux de neurones</div>;

    return (
      <div className="space-y-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Architectures Neuronales</h3>
          <div className="space-y-4">
            {Object.entries(data.models).map(([modelName, modelData]: [string, any]) => {
              const r2 = Number(getR2(modelData));
              const rmse = Number(getRMSE(modelData));
              const mae = Number(getMAE(modelData));
              return (
              <div key={modelName} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="text-md font-semibold text-gray-800">
                    {modelName.replace(/_/g, ' ').toUpperCase()}
                  </h4>
                  {modelData.task === 'classification' ? (
                    <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                      Classification
                    </span>
                  ) : (
                    <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                      Régression
                    </span>
                  )}
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {modelData.task === 'classification' ? (
                    <>
                      <div className="bg-gray-50 p-3 rounded">
                        <div className="text-lg font-bold text-gray-900">{formatPercentage((getAccuracy(modelData) || 0) * 100)}</div>
                        <div className="text-xs text-gray-600">Accuracy</div>
                      </div>
                      <div className="bg-gray-50 p-3 rounded">
                        <div className="text-lg font-bold text-gray-900">{formatPercentage((getPrecision(modelData) || 0) * 100)}</div>
                        <div className="text-xs text-gray-600">Precision</div>
                      </div>
                      <div className="bg-gray-50 p-3 rounded">
                        <div className="text-lg font-bold text-gray-900">{formatPercentage((getRecall(modelData) || 0) * 100)}</div>
                        <div className="text-xs text-gray-600">Recall</div>
                      </div>
                      <div className="bg-gray-50 p-3 rounded">
                        <div className="text-lg font-bold text-gray-900">{formatPercentage((getF1(modelData) || 0) * 100)}</div>
                        <div className="text-xs text-gray-600">F1-Score</div>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="bg-gray-50 p-3 rounded">
                        <div className="text-lg font-bold text-gray-900">{formatNumber(r2, 4)}</div>
                        <div className="text-xs text-gray-600">R² Score</div>
                      </div>
                      <div className="bg-gray-50 p-3 rounded">
                        <div className="text-lg font-bold text-gray-900">{formatNumber(rmse)}</div>
                        <div className="text-xs text-gray-600">RMSE</div>
                      </div>
                      <div className="bg-gray-50 p-3 rounded">
                        <div className="text-lg font-bold text-gray-900">{formatNumber(mae)}</div>
                        <div className="text-xs text-gray-600">MAE</div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            );})}
          </div>
        </div>
      </div>
    );
  };

  // Rendu pour Séries Temporelles
  const renderTimeSeries = () => {
    const data = results.analyses.timeSeries;
    if (!data || !data.models) return <div>Aucune donnée de séries temporelles</div>;

    return (
      <div className="space-y-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Modèles de Prévision</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Modèle</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">MAE</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">RMSE</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">MAPE</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {Object.entries(data.models).map(([modelName, modelData]: [string, any]) => {
                  const mae = Number(getMAE(modelData));
                  const rmse = Number(getRMSE(modelData));
                  const mape = Number(getMAPE(modelData));
                  return (
                  <tr key={modelName} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {modelName.toUpperCase()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {formatNumber(mae)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {formatNumber(rmse)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {formatPercentage(mape)}
                    </td>
                  </tr>
                );})}
              </tbody>
            </table>
          </div>
        </div>

        {data.best_model && (() => {
          const bestMAE = Number(getMAE(data.best_model));
          const bestMAPE = Number(getMAPE(data.best_model));
          return (
          <div className="bg-gradient-to-r from-cyan-50 to-blue-50 border border-cyan-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">📈 Meilleur Modèle de Prévision</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white p-4 rounded-lg">
                <div className="text-xl font-bold text-cyan-600">{data.best_model.model.toUpperCase()}</div>
                <div className="text-sm text-gray-600">Modèle recommandé</div>
              </div>
              <div className="bg-white p-4 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{formatNumber(bestMAE)}</div>
                <div className="text-sm text-gray-600">MAE (Erreur moyenne)</div>
              </div>
              <div className="bg-white p-4 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">{formatPercentage(bestMAPE)}</div>
                <div className="text-sm text-gray-600">MAPE</div>
              </div>
            </div>
          </div>
        );})()}
      </div>
    );
  };

  // Rendu pour Clustering Avancé
  const renderClustering = () => {
    const data = results.analyses.clusteringAdvanced;
    if (!data || !data.models) return <div>Aucune donnée de clustering</div>;

    return (
      <div className="space-y-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Méthodes de Clustering</h3>
          <div className="space-y-4">
            {Object.entries(data.models).map(([modelName, modelData]: [string, any]) => {
              const nClusters = getNClusters(modelData);
              const silhouette = Number(getSilhouette(modelData));
              const davies = Number(getDaviesBouldin(modelData));
              return (
              <div key={modelName} className="border border-gray-200 rounded-lg p-4">
                <h4 className="text-md font-semibold text-gray-800 mb-3">
                  {modelName.replace(/_/g, ' ').toUpperCase()}
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="bg-gray-50 p-3 rounded">
                    <div className="text-lg font-bold text-gray-900">{nClusters || 'Auto'}</div>
                    <div className="text-xs text-gray-600">Nombre de clusters</div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded">
                    <div className="text-lg font-bold text-gray-900">{formatNumber(silhouette, 3)}</div>
                    <div className="text-xs text-gray-600">Silhouette Score</div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded">
                    <div className="text-lg font-bold text-gray-900">{formatNumber(davies, 3)}</div>
                    <div className="text-xs text-gray-600">Davies-Bouldin</div>
                  </div>
                </div>
              </div>
            );})}
          </div>
        </div>

        {data.best_model && (() => {
          const bmSilhouette = Number(getSilhouette(data.best_model));
          const bmClusters = getNClusters(data.best_model);
          return (
          <div className="bg-gradient-to-r from-teal-50 to-green-50 border border-teal-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">🎨 Meilleure Segmentation</h3>
            <p className="text-gray-700">
              <strong>{data.best_model.model}</strong> avec <strong>{bmClusters} clusters</strong> et un score de silhouette de <strong>{formatNumber(bmSilhouette, 3)}</strong>
            </p>
          </div>
        );})()}
      </div>
    );
  };

  const renderSymptomMatching = () => {
    const data = results.analyses.symptomMatching;
    if (!data) {
      return (
        <div className="p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-yellow-800">Aucune donnée disponible pour l'analyse de correspondance symptômes</p>
        </div>
      );
    }
    
    if (data.error) {
      return (
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 font-semibold">Erreur lors de l'analyse:</p>
          <p className="text-red-700 text-sm mt-2">{data.error}</p>
        </div>
      );
    }
    
    if (!data.success) {
      return (
        <div className="p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-yellow-800">{data.note || 'Analyse non réussie'}</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {/* Résumé */}
        <div className="bg-gradient-to-r from-pink-50 to-purple-50 border border-pink-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Résumé de l'Analyse</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white p-4 rounded-lg border border-pink-100">
              <div className="text-2xl font-bold text-pink-600">{data.total_diseases || 0}</div>
              <div className="text-sm text-gray-600">Maladies analysées</div>
            </div>
            <div className="bg-white p-4 rounded-lg border border-purple-100">
              <div className="text-2xl font-bold text-purple-600">{data.total_symptoms || 0}</div>
              <div className="text-sm text-gray-600">Symptômes évalués</div>
            </div>
            {data.bernoulli_nb?.accuracy ? (
              <div className="bg-white p-4 rounded-lg border border-green-100">
                <div className="text-2xl font-bold text-green-600">
                  {(data.bernoulli_nb.accuracy * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-gray-600">Bernoulli</div>
              </div>
            ) : data.bernoulli_nb?.note && (
              <div className="bg-white p-4 rounded-lg border border-orange-100">
                <div className="text-xs text-orange-700 font-medium">{data.bernoulli_nb.note}</div>
                <div className="text-sm text-gray-600 mt-1">Bernoulli</div>
              </div>
            )}
            {data.multinomial_nb?.accuracy ? (
              <div className="bg-white p-4 rounded-lg border border-blue-100">
                <div className="text-2xl font-bold text-blue-600">
                  {(data.multinomial_nb.accuracy * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-gray-600">Multinomial</div>
              </div>
            ) : data.multinomial_nb?.note && (
              <div className="bg-white p-4 rounded-lg border border-orange-100">
                <div className="text-xs text-orange-700 font-medium">{data.multinomial_nb.note}</div>
                <div className="text-sm text-gray-600 mt-1">Multinomial</div>
              </div>
            )}
          </div>
        </div>

        {/* TF-IDF Top Symptômes */}
        {data.tfidf_analysis?.top_symptoms_global && data.tfidf_analysis.top_symptoms_global.length > 0 && (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Top Symptômes (TF-IDF)</h3>
            <p className="text-xs text-gray-600 mb-4 italic">
              {data.tfidf_analysis.note || 'Symptômes les plus distinctifs basés sur fréquence et variance'}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {data.tfidf_analysis.top_symptoms_global.slice(0, 10).map((item: any, idx: number) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-gradient-to-r from-blue-50 to-blue-50 rounded border border-blue-200 hover:shadow-md transition">
                  <div className="flex items-center flex-1">
                    <div className="w-7 h-7 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold text-xs mr-3 flex-shrink-0">
                      {idx + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className="font-medium text-gray-900 block truncate">{item.symptom}</span>
                      <span className="text-xs text-gray-500">
                        Fréq: {typeof item.frequency_pct === 'number' ? item.frequency_pct.toFixed(1) : item.frequency_pct}% | Var: {typeof item.variance === 'number' ? item.variance.toFixed(4) : item.variance}
                      </span>
                    </div>
                  </div>
                  <span className="text-blue-600 font-semibold text-sm ml-2 flex-shrink-0">
                    {typeof item.tfidf_score === 'number' ? item.tfidf_score.toFixed(3) : item.tfidf_score}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Exemples de Prédictions (Bernoulli) */}
        {data.bernoulli_nb?.example_predictions && (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">🎯 Exemples de Prédictions</h3>
            <div className="space-y-4">
              {data.bernoulli_nb.example_predictions.slice(0, 3).map((example: any, idx: number) => (
                <div key={idx} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                  <div className="mb-2">
                    <span className="text-sm font-medium text-gray-600">Maladie réelle : </span>
                    <span className="font-bold text-gray-900">{example.true_disease}</span>
                  </div>
                  <div className="space-y-2">
                    {example.top_predictions.slice(0, 3).map((pred: any, pidx: number) => (
                      <div key={pidx} className="flex items-center justify-between">
                        <span className="text-sm text-gray-700">{pred.disease}</span>
                        <div className="flex items-center">
                          <div className="w-32 bg-gray-200 rounded-full h-2 mr-2">
                            <div 
                              className={`h-2 rounded-full ${pidx === 0 ? 'bg-green-500' : 'bg-blue-400'}`}
                              style={{ width: `${pred.probability * 100}%` }}
                            />
                          </div>
                          <span className="text-sm font-semibold text-gray-900">
                            {(pred.probability * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Importance des Symptômes */}
        {data.symptom_importance?.top_symptoms && (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Symptômes les Plus Importants</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {data.symptom_importance.top_symptoms.slice(0, 12).map((item: any, idx: number) => (
                <div key={idx} className="p-3 bg-gradient-to-r from-yellow-50 to-orange-50 rounded border border-yellow-200">
                  <div className="text-sm font-medium text-gray-900">{item.symptom}</div>
                  <div className="flex items-center mt-1">
                    <div className="text-xs text-gray-600 mr-2">Score:</div>
                    <div className="text-sm font-bold text-orange-600">
                      {typeof item.importance_score === 'number' ? item.importance_score.toFixed(3) : item.importance_score}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Top Symptoms Per Disease */}
        {data.top_symptoms_per_disease && data.top_symptoms_per_disease.length > 0 && (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Symptômes par Maladie</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {data.top_symptoms_per_disease.slice(0, 10).map((item: any, idx: number) => (
                <div key={idx} className="border border-gray-300 rounded-lg p-4 bg-gradient-to-br from-gray-50 to-white">
                  <h4 className="font-semibold text-gray-900 mb-3 text-sm line-clamp-2">{item.disease || item.name}</h4>
                  <div className="space-y-2">
                    {(item.top_symptoms || item.symptoms || []).slice(0, 5).map((sym: any, sidx: number) => (
                      <div key={sidx} className="flex items-center justify-between text-xs">
                        <span className="text-gray-700 truncate flex-1">{typeof sym === 'string' ? sym : sym.symptom}</span>
                        {typeof sym !== 'string' && sym.frequency && (
                          <span className="text-gray-500 ml-2 flex-shrink-0">
                            {typeof sym.frequency === 'number' ? sym.frequency.toFixed(1) : sym.frequency}%
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Disease Similarity */}
        {data.disease_similarity && (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Similarité Entre Maladies</h3>
            <div className="text-sm text-gray-600 mb-4">
              {data.disease_similarity.total_pairs && (
                <p>Paires de maladies analysées: <span className="font-semibold">{data.disease_similarity.total_pairs}</span></p>
              )}
              {data.disease_similarity.unique_diseases && (
                <p className="mt-1">Maladies uniques: <span className="font-semibold">{data.disease_similarity.unique_diseases}</span></p>
              )}
            </div>
            {data.disease_similarity.similar_pairs && data.disease_similarity.similar_pairs.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {data.disease_similarity.similar_pairs.slice(0, 6).map((pair: any, idx: number) => (
                  <div key={idx} className="p-3 bg-purple-50 rounded border border-purple-200 text-sm">
                    <div className="font-medium text-gray-900">{pair.disease1 || pair.pair?.[0]}</div>
                    <div className="text-gray-600 text-xs">↔ {pair.disease2 || pair.pair?.[1]}</div>
                    {pair.similarity && (
                      <div className="mt-2 flex items-center justify-between">
                        <span className="text-xs text-gray-600">Similarité:</span>
                        <span className="font-semibold text-purple-600">{typeof pair.similarity === 'number' ? pair.similarity.toFixed(3) : pair.similarity}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  const renderSimulator = () => {
    return (
      <div className="space-y-6">
        <PredictionSimulator 
          results={results}
          columns={columns}
          data={data}
        />
      </div>
    );
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverview();
      case 'descriptive':
        return renderDescriptiveStats();
      case 'correlations':
        return renderCorrelations();
      case 'distributions':
        return renderDistributions();
      case 'outliers':
        return renderOutliers();
      case 'categorical':
        return renderCategorical();
      case 'associations':
        return renderAssociations();
      case 'regression':
        return renderRegression();
      case 'classification':
        return renderClassification();
      case 'discriminant':
        return renderDiscriminant();
      case 'neuralNetworks':
        return renderNeuralNetworks();
      case 'timeSeries':
        return renderTimeSeries();
      case 'clustering':
        return renderClustering();
      case 'symptomMatching':
        return renderSymptomMatching();
      case 'simulator':
        return renderSimulator();
      default:
        return renderOverview();
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="mb-6 lg:mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2">
              Résultats de l'analyse
            </h2>
            <p className="text-sm sm:text-base text-gray-600">
              Analyse terminée le {new Date(results.summary.analysisDate).toLocaleString()}
            </p>
          </div>
          <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
            <button
              onClick={copySummary}
              className="inline-flex items-center justify-center px-3 sm:px-4 py-2 border border-gray-300 rounded-lg text-xs sm:text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
            >
              <Copy size={14} className="sm:w-4 sm:h-4 mr-2" />
              Copier synthèse
            </button>
            <button
              onClick={exportResults}
              className="inline-flex items-center justify-center px-3 sm:px-4 py-2 border border-gray-300 rounded-lg text-xs sm:text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
            >
              <Download size={14} className="sm:w-4 sm:h-4 mr-2" />
              Exporter
            </button>
            <button
              onClick={onReset}
              className="inline-flex items-center justify-center px-3 sm:px-4 py-2 border border-blue-300 rounded-lg text-xs sm:text-sm font-medium text-blue-700 bg-blue-50 hover:bg-blue-100 transition-colors"
            >
              <RefreshCw size={14} className="sm:w-4 sm:h-4 mr-2" />
              Nouvelle analyse
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6 sm:mb-8">
        <nav className="-mb-px flex space-x-4 sm:space-x-8 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-3 sm:py-4 px-1 border-b-2 font-medium text-xs sm:text-sm transition-colors duration-200 whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center space-x-1 sm:space-x-2">
                  <Icon size={16} className="sm:w-[18px] sm:h-[18px]" />
                  <span>{tab.name}</span>
                </div>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mb-6 sm:mb-8">
        {renderTabContent()}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row justify-between gap-3 sm:gap-0">
        <button
          onClick={onPrev}
          className="inline-flex items-center justify-center px-4 sm:px-6 py-2 sm:py-3 border border-gray-300 rounded-lg text-sm sm:text-base font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
        >
          <ChevronLeft size={16} className="sm:w-5 sm:h-5 mr-2" />
          Retour aux analyses
        </button>

        <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4">
          <button
            onClick={exportResults}
            className="inline-flex items-center justify-center px-4 sm:px-6 py-2 sm:py-3 border border-green-300 rounded-lg text-sm sm:text-base font-medium text-green-700 bg-green-50 hover:bg-green-100 transition-colors"
          >
            <FileText size={16} className="sm:w-5 sm:h-5 mr-2" />
            Générer un rapport
          </button>
          <button
            onClick={onReset}
            className="inline-flex items-center justify-center px-4 sm:px-6 py-2 sm:py-3 border border-transparent text-sm sm:text-base font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 transition-colors"
          >
            <RefreshCw size={16} className="sm:w-5 sm:h-5 mr-2" />
            Nouvelle analyse
          </button>
        </div>
      </div>
    </div>
  );
};

export default AnalysisResults;