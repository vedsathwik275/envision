import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../store';
import { uploadDataFile, setFile, setUploadProgress, clearUploadState, fetchDataPreview, validateFile } from '../store/uploadSlice';
import { isValidCsvFile } from '../utils/validators';
import { useDropzone } from 'react-dropzone';

// Define upload state interface for type safety
interface UploadState {
  file: File | null;
  fileId: string | null;
  preview: any;
  isUploading: boolean;
  uploadProgress: number;
  error: string | null;
  validationErrors: string[];
  isValidForModel: boolean;
}

/**
 * Custom hook for file upload functionality
 */
export const useFileUpload = () => {
  const dispatch = useDispatch<AppDispatch>();
  const {
    file,
    fileId,
    preview,
    isUploading,
    uploadProgress,
    error,
    validationErrors,
    isValidForModel,
  } = useSelector((state: RootState) => state.upload as UploadState);

  /**
   * Handle file selection
   */
  const handleFileSelected = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      const selectedFile = acceptedFiles[0];
      
      // Validate file type and size
      if (!isValidCsvFile(selectedFile)) {
        console.error('Invalid file format or size');
        return;
      }
      
      // Set file in state
      dispatch(setFile(selectedFile));
    }
  }, [dispatch]);

  /**
   * Handle file upload
   */
  const uploadFile = useCallback(async () => {
    if (!file) return;
    
    try {
      // Upload file
      await dispatch(uploadDataFile(file)).unwrap();
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  }, [dispatch, file]);

  /**
   * Get file preview
   */
  const getPreview = useCallback(async (id: string) => {
    try {
      await dispatch(fetchDataPreview(id)).unwrap();
    } catch (error) {
      console.error('Error fetching preview:', error);
    }
  }, [dispatch]);

  /**
   * Validate file for a model
   */
  const validateFileForModel = useCallback(async (fileId: string, modelId: string) => {
    try {
      await dispatch(validateFile({ fileId, modelId })).unwrap();
    } catch (error) {
      console.error('Error validating file:', error);
    }
  }, [dispatch]);

  /**
   * Clear upload state
   */
  const clearUpload = useCallback(() => {
    dispatch(clearUploadState());
  }, [dispatch]);

  /**
   * Configure dropzone
   */
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: handleFileSelected,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.csv'],
      'application/csv': ['.csv'],
    },
    maxFiles: 1,
    multiple: false,
  });

  return {
    // State
    file,
    fileId,
    preview,
    isUploading,
    uploadProgress,
    error,
    validationErrors,
    isValidForModel,
    isDragActive,
    
    // Actions
    uploadFile,
    getPreview,
    validateFileForModel,
    clearUpload,
    
    // Dropzone
    getRootProps,
    getInputProps,
  };
}; 