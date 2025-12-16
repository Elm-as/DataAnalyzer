import React, { useState } from 'react';
import {
  AlertCircle,
  CheckCircle,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Trash2,
  Filter,
} from 'lucide-react';
import { DataValidationReport } from '../utils/dataValidator';

interface DataQualityReportProps {
  report: DataValidationReport;
  columns: any[];
  onColumnsUpdated: (columns: any[]) => void;
  onNext: () => void;
  onPrev: () => void;
}

const DataQualityReport: React.FC<DataQualityReportProps> = ({
  report,
  columns,
  onColumnsUpdated,
  onNext,
  onPrev,
}) => {
  const [expandedColumn, setExpandedColumn] = useState<string | null>(null);
  const [showOnlyIssues, setShowOnlyIssues] = useState(false);

  // Colonnes à afficher
  const displayedColumns = showOnlyIssues
    ? report.problematicColumns
    : Object.keys(report.columnAnalysis);

  // Supprimer les colonnes sélectionnées
  const handleRemoveColumns = (colsToRemove: string[]) => {
    const updated = columns.filter(col => !colsToRemove.includes(col.name));
    onColumnsUpdated(updated);
  };

  // Supprimer les colonnes problématiques
  const handleRemoveProblematicColumns = () => {
    if (confirm(`Supprimer ${report.problematicColumns.length} colonnes problématiques ?`)) {
      handleRemoveColumns(report.problematicColumns);
    }
  };

  const getQualityColor = (completeness: number) => {
    if (completeness >= 90) return 'text-green-600 bg-green-50 border-green-200';
    if (completeness >= 70) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (completeness >= 50) return 'text-orange-600 bg-orange-50 border-orange-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getIssueIcon = (nullPercentage: number, variance: number, uniqueValues: number) => {
    if (nullPercentage === 100) return '🚫';
    if (nullPercentage >= 70) return '❌';
    if (nullPercentage >= 50) return '⚠️';
    if (variance === 0 && uniqueValues > 1) return '⚠️';
    if (uniqueValues < 3) return '⚠️';
    return '✅';
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="max-w-5xl mx-auto">
        {/* En-tête */}
        <div className="mb-8">
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-4">
            📊 Rapport de Qualité des Données
          </h2>
          <p className="text-gray-600">
            Analyse de vos données pour optimiser les futures analyses
          </p>
        </div>

        {/* Résumé global */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="p-4 rounded-lg border border-gray-200 bg-white">
            <div className="text-sm text-gray-600">Complétude</div>
            <div className={`text-2xl font-bold ${
              report.quality.completeness >= 80 ? 'text-green-600' : 'text-orange-600'
            }`}>
              {report.quality.completeness.toFixed(1)}%
            </div>
          </div>

          <div className="p-4 rounded-lg border border-gray-200 bg-white">
            <div className="text-sm text-gray-600">Valeurs N/A</div>
            <div className={`text-2xl font-bold ${
              report.quality.nullPercentage < 20 ? 'text-green-600' : 'text-red-600'
            }`}>
              {report.quality.nullPercentage.toFixed(1)}%
            </div>
          </div>

          <div className="p-4 rounded-lg border border-gray-200 bg-white">
            <div className="text-sm text-gray-600">Colonnes</div>
            <div className="text-2xl font-bold text-blue-600">
              {Object.keys(report.columnAnalysis).length}
            </div>
          </div>

          <div className="p-4 rounded-lg border border-gray-200 bg-white">
            <div className="text-sm text-gray-600">Doublons</div>
            <div className={`text-2xl font-bold ${
              report.quality.duplicateRows === 0 ? 'text-green-600' : 'text-orange-600'
            }`}>
              {report.quality.duplicateRows}
            </div>
          </div>
        </div>

        {/* Alertes */}
        {report.issues.length > 0 && (
          <div className="mb-6 p-4 rounded-lg border-l-4 border-red-500 bg-red-50">
            <div className="flex items-start gap-3">
              <AlertCircle size={20} className="text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-800 mb-2">⛔ Problèmes Critiques</h3>
                <ul className="text-red-700 text-sm space-y-1">
                  {report.issues.map((issue, i) => (
                    <li key={i}>• {issue}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Avertissements */}
        {report.warnings.length > 0 && (
          <div className="mb-6 p-4 rounded-lg border-l-4 border-orange-500 bg-orange-50">
            <div className="flex items-start gap-3">
              <AlertTriangle size={20} className="text-orange-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-orange-800 mb-2">⚠️ Avertissements</h3>
                <ul className="text-orange-700 text-sm space-y-1">
                  {report.warnings.map((warning, i) => (
                    <li key={i}>• {warning}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Suggestions */}
        {report.suggestions.length > 0 && (
          <div className="mb-6 p-4 rounded-lg border-l-4 border-blue-500 bg-blue-50">
            <div className="flex items-start gap-3">
              <CheckCircle size={20} className="text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-blue-800 mb-2">💡 Suggestions</h3>
                <ul className="text-blue-700 text-sm space-y-1">
                  {report.suggestions.map((suggestion, i) => (
                    <li key={i}>• {suggestion}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Analyse par colonne */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">
              🔍 Analyse Détaillée des Colonnes
            </h3>
            <button
              onClick={() => setShowOnlyIssues(!showOnlyIssues)}
              className="flex items-center gap-2 px-3 py-1 text-sm rounded-lg border border-gray-300 hover:bg-gray-50 transition"
            >
              <Filter size={16} />
              {showOnlyIssues ? 'Toutes' : 'Problèmes'}
            </button>
          </div>

          {report.problematicColumns.length > 0 && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 flex items-center justify-between">
              <span className="text-sm text-red-700">
                {report.problematicColumns.length} colonnes problématiques détectées
              </span>
              <button
                onClick={handleRemoveProblematicColumns}
                className="flex items-center gap-2 px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 transition"
              >
                <Trash2 size={16} />
                Supprimer
              </button>
            </div>
          )}

          <div className="space-y-3">
            {displayedColumns.map((colName) => {
              const analysis = report.columnAnalysis[colName];
              const isExpanded = expandedColumn === colName;

              return (
                <div
                  key={colName}
                  className={`rounded-lg border transition ${
                    analysis.issue
                      ? 'border-red-200 bg-red-50'
                      : 'border-gray-200 bg-white'
                  }`}
                >
                  {/* En-tête de colonne */}
                  <button
                    onClick={() => setExpandedColumn(isExpanded ? null : colName)}
                    className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition text-left"
                  >
                    <div className="flex items-center gap-3 flex-1">
                      <span className="text-xl">
                        {getIssueIcon(
                          analysis.nullPercentage,
                          analysis.variance,
                          analysis.uniqueValues
                        )}
                      </span>
                      <div className="flex-1">
                        <div className="font-medium text-gray-800">{colName}</div>
                        <div className="text-sm text-gray-600">
                          {analysis.type} • {analysis.uniqueValues} valeurs uniques
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <div className={`text-sm font-medium ${
                          analysis.nullPercentage < 20
                            ? 'text-green-600'
                            : analysis.nullPercentage < 50
                            ? 'text-orange-600'
                            : 'text-red-600'
                        }`}>
                          {analysis.nullPercentage.toFixed(1)}% N/A
                        </div>
                        <div className="text-xs text-gray-500">
                          {(analysis.nullCount)} valeurs manquantes
                        </div>
                      </div>
                      {isExpanded ? (
                        <ChevronUp size={20} className="text-gray-400" />
                      ) : (
                        <ChevronDown size={20} className="text-gray-400" />
                      )}
                    </div>
                  </button>

                  {/* Détails de colonne */}
                  {isExpanded && (
                    <div className="border-t border-gray-200 p-4 bg-gray-50 text-sm">
                      {analysis.issue && (
                        <div className="mb-3 p-2 rounded bg-red-100 border border-red-200 text-red-700">
                          {analysis.issue}
                        </div>
                      )}
                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div>
                          <div className="text-gray-600">Complétude</div>
                          <div className="font-semibold">
                            {(100 - analysis.nullPercentage).toFixed(1)}%
                          </div>
                        </div>
                        <div>
                          <div className="text-gray-600">Variance</div>
                          <div className="font-semibold">
                            {analysis.variance.toFixed(2)}
                          </div>
                        </div>
                      </div>
                      <div className="w-full bg-gray-300 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition"
                          style={{
                            width: `${100 - analysis.nullPercentage}%`
                          }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Boutons d'action */}
        <div className="flex flex-col sm:flex-row gap-3 justify-between">
          <button
            onClick={onPrev}
            className="px-6 py-3 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium transition"
          >
            ← Retour
          </button>

          <div className="flex gap-3">
            {report.problematicColumns.length > 0 && (
              <button
                onClick={handleRemoveProblematicColumns}
                className="px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 font-medium transition flex items-center gap-2"
              >
                <Trash2 size={18} />
                Nettoyer
              </button>
            )}
            <button
              onClick={onNext}
              disabled={!report.isValid && report.quality.nullPercentage > 50}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Continuer →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataQualityReport;
