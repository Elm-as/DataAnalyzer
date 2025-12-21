import React from 'react';
import { TrendingUp, TrendingDown, AlertCircle, CheckCircle, Info, Award } from 'lucide-react';

interface ExplainabilityDisplayProps {
  results: any;
}

const ExplainabilityDisplay: React.FC<ExplainabilityDisplayProps> = ({ results }) => {
  if (!results) return null;

  const renderFeatureImportance = () => {
    const classificationData = results.analyses?.classification;
    if (!classificationData) return null;

    const bestModel = classificationData.models?.[classificationData.summary?.best_model_key];
    const featureImportance = bestModel?.feature_importance_global;

    if (!featureImportance?.available) return null;

    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Award className="w-5 h-5 text-purple-600" />
          <h3 className="text-lg font-semibold text-gray-800">
            Feature Importance (Global)
          </h3>
        </div>
        
        <div className="space-y-3">
          {featureImportance.top_features?.slice(0, 10).map((feature: any, idx: number) => (
            <div key={idx} className="flex items-center gap-3">
              <div className="w-8 text-sm font-medium text-gray-500">
                #{idx + 1}
              </div>
              <div className="flex-1">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm font-medium text-gray-700">
                    {feature.feature}
                  </span>
                  <span className="text-sm text-gray-600">
                    {feature.percentage.toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-purple-600 h-2 rounded-full transition-all"
                    style={{ width: `${Math.min(feature.percentage, 100)}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 p-3 bg-purple-50 border border-purple-200 rounded-lg">
          <p className="text-sm text-purple-800">
            <Info className="w-4 h-4 inline mr-1" />
            Top 10 features explain <strong>{featureImportance.top_10_cumulative?.toFixed(1)}%</strong> of the model's decisions
          </p>
        </div>
      </div>
    );
  };

  const renderCalibration = () => {
    const classificationData = results.analyses?.classification;
    if (!classificationData) return null;

    const bestModel = classificationData.models?.[classificationData.summary?.best_model_key];
    const calibration = bestModel?.calibration;

    if (!calibration) return null;

    const isWellCalibrated = calibration.is_well_calibrated;
    const brierScore = calibration.brier_score;
    const ece = calibration.expected_calibration_error;

    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          {isWellCalibrated ? (
            <CheckCircle className="w-5 h-5 text-green-600" />
          ) : (
            <AlertCircle className="w-5 h-5 text-orange-600" />
          )}
          <h3 className="text-lg font-semibold text-gray-800">
            Probability Calibration
          </h3>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">
              Brier Score
            </div>
            <div className="text-2xl font-bold text-gray-800">
              {brierScore?.toFixed(3)}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Lower is better
            </div>
          </div>

          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">
              Calibration Error (ECE)
            </div>
            <div className="text-2xl font-bold text-gray-800">
              {ece?.toFixed(3)}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Lower is better
            </div>
          </div>
        </div>

        <div className={`p-4 rounded-lg border ${
          isWellCalibrated 
            ? 'bg-green-50 border-green-200' 
            : 'bg-orange-50 border-orange-200'
        }`}>
          <div className="space-y-2">
            {calibration.interpretation?.map((message: string, idx: number) => (
              <p key={idx} className={`text-sm ${
                isWellCalibrated ? 'text-green-800' : 'text-orange-800'
              }`}>
                {message}
              </p>
            ))}
          </div>
        </div>

        {bestModel?.calibration_suggestion?.needed && (
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              <Info className="w-4 h-4 inline mr-1" />
              <strong>Suggestion:</strong> {bestModel.calibration_suggestion.method}
            </p>
          </div>
        )}
      </div>
    );
  };

  const renderModelAudit = () => {
    const audit = results.analyses?.classification?.model_audit;
    if (!audit) return null;

    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <AlertCircle className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-800">
            Model Audit Report
          </h3>
        </div>

        <div className="space-y-4">
          {/* Selected Model */}
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="text-sm font-medium text-blue-900 mb-2">
              Selected Model: <strong>{audit.selected_model}</strong>
            </div>
            <div className="flex items-center gap-2">
              <div className="text-xs text-blue-700">
                Overfitting Risk: 
              </div>
              <span className={`px-2 py-1 text-xs font-medium rounded ${
                audit.overfitting_risk === 'low' 
                  ? 'bg-green-100 text-green-800'
                  : audit.overfitting_risk === 'moderate'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {audit.overfitting_risk}
              </span>
            </div>
          </div>

          {/* Justifications */}
          {audit.justification && audit.justification.length > 0 && (
            <div>
              <div className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                Justifications
              </div>
              <ul className="space-y-2">
                {audit.justification.map((reason: string, idx: number) => (
                  <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                    <span className="text-green-600 mt-1">•</span>
                    <span>{reason}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Warnings */}
          {audit.warnings && audit.warnings.length > 0 && (
            <div>
              <div className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-orange-600" />
                Warnings
              </div>
              <ul className="space-y-2">
                {audit.warnings.map((warning: string, idx: number) => (
                  <li key={idx} className="text-sm text-orange-600 flex items-start gap-2">
                    <span className="mt-1">⚠</span>
                    <span>{warning}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Bias Detection */}
          {audit.bias_detected && audit.bias_detected.length > 0 && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="text-sm font-medium text-red-900 mb-2">
                Bias Detected
              </div>
              <ul className="space-y-1">
                {audit.bias_detected.map((bias: string, idx: number) => (
                  <li key={idx} className="text-sm text-red-700">
                    • {bias}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderImbalanceAnalysis = () => {
    const imbalance = results.analyses?.classification?.imbalance_analysis;
    if (!imbalance || !imbalance.is_imbalanced) return null;

    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <AlertCircle className="w-5 h-5 text-orange-600" />
          <h3 className="text-lg font-semibold text-gray-800">
            Class Imbalance Detected
          </h3>
        </div>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-orange-50 rounded-lg">
              <div className="text-xs text-gray-500 uppercase mb-1">
                Imbalance Ratio
              </div>
              <div className="text-xl font-bold text-orange-600">
                {imbalance.imbalance_ratio.toFixed(1)}:1
              </div>
            </div>
            <div className="p-3 bg-orange-50 rounded-lg">
              <div className="text-xs text-gray-500 uppercase mb-1">
                Severity
              </div>
              <div className="text-xl font-bold text-orange-600 capitalize">
                {imbalance.severity}
              </div>
            </div>
          </div>

          <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
            <p className="text-sm text-orange-800 mb-3">
              <strong>Recommendation:</strong> {imbalance.recommendation}
            </p>
            
            {imbalance.strategies && imbalance.strategies.length > 0 && (
              <div className="space-y-2">
                <div className="text-xs font-medium text-orange-900 uppercase">
                  Suggested Strategies:
                </div>
                {imbalance.strategies.map((strategy: any, idx: number) => (
                  <div key={idx} className="text-sm text-orange-700">
                    <strong>{strategy.name}:</strong> {strategy.description}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="text-xs font-medium text-blue-900 uppercase mb-2">
              Recommended Metrics:
            </div>
            <div className="flex flex-wrap gap-2">
              {imbalance.suggested_metrics?.map((metric: string, idx: number) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full"
                >
                  {metric}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {renderFeatureImportance()}
      {renderCalibration()}
      {renderModelAudit()}
      {renderImbalanceAnalysis()}
    </div>
  );
};

export default ExplainabilityDisplay;
