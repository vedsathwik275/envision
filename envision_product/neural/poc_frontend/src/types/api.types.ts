export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export interface ApiError {
  status: number;
  message: string;
  details?: any;
}

export interface TrainingRequest {
  fileId: string;
  modelType: string;
}

export interface PredictionRequest {
  modelId: string;
  months?: number;
} 