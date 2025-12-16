import React, { useState, useMemo } from 'react';
import { ChevronDown, ChevronUp, Search, Check, X, AlertTriangle } from 'lucide-react';
import { DataColumn } from '../App';
import { DataValidator } from '../utils/dataValidator';

interface ColumnSelectorProps {
  columns: DataColumn[];
  data: any[];
  onColumnsSelected: (columns: DataColumn[]) => void;
  onNext: () => void;
  onPrev: () => void;
  maxColumns?: number;
}

type SortBy = 'name' | 'quality' | 'type';

const ColumnSelector: React.FC<ColumnSelectorProps> = ({
  columns,
  data,
  onColumnsSelected,
  onNext,
  onPrev,
  maxColumns = 50,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<SortBy>('quality');
  const [selectedColumns, setSelectedColumns] = useState<Set<string>>(
    new Set(columns.filter(c => c.isSelected).map(c => c.name))
  );

  // Valider les données et obtenir les scores de qualité
  const qualityReport = useMemo(() => {
    return DataValidator.validate(data, columns.map(c => c.name));
  }, [data, columns]);

  // Colonnes triées
  const sortedColumns = useMemo(() => {
    let sorted = [...columns];

    // Filtrer par recherche
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      sorted = sorted.filter(col =>
        col.name.toLowerCase().includes(query)
      );
    }

    // Trier
    sorted.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'type':
          return a.type.localeCompare(b.type);
        case 'quality':
        default: {
          const analysisA = qualityReport.columnAnalysis[a.name];
          const analysisB = qualityReport.columnAnalysis[b.name];
          
          // Score = complétude - pénalité pour manque de variance
          const scoreA = (1 - analysisA.nullPercentage / 100) - (analysisA.variance === 0 ? 0.2 : 0);
          const scoreB = (1 - analysisB.nullPercentage / 100) - (analysisB.variance === 0 ? 0.2 : 0);
          
          return scoreB - scoreA;
        }
      }
    });

    return sorted;
  }, [columns, searchQuery, sortBy, qualityReport]);

  // Gérer la sélection
  const toggleColumn = (colName: string) => {
    const newSelected = new Set(selectedColumns);
    if (newSelected.has(colName)) {
      newSelected.delete(colName);
    } else {
      // Vérifier la limite
      if (newSelected.size >= maxColumns) {
        alert(`Maximum ${maxColumns} colonnes autorisées`);
        return;
      }
      newSelected.add(colName);
    }
    setSelectedColumns(newSelected);
  };

  // Sélectionner les meilleures colonnes
  const selectBestColumns = () => {
    const best = DataValidator.suggestBestColumns(data, maxColumns, 0.7);
    setSelectedColumns(new Set(best));
  };

  // Sélectionner tout
  const selectAll = () => {
    const allNames = sortedColumns
      .slice(0, maxColumns)
      .map(c => c.name);
    setSelectedColumns(new Set(allNames));
  };

  // Désélectionner tout
  const deselectAll = () => {
    setSelectedColumns(new Set());
  };

  // Appliquer la sélection
  const handleApply = () => {
    if (selectedColumns.size === 0) {
      alert('Sélectionnez au moins une colonne');
      return;
    }

    const updated = columns.map(col => ({
      ...col,
      isSelected: selectedColumns.has(col.name),
    }));

    onColumnsSelected(updated);
  };

  // Statistiques
  const numericColumns = sortedColumns.filter(c => c.type === 'number');
  const categoricalColumns = sortedColumns.filter(c => c.type === 'categorical');

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="max-w-4xl mx-auto">
        {/* En-tête */}
        <div className="mb-8">
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-2">
            🎯 Sélection des Colonnes
          </h2>
          <p className="text-gray-600">
            Choisissez les colonnes à analyser ({selectedColumns.size}/{maxColumns})
          </p>
        </div>

        {/* Avertissement si trop de colonnes */}
        {columns.length > maxColumns && (
          <div className="mb-6 p-4 rounded-lg border-l-4 border-orange-500 bg-orange-50">
            <div className="flex items-start gap-3">
              <AlertTriangle size={20} className="text-orange-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-orange-800">Trop de colonnes</h3>
                <p className="text-sm text-orange-700 mt-1">
                  Vous avez {columns.length} colonnes mais le maximum recommandé est {maxColumns}.
                  Sélectionnez les colonnes pertinentes pour améliorer les performances.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Barre de contrôle */}
        <div className="mb-6 space-y-4">
          {/* Recherche */}
          <div className="relative">
            <Search size={18} className="absolute left-3 top-3 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher des colonnes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Tri et boutons */}
          <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortBy)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
            >
              <option value="quality">Trier par qualité ⭐</option>
              <option value="name">Trier par nom A→Z</option>
              <option value="type">Trier par type</option>
            </select>

            <div className="flex gap-2">
              <button
                onClick={selectBestColumns}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium transition text-sm"
              >
                ✨ Meilleures
              </button>
              <button
                onClick={selectAll}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition text-sm"
              >
                ✓ Tout
              </button>
              <button
                onClick={deselectAll}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 font-medium transition text-sm"
              >
                ✕ Aucun
              </button>
            </div>
          </div>

          {/* Statistiques */}
          <div className="grid grid-cols-3 sm:grid-cols-6 gap-2 text-xs">
            <div className="p-2 rounded bg-blue-50 text-center">
              <div className="font-semibold text-blue-600">{columns.length}</div>
              <div className="text-blue-600">Colonnes</div>
            </div>
            <div className="p-2 rounded bg-green-50 text-center">
              <div className="font-semibold text-green-600">{numericColumns.length}</div>
              <div className="text-green-600">Numériques</div>
            </div>
            <div className="p-2 rounded bg-orange-50 text-center">
              <div className="font-semibold text-orange-600">{categoricalColumns.length}</div>
              <div className="text-orange-600">Catég.</div>
            </div>
            <div className="p-2 rounded bg-purple-50 text-center">
              <div className="font-semibold text-purple-600">{selectedColumns.size}</div>
              <div className="text-purple-600">Sélect.</div>
            </div>
            <div className="p-2 rounded bg-red-50 text-center">
              <div className="font-semibold text-red-600">{qualityReport.problematicColumns.length}</div>
              <div className="text-red-600">Prob.</div>
            </div>
            <div className="p-2 rounded bg-yellow-50 text-center">
              <div className="font-semibold text-yellow-600">
                {qualityReport.quality.nullPercentage.toFixed(0)}%
              </div>
              <div className="text-yellow-600">N/A</div>
            </div>
          </div>
        </div>

        {/* Liste des colonnes */}
        <div className="space-y-2 mb-8 max-h-96 overflow-y-auto">
          {sortedColumns.map((col) => {
            const analysis = qualityReport.columnAnalysis[col.name];
            const isSelected = selectedColumns.has(col.name);
            const isProblematic = qualityReport.problematicColumns.includes(col.name);

            return (
              <label
                key={col.name}
                className={`flex items-center gap-3 p-3 rounded-lg border-2 cursor-pointer transition ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50'
                    : isProblematic
                    ? 'border-red-200 bg-red-50 hover:border-red-300'
                    : 'border-gray-200 bg-white hover:border-blue-300'
                }`}
              >
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => toggleColumn(col.name)}
                  className="w-5 h-5 rounded"
                />

                <div className="flex-1 min-w-0">
                  <div className="font-medium text-gray-800 truncate">{col.name}</div>
                  <div className="text-xs text-gray-600">
                    {col.type} • {analysis.uniqueValues} valeurs uniques
                  </div>
                </div>

                <div className="flex-shrink-0 text-right">
                  <div className={`text-sm font-medium ${
                    analysis.nullPercentage < 20
                      ? 'text-green-600'
                      : analysis.nullPercentage < 50
                      ? 'text-orange-600'
                      : 'text-red-600'
                  }`}>
                    {analysis.nullPercentage.toFixed(0)}%
                  </div>
                  <div className="text-xs text-gray-500">N/A</div>
                </div>

                {isSelected && (
                  <Check size={20} className="flex-shrink-0 text-blue-600" />
                )}
              </label>
            );
          })}
        </div>

        {/* Boutons d'action */}
        <div className="flex flex-col sm:flex-row gap-3 justify-between">
          <button
            onClick={onPrev}
            className="px-6 py-3 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium transition"
          >
            ← Retour
          </button>

          <button
            onClick={handleApply}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition"
          >
            Continuer ({selectedColumns.size}) →
          </button>
        </div>
      </div>
    </div>
  );
};

export default ColumnSelector;
