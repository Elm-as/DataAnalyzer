import React, { useState } from 'react';
import { Upload, BarChart3, Settings, TrendingUp, Download, HelpCircle, CheckSquare, Zap } from 'lucide-react';
import FileUpload from './components/FileUpload';
import DataPreview from './components/DataPreview';
import DataQualityReport from './components/DataQualityReport';
import ColumnSelector from './components/ColumnSelector';
import DataConfiguration from './components/DataConfiguration';
import AnalysisOptions from './components/AnalysisOptions';
import AnalysisResults from './components/AnalysisResults';
import Sidebar from './components/Sidebar';
import HelpMenu from './components/HelpMenu';
import { DataValidator, DataValidationReport } from './utils/dataValidator';

export interface DataColumn {
  name: string;
  type: 'number' | 'string' | 'date' | 'boolean' | 'categorical';
  isHeader: boolean;
  isSelected: boolean;
  sample?: any[];
  uniqueValues?: any[];
}

export interface AnalysisConfig {
  // Analyses de base
  descriptiveStats: boolean;
  correlations: boolean;
  distributions: boolean;
  outliers: boolean;
  clustering: boolean;
  trends: boolean;
  categorical: boolean;
  associations: boolean;
  
  // Analyses avancées
  regression: boolean;
  classification: boolean;
  discriminant: boolean;
  neuralNetworks: boolean;
  timeSeries: boolean;
  advancedClustering: boolean;
  dataCleaning: boolean;
  advancedStats: boolean;
  symptomMatching: boolean;
}

function App() {
  const [currentStep, setCurrentStep] = useState(0);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [helpMenuOpen, setHelpMenuOpen] = useState(false);
  const [rawData, setRawData] = useState<any[]>([]);
  const [columns, setColumns] = useState<DataColumn[]>([]);
  const [analysisConfig, setAnalysisConfig] = useState<AnalysisConfig>({
    descriptiveStats: true,
    correlations: true,
    distributions: true,
    outliers: true,
    clustering: false,
    trends: false,
    categorical: true,
    associations: false,
    
    // Analyses avancées (désactivées par défaut)
    regression: false,
    classification: false,
    discriminant: false,
    neuralNetworks: false,
    timeSeries: false,
    advancedClustering: false,
    dataCleaning: false,
    advancedStats: false,
    symptomMatching: false,
  });
  const [results, setResults] = useState<any>(null);

  const [validationReport, setValidationReport] = useState<DataValidationReport | null>(null);

  const steps = [
    { id: 0, name: 'Import', icon: Upload, description: 'Importer vos données' },
    { id: 1, name: 'Aperçu', icon: BarChart3, description: 'Prévisualiser les données' },
    { id: 2, name: 'Qualité', icon: CheckSquare, description: 'Vérifier la qualité' },
    { id: 3, name: 'Colonnes', icon: Zap, description: 'Sélectionner les meilleures' },
    { id: 4, name: 'Configuration', icon: Settings, description: 'Configurer les colonnes' },
    { id: 5, name: 'Analyses', icon: TrendingUp, description: 'Choisir les analyses' },
    { id: 6, name: 'Résultats', icon: Download, description: 'Voir les résultats' },
  ];

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <FileUpload
            onDataLoaded={(data) => {
              setRawData(data);
              nextStep();
            }}
          />
        );
      case 1:
        return (
          <DataPreview
            data={rawData}
            onColumnsDetected={(cols) => {
              setColumns(cols);
              // Analyser la qualité des données
              const report = DataValidator.validate(rawData, cols.map(c => c.name));
              setValidationReport(report);
            }}
            onDataUpdated={(updatedData) => {
              // Mettre à jour les données si conversion automatique
              setRawData(updatedData);
            }}
            onNext={nextStep}
            onPrev={prevStep}
          />
        );
      case 2:
        return validationReport ? (
          <DataQualityReport
            report={validationReport}
            columns={columns}
            onColumnsUpdated={(updatedCols) => {
              setColumns(updatedCols);
              // Réanalyser après suppression de colonnes
              const newData = rawData.map((row: any) => {
                const newRow: any = {};
                updatedCols.forEach(col => {
                  newRow[col.name] = row[col.name];
                });
                return newRow;
              });
              const newReport = DataValidator.validate(newData, updatedCols.map(c => c.name));
              setValidationReport(newReport);
            }}
            onNext={nextStep}
            onPrev={prevStep}
          />
        ) : null;
      case 3:
        return (
          <ColumnSelector
            columns={columns}
            data={rawData}
            onColumnsSelected={(selectedCols) => {
              setColumns(selectedCols);
              nextStep();
            }}
            onNext={nextStep}
            onPrev={prevStep}
            maxColumns={50}
          />
        );
      case 4:
        return (
          <DataConfiguration
            columns={columns}
            onColumnsUpdated={setColumns}
            onNext={nextStep}
            onPrev={prevStep}
          />
        );
      case 5:
        return (
          <AnalysisOptions
            config={analysisConfig}
            onConfigUpdated={setAnalysisConfig}
            columns={columns}
            data={rawData}
            onAnalysisComplete={(results) => {
              setResults(results);
              nextStep();
            }}
            onPrev={prevStep}
          />
        );
      case 6:
        return (
          <AnalysisResults
            results={results}
            columns={columns}
            data={rawData}
            onPrev={prevStep}
            onReset={() => {
              setCurrentStep(0);
              setRawData([]);
              setColumns([]);
              setResults(null);
              setValidationReport(null);
            }}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <Sidebar 
        steps={steps} 
        currentStep={currentStep} 
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />
      
      <HelpMenu 
        isOpen={helpMenuOpen}
        onClose={() => setHelpMenuOpen(false)}
      />
      
      <div className="lg:ml-80">
        <div className="p-4 sm:p-6 lg:p-8">
          {/* Header */}
          <div className="mb-6 lg:mb-8">
            <div className="flex items-center justify-between mb-4">
              <div className="lg:hidden">
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="p-2 rounded-lg bg-white shadow-md border border-gray-200"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>
              </div>
              <button
                onClick={() => setHelpMenuOpen(true)}
                className="ml-auto flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-md"
                title="Ouvrir le guide d'utilisation"
              >
                <HelpCircle className="w-5 h-5" />
                <span className="hidden sm:inline font-medium">Guide</span>
              </button>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
              Analyseur de Données
            </h1>
            <p className="text-gray-600">
              Importez, configurez et analysez vos données en quelques clics
            </p>
          </div>

          {/* Progress Bar */}
          <div className="mb-6 lg:mb-8">
            <div className="flex items-center justify-between mb-4">
              {steps.map((step, index) => (
                <div
                  key={step.id}
                  className={`flex items-center ${
                    index < steps.length - 1 ? 'flex-1' : ''
                  }`}
                >
                  <div
                    className={`w-8 h-8 sm:w-10 sm:h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300 ${
                      currentStep === index
                        ? 'bg-blue-600 border-blue-600 text-white'
                        : currentStep > index
                        ? 'bg-green-500 border-green-500 text-white'
                        : 'bg-white border-gray-300 text-gray-400'
                    }`}
                  >
                    <step.icon size={16} className="sm:w-5 sm:h-5" />
                  </div>
                  {index < steps.length - 1 && (
                    <div
                      className={`flex-1 h-0.5 mx-4 transition-all duration-300 ${
                        currentStep > index ? 'bg-green-500' : 'bg-gray-300'
                      }`}
                    />
                  )}
                </div>
              ))}
            </div>
            <div className="text-center">
              <h2 className="text-xl font-semibold text-gray-800">
                {steps[currentStep].name}
              </h2>
              <p className="text-gray-600 text-sm hidden sm:block">
                {steps[currentStep].description}
              </p>
            </div>
          </div>

          {/* Step Content */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            {renderStepContent()}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;