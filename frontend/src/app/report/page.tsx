/**
 * Report Page - CleanGrid Phase 1
 * Complete waste reporting interface with image upload and location selection
 */

'use client';

export const dynamic = 'force-dynamic';

import { useState, useCallback } from 'react';
import dynamicImport from 'next/dynamic';
import { useRouter } from 'next/navigation';

import ImageUploadZone from '@/components/report/ImageUploadZone';
const LocationPicker = dynamicImport(() => import('@/components/report/LocationPicker'), { ssr: false });
import AIResultCard from '@/components/report/AIResultCard';
import { Skeleton } from '@/components/ui/skeleton';
import { useToast } from '@/components/ui/toast';
import { ReportCreate, Location } from '@/types/report';

const ReportPage: React.FC = () => {
  const router = useRouter();
  const { toast } = useToast();
  
  // Form state
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [location, setLocation] = useState<Location | null>(null);
  const [note, setNote] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  // Handle location change from LocationPicker
  const handleLocationChange = useCallback((lat: number, lng: number) => {
    setLocation({ lat, lng });
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
      if (imageFile) {
        formData.append('image', imageFile);
      }
      if (location) {
        formData.append('lat', location.lat.toString());
        formData.append('lng', location.lng.toString());
      }
      if (note.trim()) {
        formData.append('note', note.trim());
      }

      // Submit to API
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/reports`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
        // DO NOT set Content-Type header - let browser set it with correct boundary
      });

      if (!response.ok) {
        let errorMessage = 'Failed to submit report';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch (parseError) {
          // If response is not JSON, use status text
          errorMessage = response.statusText || errorMessage;
        }
        throw new Error(errorMessage);
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
          const checkResponse = await fetch(`${apiUrl}/api/reports/${result.report_id}`, {
            credentials: 'include',
          });
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
      toast({
        title: 'Report submission failed',
        description: (error as Error).message,
        variant: 'error',
      });
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
                initialLocation={location || undefined}
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

          {isSubmitting && !analysisResult ? (
            <div className="space-y-3 border-t px-6 pb-6 pt-4">
              <Skeleton className="h-5 w-48" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-11/12" />
            </div>
          ) : null}

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
