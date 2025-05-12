import api, { request } from './api';
import { UploadResponse, DataPreview } from '../types/data.types';

/**
 * Upload a data file to the server
 */
export const uploadFile = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await request<UploadResponse>({
    method: 'POST',
    url: '/data/upload',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      // Can report progress here if needed
      const percentCompleted = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
      console.log(`Upload progress: ${percentCompleted}%`);
    },
  });
  
  return response.data;
};

/**
 * Get a preview of the uploaded file
 */
export const getDataPreview = async (fileId: string): Promise<DataPreview> => {
  const response = await request<DataPreview>({
    method: 'GET',
    url: `/data/preview/${fileId}`,
  });
  
  return response.data;
};

/**
 * Validate if the uploaded file meets the requirements for a specific model
 */
export const validateFileForModel = async (fileId: string, modelId: string): Promise<{isValid: boolean, errors?: string[]}> => {
  const response = await request<{isValid: boolean, errors?: string[]}>({
    method: 'POST',
    url: '/data/validate',
    data: {
      fileId,
      modelId,
    },
  });
  
  return response.data;
}; 