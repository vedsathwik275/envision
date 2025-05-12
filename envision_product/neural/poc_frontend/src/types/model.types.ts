export interface Model {
  id: string;
  name: string;
  description: string;
  requiredColumns: string[];
  targetColumn: string;
  isAvailable: boolean;
}

export interface TrainingJob {
  jobId: string;
  status: 'pending' | 'training' | 'completed' | 'failed';
  progress: number;
  modelType: string;
  fileId: string;
  createdAt: string;
  completedAt?: string;
  error?: string;
}

export interface TrainingStatus {
  status: 'pending' | 'training' | 'completed' | 'failed';
  progress: number;
  currentEpoch?: number;
  totalEpochs?: number;
  timeRemaining?: number;
  metrics?: {
    loss: number;
    accuracy: number;
  };
  error?: string;
}

export interface TrainingResult {
  modelId: string;
  metrics: {
    mae: number;
    rmse: number;
    r2: number;
  };
  fileId: string;
  jobId: string;
  evaluationImage?: string;
} 