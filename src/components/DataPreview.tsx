import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Eye, Settings, CheckCircle, Wand2 } from 'lucide-react';
import { DataColumn } from '../App';
import { api } from '../api/backend';
import TypeConverter from './TypeConverter';

interface DataPreviewProps {
  data: any[];
  onColumnsDetected: (columns: DataColumn[]) => void;
  onDataUpdated?: (data: any[]) => void;
  onNext: () => void;
  onPrev: () => void;
}

const DataPreview: React.FC<DataPreviewProps> = ({
  data,
  onColumnsDetected,
  onDataUpdated,
  onNext,
  onPrev,
}) => {
  const [currentPage, setCurrentPage] = useState(0);
  const [detectedColumns, setDetectedColumns] = useState<DataColumn[]>([]);
  const [showTypeConverter, setShowTypeConverter] = useState(false);
  const [autoDetecting, setAutoDetecting] = useState(false);
  const [autoDetectionDone, setAutoDetectionDone] = useState(false);
  const [booleanDetectionResult, setBooleanDetectionResult] = useState<any>(null);
  const [currentData, setCurrentData] = useState(data);
  const rowsPerPage = 10;

  useEffect(() => {
    if (data.length > 0 && detectedColumns.length === 0) {
      const firstRow = data[0];
      const columns: DataColumn[] = Object.keys(firstRow).map((key) => {
        const sampleValues = data.slice(0, 100).map((row) => row[key]);
        const nonNullValues = sampleValues.filter((val) => val != null && val !== '');
        
        let type: 'number' | 'string' | 'date' | 'boolean' | 'categorical' = 'string';
        
        // Detect type based on sample values
        if (nonNullValues.length > 0) {
          // PREMIÈRE: Détection booléenne (0/1, true/false)
          const booleanCount = nonNullValues.filter((val) => 
            val === 0 || val === 1 || val === '0' || val === '1' ||
            val === true || val === false || val === 'true' || val === 'false' ||
            String(val).toLowerCase() === 'yes' || String(val).toLowerCase() === 'no' ||
            String(val).toLowerCase() === 'oui' || String(val).toLowerCase() === 'non'
          ).length;
          
          // DEUXIÈME: Détection numérique
          const numericCount = nonNullValues.filter((val) => !isNaN(Number(val))).length;
          
          // TROISIÈME: Détection date
          const dateCount = nonNullValues.filter((val) => 
            !isNaN(Date.parse(val)) && isNaN(Number(val))
          ).length;
          
          // Check for categorical data (limited unique values)
          const uniqueValues = [...new Set(nonNullValues)];
          const uniqueRatio = uniqueValues.length / nonNullValues.length;

          if (booleanCount / nonNullValues.length > 0.95) {
            type = 'boolean';
          } else if (numericCount / nonNullValues.length > 0.8) {
            type = 'number';
          } else if (dateCount / nonNullValues.length > 0.8) {
            type = 'date';
          } else if (uniqueRatio < 0.1 && uniqueValues.length < 20) {
            type = 'categorical';
          }
        }

        return {
          name: key,
          type,
          isHeader: true,
          isSelected: !(/^(index|id|row|num|n°|\d+)$/i.test(key)), // Skip typical index columns
          sample: nonNullValues.slice(0, 5),
          uniqueValues: type === 'categorical' ? [...new Set(nonNullValues)].slice(0, 10) : undefined,
        };
      });

      setDetectedColumns(columns);
      onColumnsDetected(columns);

      // Détection automatique des colonnes booléennes (0/1) via le backend
      if (!autoDetectionDone) {
        detectBooleansAutomatically(data, columns);
      }
    }
  }, [data]);

  const detectBooleansAutomatically = async (dataToAnalyze: any[], currentColumns: DataColumn[]) => {
    try {
      setAutoDetecting(true);
      const result = await api.detectBooleans(dataToAnalyze);
      
      if (result.boolean_columns && result.boolean_columns.length > 0) {
        setBooleanDetectionResult(result);
        
        // Mettre à jour automatiquement les données et colonnes
        setCurrentData(result.data);
        
        const updatedColumns = currentColumns.map(col => {
          if (result.boolean_columns.includes(col.name)) {
            return { ...col, type: 'boolean' as any };
          }
          return col;
        });
        
        setDetectedColumns(updatedColumns);
        onColumnsDetected(updatedColumns);
        
        // Notifier App.tsx des données mises à jour
        if (onDataUpdated) {
          onDataUpdated(result.data);
        }
        
        console.log(`✅ ${result.converted_count} colonnes booléennes détectées et converties automatiquement`);
      }
      
      setAutoDetectionDone(true);
    } catch (error) {
      console.error('Erreur lors de la détection automatique:', error);
      setAutoDetectionDone(true);
    } finally {
      setAutoDetecting(false);
    }
  };

  const totalPages = Math.ceil(currentData.length / rowsPerPage);
  const paginatedData = currentData.slice(
    currentPage * rowsPerPage,
    (currentPage + 1) * rowsPerPage
  );

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'number': return '🔢';
      case 'date': return '📅';
      case 'boolean': return '✓';
      case 'categorical': return '🏷️';
      default: return '📝';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'number': return 'text-blue-600 bg-blue-50';
      case 'date': return 'text-green-600 bg-green-50';
      case 'boolean': return 'text-purple-600 bg-purple-50';
      case 'categorical': return 'text-orange-600 bg-orange-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const handleManualConversion = (updatedData: any[], updatedColumns: DataColumn[]) => {
    setCurrentData(updatedData);
    setDetectedColumns(updatedColumns);
    onColumnsDetected(updatedColumns);
    
    // Notifier App.tsx des données mises à jour
    if (onDataUpdated) {
      onDataUpdated(updatedData);
    }
    
    setShowTypeConverter(false);
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="mb-6 lg:mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2">
              Aperçu des données
            </h2>
            <p className="text-sm sm:text-base text-gray-600">
              {currentData.length} lignes • {detectedColumns.length} colonnes détectées
            </p>
            {autoDetecting && (
              <div className="flex items-center space-x-2 text-sm text-blue-600 mt-2">
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent"></div>
                <span>Détection automatique des colonnes booléennes...</span>
              </div>
            )}
            {booleanDetectionResult && (
              <div className="flex items-center space-x-2 text-sm text-green-600 mt-2">
                <CheckCircle size={16} />
                <span>{booleanDetectionResult.message}</span>
              </div>
            )}
          </div>
          <div className="flex flex-col items-end space-y-2">
            <div className="flex items-center space-x-2 text-xs sm:text-sm text-gray-500">
              <Eye size={16} />
              <span className="hidden sm:inline">Page {currentPage + 1} sur {totalPages}</span>
              <span className="sm:hidden">{currentPage + 1}/{totalPages}</span>
            </div>
            <button
              onClick={() => setShowTypeConverter(true)}
              className="inline-flex items-center px-3 py-1.5 border border-purple-300 rounded-lg text-xs sm:text-sm font-medium text-purple-700 bg-purple-50 hover:bg-purple-100 transition-colors"
            >
              <Wand2 size={14} className="mr-1.5" />
              Convertir les types
            </button>
          </div>
        </div>

        {/* Column Detection Summary */}
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <div className="text-xl sm:text-2xl font-bold text-blue-600">
              {detectedColumns.filter(col => col.type === 'number').length}
            </div>
            <div className="text-xs sm:text-sm text-blue-800">Numériques</div>
          </div>
          <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
            <div className="text-xl sm:text-2xl font-bold text-orange-600">
              {detectedColumns.filter(col => col.type === 'categorical').length}
            </div>
            <div className="text-xs sm:text-sm text-orange-800">Catégorielles</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
            <div className="text-xl sm:text-2xl font-bold text-green-600">
              {detectedColumns.filter(col => col.type === 'date').length}
            </div>
            <div className="text-xs sm:text-sm text-green-800">Dates</div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
            <div className="text-xl sm:text-2xl font-bold text-purple-600">
              {detectedColumns.filter(col => col.type === 'boolean').length}
            </div>
            <div className="text-xs sm:text-sm text-purple-800">Booléennes</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <div className="text-xl sm:text-2xl font-bold text-gray-600">
              {detectedColumns.filter(col => col.type === 'string').length}
            </div>
            <div className="text-xs sm:text-sm text-gray-800">Texte</div>
          </div>
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden mb-4 sm:mb-6">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {detectedColumns.map((column, index) => (
                  <th
                    key={index}
                    className="px-2 sm:px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    <div className="flex items-center space-x-1 sm:space-x-2">
                      <span className="text-sm sm:text-lg">{getTypeIcon(column.type)}</span>
                      <div>
                        <div className="font-semibold text-gray-900 text-xs sm:text-sm">
                          {column.name}
                        </div>
                        <div className={`inline-flex items-center px-1 sm:px-2 py-0.5 sm:py-1 rounded-full text-xs font-medium ${getTypeColor(column.type)}`}>
                          {column.type}
                        </div>
                      </div>
                      {column.isSelected && (
                        <CheckCircle size={14} className="sm:w-4 sm:h-4 text-green-500" />
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {paginatedData.map((row, rowIndex) => (
                <tr key={rowIndex} className="hover:bg-gray-50">
                  {detectedColumns.map((column, colIndex) => (
                    <td key={colIndex} className="px-2 sm:px-4 py-3 whitespace-nowrap text-xs sm:text-sm text-gray-900">
                      <div className="max-w-[100px] sm:max-w-xs truncate">
                        {row[column.name]?.toString() || '-'}
                      </div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mb-6 sm:mb-8">
          <button
            onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
            disabled={currentPage === 0}
            className="inline-flex items-center px-3 sm:px-4 py-2 border border-gray-300 rounded-lg text-xs sm:text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft size={14} className="sm:w-4 sm:h-4 mr-1" />
            <span className="hidden sm:inline">Précédent</span>
            <span className="sm:hidden">Préc</span>
          </button>

          <div className="flex items-center space-x-1 sm:space-x-2">
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              const pageNum = Math.max(0, Math.min(totalPages - 5, currentPage - 2)) + i;
              return (
                <button
                  key={pageNum}
                  onClick={() => setCurrentPage(pageNum)}
                  className={`px-2 sm:px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
                    currentPage === pageNum
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {pageNum + 1}
                </button>
              );
            })}
          </div>

          <button
            onClick={() => setCurrentPage(Math.min(totalPages - 1, currentPage + 1))}
            disabled={currentPage === totalPages - 1}
            className="inline-flex items-center px-3 sm:px-4 py-2 border border-gray-300 rounded-lg text-xs sm:text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="hidden sm:inline">Suivant</span>
            <span className="sm:hidden">Suiv</span>
            <ChevronRight size={14} className="sm:w-4 sm:h-4 ml-1" />
          </button>
        </div>
      )}

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
          className="inline-flex items-center justify-center px-4 sm:px-6 py-2 sm:py-3 border border-transparent text-sm sm:text-base font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 transition-colors"
        >
          Configurer les colonnes
          <Settings size={16} className="sm:w-5 sm:h-5 ml-2" />
        </button>
      </div>

      {/* Type Converter Modal */}
      {showTypeConverter && (
        <TypeConverter
          columns={detectedColumns}
          data={currentData}
          onConvert={handleManualConversion}
          onClose={() => setShowTypeConverter(false)}
        />
      )}
    </div>
  );
};

export default DataPreview;