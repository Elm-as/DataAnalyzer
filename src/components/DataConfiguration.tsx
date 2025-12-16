import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Settings, ToggleLeft, ToggleRight, Hash, Calendar, Type, Check } from 'lucide-react';
import { DataColumn } from '../App';

interface DataConfigurationProps {
  columns: DataColumn[];
  onColumnsUpdated: (columns: DataColumn[]) => void;
  onNext: () => void;
  onPrev: () => void;
}

const DataConfiguration: React.FC<DataConfigurationProps> = ({
  columns,
  onColumnsUpdated,
  onNext,
  onPrev,
}) => {
  const [localColumns, setLocalColumns] = useState<DataColumn[]>([...columns]);

  const updateColumn = (index: number, updates: Partial<DataColumn>) => {
    const updatedColumns = [...localColumns];
    updatedColumns[index] = { ...updatedColumns[index], ...updates };
    setLocalColumns(updatedColumns);
    onColumnsUpdated(updatedColumns);
  };

  const toggleColumnSelection = (index: number) => {
    updateColumn(index, { isSelected: !localColumns[index].isSelected });
  };

  const changeColumnType = (index: number, type: DataColumn['type']) => {
    updateColumn(index, { type });
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'number': return <Hash size={16} />;
      case 'date': return <Calendar size={16} />;
      case 'boolean': return <Check size={16} />;
      case 'categorical': return <span className="text-orange-600">🏷️</span>;
      default: return <Type size={16} />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'number': return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'date': return 'bg-green-100 text-green-800 border-green-300';
      case 'boolean': return 'bg-purple-100 text-purple-800 border-purple-300';
      case 'categorical': return 'bg-orange-100 text-orange-800 border-orange-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const selectedCount = localColumns.filter(col => col.isSelected).length;

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="mb-6 lg:mb-8">
        <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2">
          Configuration des colonnes
        </h2>
        <p className="text-sm sm:text-base text-gray-600">
          Ajustez les types de données et sélectionnez les colonnes à analyser
        </p>
        
        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center">
            <Settings size={18} className="sm:w-5 sm:h-5 text-blue-600 mr-3 flex-shrink-0" />
            <div>
              <h3 className="text-sm sm:text-base font-semibold text-blue-900">
                {selectedCount} colonnes sélectionnées pour l'analyse
              </h3>
              <p className="text-sm text-blue-700">
                Les colonnes désélectionnées seront ignorées dans les analyses
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-3 sm:space-y-4 mb-6 sm:mb-8">
        {localColumns.map((column, index) => (
          <div
            key={index}
            className={`border rounded-lg p-4 sm:p-6 transition-all duration-200 ${
              column.isSelected
                ? 'border-blue-300 bg-blue-50'
                : 'border-gray-200 bg-gray-50'
            }`}
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-center space-x-3 sm:space-x-4">
                <button
                  onClick={() => toggleColumnSelection(index)}
                  className="transition-colors duration-200"
                >
                  {column.isSelected ? (
                    <ToggleRight size={28} className="sm:w-8 sm:h-8 text-blue-600" />
                  ) : (
                    <ToggleLeft size={28} className="sm:w-8 sm:h-8 text-gray-400" />
                  )}
                </button>

                <div>
                  <h3 className={`text-base sm:text-lg font-semibold transition-colors ${
                    column.isSelected ? 'text-blue-900' : 'text-gray-600'
                  }`}>
                    {column.name}
                  </h3>
                  <p className={`text-sm transition-colors ${
                    column.isSelected ? 'text-blue-700' : 'text-gray-500'
                  }`}>
                    {column.sample?.slice(0, 3).join(', ')}
                    {column.sample && column.sample.length > 3 && '...'}
                  </p>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-3">
                <span className="text-xs sm:text-sm text-gray-600">Type:</span>
                <div className="flex flex-wrap gap-1 sm:gap-2">
                  {(['string', 'number', 'date', 'boolean', 'categorical'] as const).map((type) => (
                    <button
                      key={type}
                      onClick={() => changeColumnType(index, type)}
                      disabled={!column.isSelected}
                      className={`px-2 sm:px-3 py-1 sm:py-2 rounded-lg text-xs sm:text-sm font-medium border transition-all duration-200 ${
                        column.type === type
                          ? getTypeColor(type)
                          : column.isSelected
                          ? 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                          : 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed'
                      }`}
                    >
                      <div className="flex items-center space-x-0.5 sm:space-x-1">
                        {getTypeIcon(type)}
                        <span className="capitalize">{type}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {column.isSelected && (
              <div className="mt-3 sm:mt-4 pt-3 sm:pt-4 border-t border-blue-200">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 text-xs sm:text-sm">
                  <div>
                    <span className="font-medium text-blue-900">Échantillon:</span>
                    <div className="text-blue-700">
                      {column.sample?.slice(0, 2).map((val, i) => (
                        <div key={i} className="truncate">{val?.toString() || 'null'}</div>
                      ))}
                    </div>
                  </div>
                  {column.type === 'categorical' && column.uniqueValues && (
                    <div>
                      <span className="font-medium text-blue-900">Catégories:</span>
                      <div className="text-blue-700">
                        {column.uniqueValues.slice(0, 3).map((val, i) => (
                          <div key={i} className="truncate text-xs">{val?.toString()}</div>
                        ))}
                        {column.uniqueValues.length > 3 && (
                          <div className="text-xs text-blue-500">+{column.uniqueValues.length - 3} autres</div>
                        )}
                      </div>
                    </div>
                  )}
                  <div>
                    <span className="font-medium text-blue-900">Type détecté:</span>
                    <div className={`inline-flex items-center mt-1 px-2 py-1 rounded-full text-xs font-medium ${getTypeColor(column.type)}`}>
                      {getTypeIcon(column.type)}
                      <span className="ml-0.5 sm:ml-1 capitalize">{column.type}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {selectedCount === 0 && (
        <div className="mb-8 p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center">
            <div className="text-yellow-600 mr-3">⚠️</div>
            <div>
              <h3 className="font-semibold text-yellow-800">
                Aucune colonne sélectionnée
              </h3>
              <p className="text-sm text-yellow-700">
                Veuillez sélectionner au moins une colonne pour continuer l'analyse
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Summary */}
      <div className="mb-6 sm:mb-8 p-4 sm:p-6 bg-white border border-gray-200 rounded-lg">
        <h3 className="text-sm sm:text-base font-semibold text-gray-900 mb-3 sm:mb-4">Résumé de la configuration</h3>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          {(['number', 'categorical', 'string', 'date'] as const).map((type) => {
            const count = localColumns.filter(col => col.isSelected && col.type === type).length;
            return (
              <div key={type} className={`p-3 sm:p-4 rounded-lg border ${getTypeColor(type)}`}>
                <div className="flex items-center space-x-1 sm:space-x-2">
                  {getTypeIcon(type)}
                  <span className="text-xs sm:text-sm font-medium capitalize">{type}</span>
                </div>
                <div className="text-xl sm:text-2xl font-bold">{count}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row justify-between gap-3 sm:gap-0">
        <button
          onClick={onPrev}
          className="inline-flex items-center justify-center px-4 sm:px-6 py-2 sm:py-3 border border-gray-300 rounded-lg text-sm sm:text-base font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
        >
          <ChevronLeft size={16} className="sm:w-5 sm:h-5 mr-2" />
          Retour
        </button>

        <button
          onClick={onNext}
          disabled={selectedCount === 0}
          className="inline-flex items-center justify-center px-4 sm:px-6 py-2 sm:py-3 border border-transparent text-sm sm:text-base font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Choisir les analyses
          <ChevronRight size={16} className="sm:w-5 sm:h-5 ml-2" />
        </button>
      </div>
    </div>
  );
};

export default DataConfiguration;