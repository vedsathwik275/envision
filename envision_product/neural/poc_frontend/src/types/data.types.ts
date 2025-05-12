export interface OrderVolumeData {
  'SOURCE CITY': string;
  'DESTINATION CITY': string;
  'ORDER TYPE': string;
  'ORDER MONTH': string;
  'ORDER VOLUME': number;
}

export interface DataPreview {
  fileId: string;
  fileName: string;
  columns: string[];
  sampleRows: any[][];
  totalRows: number;
}

export interface UploadResponse {
  status: string;
  fileId: string;
  preview: DataPreview;
}

export interface PredictionResult {
  'SOURCE CITY': string;
  'DESTINATION CITY': string;
  'ORDER TYPE': string;
  'PREDICTION YEAR': number;
  'PREDICTION MONTH': number;
  'PREDICTION DATE': string;
  'PREDICTED ORDER VOLUME': number;
}

export interface PredictionResults {
  results: PredictionResult[];
  modelId: string;
  fileId: string;
  trainingMetrics: {
    mae: number;
    rmse: number;
    r2: number;
  };
} 