import React, { useState } from 'react';
import { RefreshCw, Check, X, Wand2 } from 'lucide-react';
import { DataColumn } from '../App';

interface TypeConverterProps {
  columns: DataColumn[];
  data: any[];
  onConvert: (updatedData: any[], updatedColumns: DataColumn[]) => void;
  onClose: () => void;
}

const TypeConverter: React.FC<TypeConverterProps> = ({
  columns,
  data,
  onConvert,
  onClose,
}) => {
  const [selectedColumns, setSelectedColumns] = useState<Set<string>>(new Set());
  const [targetTypes, setTargetTypes] = useState<Map<string, string>>(new Map());
  const [converting, setConverting] = useState(false);

  const availableTypes = [
    { value: 'boolean', label: 'Booléen', icon: '✓', description: 'true/false, 0/1, oui/non' },
    { value: 'number', label: 'Numérique', icon: '🔢', description: 'Nombres entiers ou décimaux' },
    { value: 'string', label: 'Texte', icon: '📝', description: 'Chaîne de caractères' },
    { value: 'date', label: 'Date', icon: '📅', description: 'Date et heure' },
    { value: 'categorical', label: 'Catégorielle', icon: '🏷️', description: 'Valeurs discrètes' },
  ];

  const toggleColumn = (columnName: string, currentType: string) => {
    const newSelected = new Set(selectedColumns);
    if (newSelected.has(columnName)) {
      newSelected.delete(columnName);
      const newTypes = new Map(targetTypes);
      newTypes.delete(columnName);
      setTargetTypes(newTypes);
    } else {
      newSelected.add(columnName);
      // Par défaut, suggérer un type différent du type actuel
      const newTypes = new Map(targetTypes);
      if (currentType !== 'boolean') {
        newTypes.set(columnName, 'boolean');
      } else {
        newTypes.set(columnName, 'number');
      }
      setTargetTypes(newTypes);
    }
    setSelectedColumns(newSelected);
  };

  const setTargetType = (columnName: string, type: string) => {
    const newTypes = new Map(targetTypes);
    newTypes.set(columnName, type);
    setTargetTypes(newTypes);
  };

  const convertValue = (value: any, targetType: string): any => {
    if (value === null || value === undefined || value === '') {
      return null;
    }

    switch (targetType) {
      case 'boolean':
        if (typeof value === 'boolean') return value;
        if (value === 0 || value === '0' || String(value).toLowerCase() === 'false' || 
            String(value).toLowerCase() === 'non' || String(value).toLowerCase() === 'no') {
          return false;
        }
        if (value === 1 || value === '1' || String(value).toLowerCase() === 'true' || 
            String(value).toLowerCase() === 'oui' || String(value).toLowerCase() === 'yes') {
          return true;
        }
        return Boolean(value);

      case 'number':
        const num = Number(value);
        return isNaN(num) ? null : num;

      case 'string':
        return String(value);

      case 'date':
        const date = new Date(value);
        return isNaN(date.getTime()) ? null : date.toISOString();

      case 'categorical':
        return String(value);

      default:
        return value;
    }
  };

  const handleConvert = () => {
    setConverting(true);

    try {
      // Convertir les données
      const convertedData = data.map(row => {
        const newRow = { ...row };
        selectedColumns.forEach(colName => {
          const targetType = targetTypes.get(colName);
          if (targetType) {
            newRow[colName] = convertValue(row[colName], targetType);
          }
        });
        return newRow;
      });

      // Mettre à jour les colonnes
      const updatedColumns = columns.map(col => {
        if (selectedColumns.has(col.name) && targetTypes.has(col.name)) {
          return {
            ...col,
            type: targetTypes.get(col.name) as any,
          };
        }
        return col;
      });

      onConvert(convertedData, updatedColumns);
    } finally {
      setConverting(false);
    }
  };

  const getTypeIcon = (type: string) => {
    const typeObj = availableTypes.find(t => t.value === type);
    return typeObj?.icon || '📝';
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'number': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'date': return 'text-green-600 bg-green-50 border-green-200';
      case 'boolean': return 'text-purple-600 bg-purple-50 border-purple-200';
      case 'categorical': return 'text-orange-600 bg-orange-50 border-orange-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Wand2 className="w-6 h-6 text-purple-600" />
              <h3 className="text-xl font-bold text-gray-900">
                Convertir les types de colonnes
              </h3>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
          <p className="text-sm text-gray-600 mt-2">
            Sélectionnez les colonnes à convertir et choisissez le type de données cible
          </p>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          <div className="space-y-3">
            {columns.map((column) => (
              <div
                key={column.name}
                className={`border rounded-lg p-4 transition-all ${
                  selectedColumns.has(column.name)
                    ? 'border-purple-300 bg-purple-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-start space-x-4">
                  {/* Checkbox */}
                  <input
                    type="checkbox"
                    checked={selectedColumns.has(column.name)}
                    onChange={() => toggleColumn(column.name, column.type)}
                    className="mt-1 h-5 w-5 text-purple-600 rounded focus:ring-purple-500"
                  />

                  {/* Column Info */}
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-lg">{getTypeIcon(column.type)}</span>
                      <span className="font-semibold text-gray-900">{column.name}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getTypeColor(column.type)}`}>
                        {column.type}
                      </span>
                    </div>

                    {/* Type Selection (visible si sélectionné) */}
                    {selectedColumns.has(column.name) && (
                      <div className="mt-3">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Convertir en :
                        </label>
                        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                          {availableTypes.map((type) => (
                            <button
                              key={type.value}
                              onClick={() => setTargetType(column.name, type.value)}
                              className={`flex items-center space-x-2 px-3 py-2 rounded-lg border transition-all ${
                                targetTypes.get(column.name) === type.value
                                  ? 'border-purple-600 bg-purple-50 text-purple-700'
                                  : 'border-gray-200 hover:border-gray-300 text-gray-700'
                              }`}
                            >
                              <span>{type.icon}</span>
                              <span className="text-sm font-medium">{type.label}</span>
                            </button>
                          ))}
                        </div>
                        {targetTypes.get(column.name) && (
                          <p className="text-xs text-gray-500 mt-2">
                            {availableTypes.find(t => t.value === targetTypes.get(column.name))?.description}
                          </p>
                        )}
                      </div>
                    )}

                    {/* Sample Values */}
                    {column.sample && column.sample.length > 0 && (
                      <div className="mt-2 text-xs text-gray-500">
                        Exemples: {column.sample.slice(0, 3).join(', ')}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              {selectedColumns.size} colonne{selectedColumns.size > 1 ? 's' : ''} sélectionnée{selectedColumns.size > 1 ? 's' : ''}
            </div>
            <div className="flex space-x-3">
              <button
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
              >
                Annuler
              </button>
              <button
                onClick={handleConvert}
                disabled={selectedColumns.size === 0 || converting}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {converting ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Conversion...
                  </>
                ) : (
                  <>
                    <Check className="w-4 h-4 mr-2" />
                    Convertir {selectedColumns.size > 0 && `(${selectedColumns.size})`}
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TypeConverter;
