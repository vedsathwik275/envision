import api, { request } from './api';
import { Model } from '../types/model.types';
import { TrainingJob } from '../types/model.types';
import { TrainingRequest } from '../types/api.types';

/**
 * Get a list of available models
 */
export const getAvailableModels = async (): Promise<Model[]> => {
  const response = await request<Model[]>({
    method: 'GET',
    url: '/models/list',
  });
  
  return response.data;
};

/**
 * Get a specific model by ID
 */
export const getModelById = async (modelId: string): Promise<Model> => {
  const response = await request<Model>({
    method: 'GET',
    url: `/models/${modelId}`,
  });
  
  return response.data;
};

/**
 * Start training a model with the given file
 */
export const startTraining = async (fileId: string, modelType: string): Promise<TrainingJob> => {
  const requestData: TrainingRequest = {
    fileId,
    modelType,
  };
  
  const response = await request<TrainingJob>({
    method: 'POST',
    url: '/models/train',
    data: requestData,
  });
  
  return response.data;
}; 