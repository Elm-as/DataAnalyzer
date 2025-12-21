import React from 'react';
import { AlertTriangle, CheckCircle, Info, Lightbulb, TrendingUp, Database } from 'lucide-react';

interface DataInsightsProps {
  results: any;
}

const DataInsights: React.FC<DataInsightsProps> = ({ results }) => {
  if (!results) return null;

  const renderDataQuality = () => {
    const quality = results.analyses?.classification?.data_quality;
    if (!quality) return null;

    const score = quality.quality_score || 0;
    const getScoreColor = (score: number) => {
      if (score >= 80) return 'text-green-600';
      if (score >= 60) return 'text-yellow-600';
      return 'text-red-600';
    };

    const getScoreBg = (score: number) => {
      if (score >= 80) return 'bg-green-100';
      if (score >= 60) return 'bg-yellow-100';
      return 'bg-red-100';
    };

    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Database className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-800">
            Data Quality Report
          </h3>
        </div>

        {/* Quality Score */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              Overall Quality Score
            </span>
            <span className={`text-3xl font-bold ${getScoreColor(score)}`}>
              {score.toFixed(0)}/100
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all ${
                score >= 80 
                  ? 'bg-gradient-to-r from-green-500 to-green-600'
                  : score >= 60
                  ? 'bg-gradient-to-r from-yellow-500 to-yellow-600'
                  : 'bg-gradient-to-r from-red-500 to-red-600'
              }`}
              style={{ width: `${score}%` }}
            />
          </div>
          <p className="text-sm text-gray-600 mt-2">
            {quality.overall_assessment}
          </p>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="text-xs text-gray-500 uppercase mb-1">
              Total Rows
            </div>
            <div className="text-lg font-bold text-gray-800">
              {quality.summary?.total_rows?.toLocaleString()}
            </div>
          </div>
          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="text-xs text-gray-500 uppercase mb-1">
              Total Columns
            </div>
            <div className="text-lg font-bold text-gray-800">
              {quality.summary?.total_columns}
            </div>
          </div>
          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="text-xs text-gray-500 uppercase mb-1">
              Memory (MB)
            </div>
            <div className="text-lg font-bold text-gray-800">
              {quality.summary?.memory_usage_mb?.toFixed(1)}
            </div>
          </div>
        </div>

        {/* Warnings */}
        {quality.warnings && quality.warnings.length > 0 && (
          <div className="mb-4">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle className="w-4 h-4 text-orange-600" />
              <span className="text-sm font-medium text-gray-700">
                Warnings
              </span>
            </div>
            <div className="space-y-2">
              {quality.warnings.map((warning: string, idx: number) => (
                <div
                  key={idx}
                  className="p-3 bg-orange-50 border border-orange-200 rounded-lg text-sm text-orange-800"
                >
                  {warning}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommendations */}
        {quality.recommendations && quality.recommendations.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Lightbulb className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-gray-700">
                Recommendations
              </span>
            </div>
            <div className="space-y-2">
              {quality.recommendations.map((rec: string, idx: number) => (
                <div
                  key={idx}
                  className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800"
                >
                  {rec}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Missing Values Details */}
        {quality.missing_values?.columns_with_missing > 0 && (
          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="text-sm font-medium text-yellow-900 mb-2">
              Missing Values: {quality.missing_values.columns_with_missing} columns affected
            </div>
            {quality.missing_values.critical_columns?.length > 0 && (
              <div className="text-xs text-yellow-700">
                Critical columns (>50% missing): {quality.missing_values.critical_columns.map((c: any) => c.column).join(', ')}
              </div>
            )}
          </div>
        )}

        {/* Duplicates */}
        {quality.duplicates?.count > 0 && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="text-sm text-red-800">
              <AlertTriangle className="w-4 h-4 inline mr-1" />
              {quality.duplicates.count} duplicate rows found ({quality.duplicates.percentage.toFixed(1)}%)
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderFeatureEngineering = () => {
    const fe = results.analyses?.classification?.feature_engineering;
    if (!fe) return null;

    const totalSuggestions = 
      (fe.categorical_grouping?.length || 0) +
      (fe.normalization?.length || 0) +
      (fe.derived_features?.length || 0) +
      (fe.transformations?.length || 0);

    if (totalSuggestions === 0) return null;

    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-5 h-5 text-purple-600" />
          <h3 className="text-lg font-semibold text-gray-800">
            Feature Engineering Suggestions
          </h3>
        </div>

        <div className="mb-4 p-3 bg-purple-50 border border-purple-200 rounded-lg">
          <p className="text-sm text-purple-800">
            <Info className="w-4 h-4 inline mr-1" />
            {totalSuggestions} opportunities identified to improve model performance
          </p>
        </div>

        {/* Derived Features */}
        {fe.derived_features && fe.derived_features.length > 0 && (
          <div className="mb-6">
            <div className="text-sm font-medium text-gray-700 mb-3">
              Suggested Derived Features
            </div>
            <div className="space-y-3">
              {fe.derived_features.map((feature: any, idx: number) => (
                <div
                  key={idx}
                  className="p-4 bg-gradient-to-r from-purple-50 to-purple-100 border border-purple-200 rounded-lg"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="font-medium text-purple-900">
                      {feature.name}
                    </div>
                    <span className="px-2 py-1 bg-purple-200 text-purple-800 text-xs font-medium rounded">
                      New Feature
                    </span>
                  </div>
                  <div className="text-sm text-purple-800 mb-2">
                    Formula: <code className="bg-purple-200 px-2 py-1 rounded">{feature.formula}</code>
                  </div>
                  <div className="text-xs text-purple-700">
                    {feature.reason}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Transformations */}
        {fe.transformations && fe.transformations.length > 0 && (
          <div className="mb-6">
            <div className="text-sm font-medium text-gray-700 mb-3">
              Recommended Transformations
            </div>
            <div className="space-y-2">
              {fe.transformations.map((trans: any, idx: number) => (
                <div
                  key={idx}
                  className="p-3 bg-blue-50 border border-blue-200 rounded-lg"
                >
                  <div className="text-sm text-blue-900 font-medium">
                    {trans.column}: Apply {trans.suggested_transform} transformation
                  </div>
                  <div className="text-xs text-blue-700 mt-1">
                    {trans.reason}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Normalization */}
        {fe.normalization && fe.normalization.length > 0 && (
          <div className="mb-6">
            <div className="text-sm font-medium text-gray-700 mb-3">
              Normalization Recommendations
            </div>
            <div className="space-y-2">
              {fe.normalization.map((norm: any, idx: number) => (
                <div
                  key={idx}
                  className="p-3 bg-green-50 border border-green-200 rounded-lg text-sm"
                >
                  <span className="font-medium text-green-900">{norm.column}:</span>
                  <span className="text-green-700 ml-2">{norm.method}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Categorical Grouping */}
        {fe.categorical_grouping && fe.categorical_grouping.length > 0 && (
          <div>
            <div className="text-sm font-medium text-gray-700 mb-3">
              Categorical Optimizations
            </div>
            <div className="space-y-2">
              {fe.categorical_grouping.map((cat: any, idx: number) => (
                <div
                  key={idx}
                  className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm"
                >
                  <span className="font-medium text-yellow-900">{cat.column}:</span>
                  <span className="text-yellow-700 ml-2">{cat.suggestion}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {renderDataQuality()}
      {renderFeatureEngineering()}
    </div>
  );
};

export default DataInsights;
