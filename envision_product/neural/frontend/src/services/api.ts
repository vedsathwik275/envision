import axios, { AxiosResponse } from "axios";

// Define some common response types
export interface ApiResponse<T = any> {
  data?: T;
  success?: boolean;
  error?: {
    code: number;
    message: string;
  };
}

// Model interfaces
export interface ModelMetadata {
  model_id: string;
  model_type: string;
  created_at: string;
  description?: string;
  name?: string;
  evaluation?: {
    mae?: number;
    mse?: number;
    rmse?: number;
    r2?: number;
  };
  training_data?: string;
  training_params?: Record<string, any>;
  status?: string;
}

export interface PaginationMetadata {
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ModelListResponse {
  models: ModelMetadata[];
  pagination?: PaginationMetadata;
}

// Prediction interfaces
export interface OrderVolumePrediction {
  source_city: string;
  destination_city: string;
  carrier?: string;
  order_type?: string;
  month: string;
  predicted_volume: number;
}

export interface OrderVolumePredictionResponse {
  model_id: string;
  prediction_id: string;
  created_at: string;
  total_predictions: number;
  filtered_predictions: number;
  returned_predictions: number;
  has_csv_export: boolean;
  csv_path?: string;
  json_path?: string;
  predictions: OrderVolumePrediction[];
}

export interface TenderPerformancePrediction {
  carrier: string;
  source_city: string;
  dest_city: string;
  predicted_performance: number;
  actual_performance?: number;
  absolute_error?: number;
  percent_error?: number;
}

export interface TenderPerformanceResponse {
  model_id: string;
  prediction_id?: string;
  created_at?: string;
  prediction_count: number;
  metrics?: {
    mae?: number;
    mape?: number;
    records_analyzed?: number;
  };
  predictions: TenderPerformancePrediction[];
}

export interface CarrierPerformancePrediction {
  carrier: string;
  source_city: string;
  dest_city: string;
  predicted_ontime_performance: number;
  actual_ontime_performance?: number;
  absolute_error?: number;
  percent_error?: number;
}

export interface CarrierPerformanceResponse {
  prediction_id: string;
  model_id: string;
  model_type: string;
  created_at: string;
  prediction_count: number;
  data?: {
    prediction_time: string;
    metrics?: {
      mae?: number;
      mape?: number;
      rmse?: number;
      records_analyzed?: number;
    };
    predictions: CarrierPerformancePrediction[];
  };
  metrics?: {
    mae?: number;
    mape?: number;
    rmse?: number;
    records_analyzed?: number;
  };
}

// File interfaces
export interface FileMetadata {
  file_id: string;
  filename: string;
  content_type: string;
  timestamp?: string;
}

export interface DataPreview {
  file_id: string;
  total_rows: number;
  total_columns: number;
  sample_rows: Record<string, any>[];
  column_info: Record<string, {
    type: string;
    unique_values: number;
    missing_values: number;
  }>;
  missing_data_summary: {
    total_missing: number;
    percent_missing: number;
  };
}

// Training response interfaces
export interface TrainingResponse {
  status: string;
  message: string;
  model_id?: string;
}

// Create an axios instance with default configuration
const api = axios.create({
  baseURL: "http://localhost:8000/api",
  timeout: 30000, // 30 seconds
  headers: {
    "Content-Type": "application/json",
  },
});

// Add a request interceptor for authentication headers and request handling
api.interceptors.request.use(
  (config) => {
    // Get token from local storage or other source if needed
    const token = localStorage.getItem("auth_token");
    
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    // Unwrap successful responses if they follow the standard pattern
    if (response.data && typeof response.data === 'object' && 'success' in response.data) {
      return response.data.data ? response.data.data : response.data;
    }
    return response.data;
  },
  (error) => {
    // Handle different error cases
    const { response } = error;
    
    if (response && response.status === 401) {
      // Handle unauthorized access (e.g., redirect to login)
      console.error("Unauthorized access. Please log in again.");
      // localStorage.removeItem("auth_token");
      // window.location.href = "/login";
    } else if (response && response.status === 403) {
      console.error("Permission denied. You don't have access to this resource.");
    } else if (response && response.status >= 500) {
      console.error("Server error. Please try again later or contact support.");
    } else if (!response) {
      console.error("Network error. Please check your connection.");
    }
    
    // Extract error message if available
    let errorMessage = "An unknown error occurred";
    if (response && response.data) {
      if (response.data.error && response.data.error.message) {
        errorMessage = response.data.error.message;
      } else if (response.data.detail) {
        errorMessage = response.data.detail;
      } else if (typeof response.data === 'string') {
        errorMessage = response.data;
      }
    }
    
    return Promise.reject({
      status: response ? response.status : 0,
      message: errorMessage,
      originalError: error
    });
  }
);

// File Management API
export const fileApi = {
  upload: (file: File, onProgress?: (percentage: number) => void): Promise<FileMetadata> => {
    const formData = new FormData();
    formData.append("file", file);
    
    return api.post("/files/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const percentage = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentage);
        }
      },
    });
  },
  
  uploadCSV: (file: File, onProgress?: (percentage: number) => void): Promise<FileMetadata> => {
    const formData = new FormData();
    formData.append("file", file);
    
    return api.post("/files/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const percentage = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentage);
        }
      },
    });
  },
  
  getPreview: (fileId: string): Promise<DataPreview> => {
    return api.get(`/data/preview/${fileId}`);
  },
  
  listFiles: (): Promise<FileMetadata[]> => {
    return api.get("/files");
  }
};

// Model Management API
export const modelApi = {
  listModels: (filters?: Record<string, any>): Promise<ModelListResponse> => {
    return api.get("/models", { params: filters });
  },
  
  getLatestModel: (modelType: string, filters?: Record<string, any>): Promise<ModelMetadata> => {
    return api.get("/models/latest", { 
      params: { 
        model_type: modelType,
        ...filters 
      } 
    });
  },
  
  getModelDetails: (modelId: string): Promise<ModelMetadata> => {
    return api.get(`/models/${modelId}`);
  },
  
  trainOrderVolumeModel: (dataFileId: string, params?: Record<string, any>): Promise<TrainingResponse> => {
    return api.post("/models/train/order-volume", null, {
      params: {
        data_file_id: dataFileId,
        ...params
      }
    });
  },
  
  trainTenderPerformanceModel: (dataFileId: string, params?: Record<string, any>): Promise<TrainingResponse> => {
    return api.post("/models/train/tender-performance", null, {
      params: {
        data_file_id: dataFileId,
        ...params
      }
    });
  },
  
  trainCarrierPerformanceModel: (dataFileId: string, params?: Record<string, any>): Promise<TrainingResponse> => {
    return api.post("/models/train/carrier-performance", null, {
      params: {
        data_file_id: dataFileId,
        ...params
      }
    });
  },
  
  deleteModel: (modelId: string): Promise<{ status: string; message: string }> => {
    return api.delete(`/models/${modelId}`);
  }
};

// Prediction Management API
export const predictionApi = {
  // Order Volume predictions
  generateOrderVolumePrediction: (modelId: string, months: number = 6): Promise<OrderVolumePredictionResponse> => {
    return api.post("/predictions/order-volume", {
      model_id: modelId,
      months: months
    });
  },
  
  getOrderVolumePredictions: (modelId: string, filters?: Record<string, any>): Promise<OrderVolumePredictionResponse> => {
    return api.get(`/predictions/order-volume/${modelId}`, {
      params: filters
    });
  },
  
  getOrderVolumeByLane: (modelId: string, sourceCity: string, destinationCity: string, filters?: Record<string, any>): Promise<OrderVolumePredictionResponse> => {
    return api.get(`/predictions/order-volume/${modelId}/by-lane`, {
      params: {
        source_city: sourceCity,
        destination_city: destinationCity,
        ...filters
      }
    });
  },
  
  downloadOrderVolumePredictions: (modelId: string, format: string = 'csv'): Promise<Blob> => {
    return api.get(`/predictions/order-volume/${modelId}/download`, {
      params: { format },
      responseType: 'blob'
    });
  },
  
  // Tender Performance predictions
  generateTenderPerformancePrediction: (modelId: string): Promise<TenderPerformanceResponse> => {
    return api.post("/predictions/tender-performance", {
      model_id: modelId
    });
  },
  
  getTenderPerformancePredictions: (modelId: string, simplified: boolean = true): Promise<TenderPerformanceResponse> => {
    return api.get(`/predictions/tender-performance/${modelId}`, {
      params: { simplified }
    });
  },
  
  getTenderPerformanceByLane: (
    modelId: string, 
    sourceCity: string, 
    destCity: string, 
    carrier?: string, 
    simplified: boolean = true
  ): Promise<TenderPerformanceResponse> => {
    return api.get(`/predictions/tender-performance/${modelId}/by-lane`, {
      params: {
        source_city: sourceCity,
        dest_city: destCity,
        carrier,
        simplified
      }
    });
  },
  
  downloadTenderPerformancePredictions: (
    modelId: string, 
    format: string = 'csv', 
    simplified: boolean = true,
    filters?: Record<string, any>
  ): Promise<Blob> => {
    return api.get(`/predictions/tender-performance/${modelId}/download`, {
      params: {
        format,
        simplified,
        ...filters
      },
      responseType: 'blob'
    });
  },
  
  // Carrier Performance predictions
  generateCarrierPerformancePrediction: (modelId: string): Promise<CarrierPerformanceResponse> => {
    return api.post("/predictions/carrier-performance", {
      model_id: modelId
    });
  },
  
  getCarrierPerformancePredictions: (modelId: string, simplified: boolean = true): Promise<CarrierPerformanceResponse> => {
    return api.get(`/predictions/carrier-performance/${modelId}`, {
      params: { simplified }
    });
  },
  
  getCarrierPerformanceByLane: (
    modelId: string, 
    sourceCity: string, 
    destCity: string, 
    carrier?: string, 
    simplified: boolean = true
  ): Promise<CarrierPerformanceResponse> => {
    return api.get(`/predictions/carrier-performance/${modelId}/by-lane`, {
      params: {
        source_city: sourceCity,
        dest_city: destCity,
        carrier,
        simplified
      }
    });
  },
  
  downloadCarrierPerformancePredictions: (
    modelId: string, 
    format: string = 'csv', 
    simplified: boolean = true,
    filters?: Record<string, any>
  ): Promise<Blob> => {
    return api.get(`/predictions/carrier-performance/${modelId}/download`, {
      params: {
        format,
        simplified,
        ...filters
      },
      responseType: 'blob'
    });
  }
};

// Helper to format downloaded files
export const formatDownloadedFile = (blob: Blob, filename: string): void => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

// Lane Analysis API
export const laneApi = {
  getLaneDetails: (origin: string, destination: string) => {
    return api.get(`/lanes/details`, {
      params: { origin, destination }
    });
  },
  
  getLocations: () => {
    return api.get("/lanes/locations");
  }
};

export default api;
