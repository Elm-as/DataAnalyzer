import React from 'react';
import { CheckCircle, Circle } from 'lucide-react';

interface Step {
  id: number;
  name: string;
  icon: React.ComponentType<any>;
  description: string;
}

interface SidebarProps {
  steps: Step[];
  currentStep: number;
  isOpen: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ steps, currentStep, isOpen, onToggle }) => {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onToggle}
        />
      )}
      
      {/* Sidebar */}
      <div className={`fixed left-0 top-0 h-full w-80 bg-white shadow-xl z-50 transform transition-transform duration-300 ease-in-out ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      } lg:translate-x-0 lg:block`}>
        <div className="p-4 sm:p-6 lg:p-8">
          {/* Mobile close button */}
          <div className="flex justify-end mb-4 lg:hidden">
            <button
              onClick={onToggle}
              className="p-2 rounded-lg hover:bg-gray-100"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
        <div className="flex items-center mb-8">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xl">DA</span>
          </div>
          <div className="ml-3">
            <h3 className="text-base lg:text-lg font-bold text-gray-900">Data Analyzer</h3>
            <p className="text-xs lg:text-sm text-gray-500">Analyse intelligente</p>
          </div>
        </div>

        <nav className="space-y-3 lg:space-y-4">
          {steps.map((step, index) => {
            const Icon = step.icon;
            const isCompleted = currentStep > index;
            const isCurrent = currentStep === index;

            return (
              <div
                key={step.id}
                className={`flex items-center p-3 lg:p-4 rounded-lg transition-all duration-300 ${
                  isCurrent
                    ? 'bg-blue-50 border border-blue-200'
                    : isCompleted
                    ? 'bg-green-50 border border-green-200'
                    : 'bg-gray-50 border border-gray-200'
                }`}
              >
                <div
                  className={`flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center transition-all duration-300 ${
                    isCurrent
                      ? 'bg-blue-600 text-white'
                      : isCompleted
                      ? 'bg-green-500 text-white'
                      : 'bg-white text-gray-400 border border-gray-300'
                  }`}
                >
                  {isCompleted ? <CheckCircle size={18} /> : <Icon size={18} />}
                </div>
                <div className="ml-4 flex-1">
                  <h4
                    className={`font-semibold transition-colors duration-300 ${
                      isCurrent
                        ? 'text-blue-900'
                        : isCompleted
                        ? 'text-green-900'
                        : 'text-gray-700'
                    }`}
                  >
                    {step.name}
                  </h4>
                  <p
                    className={`hidden sm:block text-sm transition-colors duration-300 ${
                      isCurrent
                        ? 'text-blue-600'
                        : isCompleted
                        ? 'text-green-600'
                        : 'text-gray-500'
                    }`}
                  >
                    {step.description}
                  </p>
                </div>
                {isCurrent && (
                  <div className="flex-shrink-0 w-2 h-2 bg-blue-600 rounded-full animate-pulse" />
                )}
              </div>
            );
          })}
        </nav>

        <div className="mt-8 lg:mt-12 p-4 lg:p-6 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
          <h4 className="font-semibold text-purple-900 mb-2">💡 Astuce</h4>
          <p className="text-sm text-purple-700">
            Assurez-vous que vos données sont bien formatées avant l'import. Les 
            colonnes avec des en-têtes clairs donneront de meilleurs résultats.
          </p>
        </div>
      </div>
    </div>
    </>
  );
};

export default Sidebar;