import api, { request } from './api';
import { TrainingStatus, TrainingResult } from '../types/model.types';

/**
 * Get the status of a training job
 */
export const getTrainingStatus = async (jobId: string): Promise<TrainingStatus> => {
  const response = await request<TrainingStatus>({
    method: 'GET',
    url: `/training/status/${jobId}`,
  });
  
  return response.data;
};

/**
 * Get training results after completion
 */
export const getTrainingResult = async (jobId: string): Promise<TrainingResult> => {
  const response = await request<TrainingResult>({
    method: 'GET',
    url: `/training/result/${jobId}`,
  });
  
  return response.data;
};

/**
 * Cancel a training job
 */
export const cancelTraining = async (jobId: string): Promise<{success: boolean}> => {
  const response = await request<{success: boolean}>({
    method: 'POST',
    url: `/training/cancel/${jobId}`,
  });
  
  return response.data;
};

/**
 * Poll for training status
 * @param jobId The ID of the training job
 * @param interval Polling interval in milliseconds
 * @param onStatusUpdate Callback function for status updates
 * @param onError Callback function for errors
 * @returns Function to stop polling
 */
export const pollTrainingStatus = (
  jobId: string,
  interval: number = 2000,
  onStatusUpdate: (status: TrainingStatus) => void,
  onError: (error: any) => void
): (() => void) => {
  let isPolling = true;
  
  const pollStatus = async () => {
    if (!isPolling) return;
    
    try {
      const status = await getTrainingStatus(jobId);
      onStatusUpdate(status);
      
      // Continue polling if training is still in progress
      if (status.status === 'pending' || status.status === 'training') {
        setTimeout(pollStatus, interval);
      }
    } catch (error) {
      onError(error);
      
      // Retry on error
      setTimeout(pollStatus, interval * 2);
    }
  };
  
  // Start polling
  pollStatus();
  
  // Return function to stop polling
  return () => {
    isPolling = false;
  };
}; 