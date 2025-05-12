
import { create } from 'zustand';

export type ModelType = 'order-volume' | 'customer-churn' | 'price-optimization';

export interface Model {
  id: string;
  name: string;
  type: ModelType;
  description: string;
  lastTrained: string | null;
  accuracy: number | null;
}

export interface TrainingProgress {
  modelId: string;
  progress: number;
  status: 'idle' | 'training' | 'completed' | 'failed';
  message: string;
}

export interface PredictionResult {
  id: string;
  modelId: string;
  modelName: string;
  dateCreated: string;
  metrics: {
    accuracy: number;
    precision: number;
    recall: number;
    f1Score: number;
  };
  chartData: Array<{
    name: string;
    actual: number;
    predicted: number;
  }>;
}

interface ModelState {
  models: Model[];
  selectedModelId: string | null;
  trainingProgress: TrainingProgress | null;
  predictionResults: PredictionResult[];
  isUploading: boolean;
  uploadProgress: number;
  uploadedFile: File | null;
  
  // Actions
  selectModel: (modelId: string) => void;
  updateTrainingProgress: (progress: TrainingProgress) => void;
  startFileUpload: (file: File) => void;
  updateUploadProgress: (progress: number) => void;
  completeFileUpload: () => void;
  addPredictionResult: (result: PredictionResult) => void;
}

export const useModelStore = create<ModelState>((set) => ({
  models: [
    {
      id: 'model-001',
      name: 'Order Volume Model',
      type: 'order-volume',
      description: 'Predicts future order volumes based on historical data and seasonal patterns.',
      lastTrained: null,
      accuracy: null
    }
  ],
  selectedModelId: null,
  trainingProgress: null,
  predictionResults: [],
  isUploading: false,
  uploadProgress: 0,
  uploadedFile: null,
  
  // Actions
  selectModel: (modelId) => set({ selectedModelId: modelId }),
  updateTrainingProgress: (progress) => set({ trainingProgress: progress }),
  startFileUpload: (file) => set({ isUploading: true, uploadProgress: 0, uploadedFile: file }),
  updateUploadProgress: (progress) => set({ uploadProgress: progress }),
  completeFileUpload: () => set({ isUploading: false, uploadProgress: 100 }),
  addPredictionResult: (result) => set((state) => ({ 
    predictionResults: [result, ...state.predictionResults] 
  }))
}));
