import React, { useState, useRef } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle, Info } from 'lucide-react';
import { CSVParser } from '../utils/csvParser';

interface FileUploadProps {
  onDataLoaded: (data: any[]) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onDataLoaded }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [warning, setWarning] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFile(files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file: File) => {
    setUploading(true);
    setError(null);

    try {
      // Valider le fichier
      const validation = CSVParser.validate(file);
      if (!validation.valid) {
        setError(validation.error || 'Erreur inconnue');
        setUploading(false);
        return;
      }

      const text = await file.text();
      let data: any[] = [];

      if (file.name.endsWith('.csv')) {
        // Utiliser le nouveau parser robuste
        const result = CSVParser.parse(text);
        
        if (result.errors.length > 0) {
          setError(result.errors[0]);
          setUploading(false);
          return;
        }

        // Avertissement si trop de colonnes
        if (result.stats.columnCount > 100) {
          setWarning(
            `⚠️ ${result.stats.columnCount} colonnes détectées. ` +
            `Vous pourrez en sélectionner les meilleures à l'étape suivante.`
          );
        }

        data = result.data;
      } else if (file.name.endsWith('.json')) {
        data = JSON.parse(text);
        if (!Array.isArray(data)) {
          throw new Error('Le fichier JSON doit contenir un tableau d\'objets');
        }
      } else {
        throw new Error('Format de fichier non supporté. Utilisez CSV ou JSON.');
      }

      if (data.length === 0) {
        throw new Error('Le fichier est vide ou ne contient pas de données valides');
      }

      onDataLoaded(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors du chargement du fichier');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-6 lg:mb-8">
          <FileText size={40} className="sm:w-12 sm:h-12 mx-auto text-blue-600 mb-4" />
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2">
            Importez vos données
          </h2>
          <p className="text-sm sm:text-base text-gray-600">
            Glissez-déposez votre fichier CSV ou JSON, ou cliquez pour sélectionner
          </p>
        </div>

        <div
          className={`relative border-2 border-dashed rounded-xl p-6 sm:p-8 lg:p-12 transition-all duration-300 cursor-pointer hover:border-blue-400 hover:bg-blue-50 ${
            dragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 bg-gray-50'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.json"
            onChange={handleFileInput}
            className="hidden"
          />

          <div className="text-center">
            {uploading ? (
              <div className="animate-spin mx-auto mb-4">
                <Upload size={32} className="sm:w-12 sm:h-12 text-blue-600" />
              </div>
            ) : (
              <Upload size={32} className="sm:w-12 sm:h-12 mx-auto text-gray-400 mb-4" />
            )}

            <div className="mb-4">
              <p className="text-base sm:text-lg font-semibold text-gray-700 mb-2">
                {uploading
                  ? 'Chargement en cours...'
                  : 'Glissez votre fichier ici ou cliquez pour sélectionner'}
              </p>
              <p className="text-sm text-gray-500">
                Formats supportés: CSV, JSON (max 10MB)
              </p>
            </div>

            {!uploading && (
              <button className="inline-flex items-center px-4 sm:px-6 py-2 sm:py-3 border border-transparent text-sm sm:text-base font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 transition-colors duration-200">
                <Upload size={16} className="sm:w-5 sm:h-5 mr-2" />
                Sélectionner un fichier
              </button>
            )}
          </div>
        </div>

        {error && (
          <div className="mt-4 sm:mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center">
              <AlertCircle size={18} className="sm:w-5 sm:h-5 text-red-600 mr-3 flex-shrink-0" />
              <div>
                <h3 className="text-sm font-semibold text-red-800">
                  Erreur de chargement
                </h3>
                <p className="text-sm text-red-600">{error}</p>
              </div>
            </div>
          </div>
        )}

        {warning && (
          <div className="mt-4 sm:mt-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <div className="flex items-center">
              <AlertCircle size={18} className="sm:w-5 sm:h-5 text-amber-600 mr-3 flex-shrink-0" />
              <div>
                <h3 className="text-sm font-semibold text-amber-800">
                  Information
                </h3>
                <p className="text-sm text-amber-700">{warning}</p>
              </div>
            </div>
          </div>
        )}

        <div className="mt-6 sm:mt-8 grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
          <div className="p-6 bg-white border border-gray-200 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
              <FileText size={18} className="sm:w-5 sm:h-5 mr-2 text-blue-600" />
              Format CSV
            </h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Première ligne = en-têtes des colonnes</li>
              <li>• Séparateur virgule (,)</li>
              <li>• Encodage UTF-8 recommandé</li>
            </ul>
          </div>

          <div className="p-6 bg-white border border-gray-200 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
              <FileText size={18} className="sm:w-5 sm:h-5 mr-2 text-purple-600" />
              Format JSON
            </h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Tableau d'objets JSON</li>
              <li>• Propriétés = noms des colonnes</li>
              <li>• Structure cohérente</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;