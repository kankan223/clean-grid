/**
 * AIResultCard - CleanGrid Phase 1
 * Displays AI analysis results with severity and confidence
 */

'use client';

import { AIAnalysisResult } from '@/types/report';

interface AIResultCardProps {
  result: AIAnalysisResult;
  onViewOnMap: () => void;
  onReportAnother: () => void;
}

const AIResultCard: React.FC<AIResultCardProps> = ({ 
  result, 
  onViewOnMap, 
  onReportAnother 
}) => {
  const getSeverityColor = (severity?: string): string => {
    switch (severity) {
      case 'High':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'Medium':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'Low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getSeverityIcon = (severity?: string): string => {
    switch (severity) {
      case 'High':
        return '🔥';
      case 'Medium':
        return '⚠️';
      case 'Low':
        return '✅';
      default:
        return '❓';
    }
  };

  if (result.status === 'processing') {
    return (
      <div className="ai-result-card">
        <div className="p-6 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 border-t-transparent"></div>
          <p className="mt-4 text-lg font-medium text-blue-600">
            🔍 Analyzing image...
          </p>
        </div>
      </div>
    );
  }

  if (result.error) {
    return (
      <div className="ai-result-card">
        <div className="p-6 text-center">
          <div className="text-red-600">
            ❌ {result.error}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="ai-result-card">
      <div className="p-6">
        {/* Status Badge */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Analysis Complete
          </h3>
          
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getSeverityColor(result.severity)}`}>
            <span className="mr-2">{getSeverityIcon(result.severity)}</span>
            <span className="uppercase">{result.severity || 'None'}</span>
          </div>
        </div>

        {/* Confidence Score */}
        {result.confidence && (
          <div className="mb-4">
            <div className="text-sm text-gray-600">
              Confidence
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {Math.round((result.confidence || 0) * 100)}%
            </div>
          </div>
        )}

        {/* Points Awarded */}
        {result.waste_detected && (
          <div className="mb-4">
            <div className="flex items-center text-green-600">
              <div className="text-2xl mr-2">+10</div>
              <div className="text-lg font-medium">points added!</div>
            </div>
            <div className="text-sm text-gray-600">
              (if logged in)
            </div>
          </div>
        )}

        {/* No Waste Detected */}
        {!result.waste_detected && (
          <div className="mb-4">
            <div className="text-gray-600">
              <div className="text-2xl mb-2">🤷</div>
              <div className="text-lg font-medium">No waste detected</div>
            </div>
            <div className="text-sm text-gray-600">
              Your report was saved for admin review.
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex space-x-4">
          <button
            onClick={onViewOnMap}
            className="flex-1 px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            📍 View on Map
          </button>
          
          <button
            onClick={onReportAnother}
            className="flex-1 px-4 py-2 bg-gray-600 text-white font-medium rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            📤 Report Another
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIResultCard;
