/**
 * AIResultCard - CleanGrid Phase 1
 * Displays AI analysis results with severity and confidence
 */

'use client';

import { AIAnalysisResult, Detection } from '@/types/report';

interface AIResultCardProps {
  result: AIAnalysisResult;
  uploadedImage?: string;
  onViewOnMap: () => void;
  onReportAnother: () => void;
}

const AIResultCard: React.FC<AIResultCardProps> = ({ 
  result, 
  uploadedImage,
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

        {/* Annotated Image with Bounding Boxes */}
        {uploadedImage && (
          <div className="mb-4 relative">
            <div className="text-sm text-gray-600 mb-2">
              Detection Results
            </div>
            <div className="relative inline-block">
              <img 
                src={uploadedImage} 
                alt="Uploaded waste image" 
                className="max-w-full h-auto rounded-lg border border-gray-200"
                style={{ maxHeight: '300px' }}
              />
              {/* Bounding Boxes Overlay */}
              {result.detections && result.detections.length > 0 && (
                <svg 
                  className="absolute top-0 left-0 w-full h-full pointer-events-none"
                  viewBox={`0 0 ${result.image_width || 400} ${result.image_height || 300}`}
                  preserveAspectRatio="none"
                >
                  {result.detections.map((detection: Detection, index: number) => (
                    <rect
                      key={index}
                      x={detection.bbox?.[0] || 0}
                      y={detection.bbox?.[1] || 0}
                      width={detection.bbox?.[2] || 0}
                      height={detection.bbox?.[3] || 0}
                      fill="none"
                      stroke={getSeverityColor(result.severity).includes('red') ? '#ef4444' : 
                              getSeverityColor(result.severity).includes('orange') ? '#f97316' : '#22c55e'}
                      strokeWidth="2"
                      rx="2"
                    />
                  ))}
                </svg>
              )}
            </div>
          </div>
        )}

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
              <div className="text-2xl mr-2">
                +{result.severity === 'High' ? '15' : result.severity === 'Medium' ? '10' : '5'}
              </div>
              <div className="text-lg font-medium">points earned!</div>
            </div>
            <div className="text-sm text-gray-600">
              {result.severity === 'High' ? 'High severity bonus' : 
               result.severity === 'Medium' ? 'Medium severity' : 'Low severity'} 
              {' '} (if logged in)
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
