/**
 * ImageUploadZone - CleanGrid Phase 1
 * Drag-and-drop image upload zone with validation
 */

'use client';

import { useState, useCallback } from 'react';

interface ImageUploadZoneProps {
  onImageSelect: (file: File) => void;
  selectedImage: File | null;
  disabled?: boolean;
}

const ImageUploadZone: React.FC<ImageUploadZoneProps> = ({ 
  onImageSelect, 
  selectedImage, 
  disabled = false 
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [dragCounter, setDragCounter] = useState(0);

  // Validate file
  const isValidFile = (file: File): boolean => {
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
    const maxSize = 10 * 1024 * 1024; // 10MB
    
    return allowedTypes.includes(file.type) && file.size <= maxSize;
  };

  const getFileError = (file: File): string | null => {
    if (!isValidFile(file)) {
      if (file.size > 10 * 1024 * 1024) {
        return 'File exceeds 10MB limit. Please compress or choose another image.';
      }
      if (!file.type.startsWith('image/')) {
        return 'Only JPEG, PNG, and WEBP images are accepted.';
      }
      return null;
    }
    return null;
  };

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    setDragCounter(0);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      const file = files[0] as File;
      const error = getFileError(file);
      
      if (error) {
        alert(error);
      } else {
        onImageSelect(file);
      }
    }
  }, [onImageSelect]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0] as File;
      const error = getFileError(file);
      
      if (error) {
        alert(error);
      } else {
        onImageSelect(file);
      }
    }
  }, [onImageSelect]);

  const handleClick = () => {
    if (!disabled) {
      document.getElementById('file-input')?.click();
    }
  }, [disabled]);

  return (
    <div className="image-upload-zone">
      <div
        className={`
          border-2 border-dashed rounded-lg p-8 text-center transition-colors
          ${isDragging ? 'border-blue-400 bg-blue-50' : 'border-gray-300 bg-gray-50'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-blue-400 cursor-pointer'}
        `}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          id="file-input"
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleFileSelect}
          disabled={disabled}
          className="hidden"
        />
        
        {selectedImage ? (
          <div className="space-y-4">
            <div className="mx-auto w-24 h-24 rounded-lg overflow-hidden">
              <img
                src={URL.createObjectURL(selectedImage)}
                alt="Selected image"
                className="w-full h-full object-cover"
              />
            </div>
            
            <div className="text-sm text-gray-600">
              <p className="font-medium">{selectedImage.name}</p>
              <p className="text-xs">
                {(selectedImage.size / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
            
            <button
              type="button"
              onClick={() => onImageSelect(null as any)}
              className="mt-2 px-3 py-1 bg-red-600 text-white text-sm rounded-md hover:bg-red-700"
            >
              Remove Image
            </button>
          </>
        ) : (
          <div className="space-y-4">
            <div className="text-gray-400">
              <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 0-4 4v8a4 4 0 0 4 4zm0 0l4.586 4.586A4 4 0 0 4 4.586 4.586zm0 0l4.586 4.586A4 4 0 0 4 4.586 4.586z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 11v1m6 0h6m-6 0v6h6" />
              </svg>
              <p className="mt-2 text-lg font-medium">Drag & Drop Image Here</p>
              <p className="text-sm">or</p>
            </div>
            
            <button
              type="button"
              className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
            >
              Choose File
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImageUploadZone;
