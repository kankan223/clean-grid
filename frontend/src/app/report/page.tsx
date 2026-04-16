/**
 * Report Page - CleanGrid Phase 1
 * Complete waste reporting interface with image upload and location selection
 */

'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';

import ImageUploadZone from '@/components/report/ImageUploadZone';
import LocationPicker from '@/components/report/LocationPicker';
import AIResultCard from '@/components/report/AIResultCard';
import { ReportCreate, Location } from '@/types/report';

const ReportPage: React.FC = () => {
  const router = useRouter();
  
  // Form state
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [location, setLocation] = useState<Location | null>(null);
  const [note, setNote] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  // Handle location change from LocationPicker
  const handleLocationChange = useCallback((newLocation: { lat: number; lng: number }) => {
    setLocation(newLocation);
  }, []);

  // Handle image upload
  const handleImageSelect = useCallback((file: File) => {
    setImageFile(file);
  }, []);

  // Validate form
  const isFormValid = (): boolean => {
    return !!(imageFile && location);
  };

  // Submit report
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isFormValid()) {
      return;
    }

    setIsSubmitting(true);
    setAnalysisResult(null);

    try {
      // Create form data
      const formData = new FormData();
      formData.append('image', imageFile);
      formData.append('lat', location.lat.toString());
      formData.append('lng', location.lng.toString());
      if (note.trim()) {
        formData.append('note', note.trim());
      }

      // Submit to API
      const response = await fetch('/api/reports', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit report');
      }

      const result = await response.json();
      
      // Show AI processing state
      setAnalysisResult({
        status: 'processing',
        message: result.message || 'Analyzing image...'
      });

      // Poll for completion (simplified - in production would use SSE)
      const pollInterval = setInterval(async () => {
        try {
          const checkResponse = await fetch(`/api/reports/${result.report_id}`);
          const checkData = await checkResponse.json();
          
          if (checkData.status !== 'processing') {
            clearInterval(pollInterval);
            setAnalysisResult(checkData);
          }
        } catch (error) {
          console.error('Polling error:', error);
        }
      }, 2000); // Poll every 2 seconds

    } catch (error) {
      console.error('Submission error:', error);
      alert(`Failed to submit report: ${error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleViewOnMap = () => {
    if (analysisResult?.incident_id) {
      router.push(`/?incident=${analysisResult.incident_id}`);
    }
  };

  const handleReportAnother = () => {
    // Reset form
    setImageFile(null);
    setLocation(null);
    setNote('');
    setAnalysisResult(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Report Waste
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Help keep our community clean by reporting waste incidents
          </p>
        </div>

        <div className="bg-white shadow-lg rounded-lg">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Step 1: Image Upload */}
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                1. Upload Image
              </h2>
              <ImageUploadZone 
                onImageSelect={handleImageSelect}
                selectedImage={imageFile}
                disabled={isSubmitting}
              />
            </div>

            {/* Step 2: Location Selection */}
            <div className={imageFile ? 'block' : 'hidden'}>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                2. Select Location
              </h2>
              <LocationPicker
                onLocationChange={handleLocationChange}
                initialLocation={location}
              />
            </div>

            {/* Step 3: Note */}
            <div className={imageFile && location ? 'block' : 'hidden'}>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                3. Add Note (Optional)
              </h2>
              <div>
                <label htmlFor="note" className="block text-sm font-medium text-gray-700 mb-2">
                  Additional details about this waste incident (max 200 characters)
                </label>
                <textarea
                  id="note"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  maxLength={200}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Large pile of plastic bottles near bus stop..."
                  disabled={isSubmitting}
                />
                <div className="text-right text-sm text-gray-500">
                  {note.length}/200
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className={imageFile && location ? 'block' : 'hidden'}>
              <button
                type="submit"
                disabled={!isFormValid() || isSubmitting}
                className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {isSubmitting ? (
                  <>
                    <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white border-t-transparent"></div>
                    <span className="ml-2">Submitting Report...</span>
                  </>
                ) : (
                  <>
                    📤 Submit Report
                  </>
                )}
              </button>
            </div>
          </form>

          {/* AI Analysis Result */}
          {analysisResult && (
            <AIResultCard
              result={analysisResult}
              onViewOnMap={handleViewOnMap}
              onReportAnother={handleReportAnother}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default ReportPage;
