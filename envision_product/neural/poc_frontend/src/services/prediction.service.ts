import api, { request } from './api';
import { PredictionResults } from '../types/data.types';
import { PredictionRequest } from '../types/api.types';

/**
 * Generate predictions using a trained model
 */
export const generatePredictions = async (modelId: string, months: number = 6): Promise<PredictionResults> => {
  const requestData: PredictionRequest = {
    modelId,
    months,
  };
  
  const response = await request<PredictionResults>({
    method: 'POST',
    url: '/predictions/generate',
    data: requestData,
  });
  
  return response.data;
};

/**
 * Get prediction results for a model
 */
export const getPredictions = async (modelId: string): Promise<PredictionResults> => {
  const response = await request<PredictionResults>({
    method: 'GET',
    url: `/predictions/result/${modelId}`,
  });
  
  return response.data;
};

/**
 * Export predictions to CSV
 */
export const exportPredictions = async (modelId: string, format: string = 'csv'): Promise<Blob> => {
  const response = await api({
    method: 'GET',
    url: `/files/export/${modelId}`,
    params: { format },
    responseType: 'blob',
  });
  
  return response.data;
};

/**
 * Download a blob as a file
 */
export const downloadBlob = (blob: Blob, filename: string): void => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}; 