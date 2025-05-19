import React, { createContext, useContext, useState, useEffect } from "react";
import { 
  modelApi, 
  predictionApi, 
  fileApi, 
  ModelMetadata, 
  FileMetadata,
  ModelListResponse
} from "../services/api";

// Extend the interfaces for our specific needs
interface Model extends ModelMetadata {
  name: string; // We ensure name is always present
}

interface File extends FileMetadata {
  size?: number;
  rows?: number;
  columns?: number;
}

interface Prediction {
  prediction_id: string;
  model_id: string;
  model_type: string;
  created_at: string;
  prediction_count: number;
  metrics?: Record<string, any>;
  title: string; // Derived from model_type
  lanes: number; // Derived from prediction_count
}

interface Stats {
  activeModels: number;
  modelAccuracy: number;
  predictionsGenerated: number;
  datasetCount: number;
}

interface AppContextProps {
  models: Model[];
  files: File[];
  predictions: Prediction[];
  stats: Stats;
  locations: string[];
  loading: {
    models: boolean;
    files: boolean;
    predictions: boolean;
  };
  refreshModels: () => void;
  refreshFiles: () => void;
  refreshPredictions: () => void;
  addModel: (model: Model) => void;
  addFile: (file: File) => void;
  addPrediction: (prediction: Prediction) => void;
}

const AppContext = createContext<AppContextProps | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [models, setModels] = useState<Model[]>([]);
  const [files, setFiles] = useState<File[]>([]);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [locations, setLocations] = useState<string[]>([]);
  const [stats, setStats] = useState<Stats>({
    activeModels: 0,
    modelAccuracy: 0,
    predictionsGenerated: 0,
    datasetCount: 0
  });
  const [loading, setLoading] = useState({
    models: true,
    files: true,
    predictions: true
  });
  
  // Initialize data on load
  useEffect(() => {
    refreshData();
  }, []);
  
  const refreshData = () => {
    refreshModels();
    refreshFiles();
    refreshPredictions();
    calculateStats();
  };
  
  // Calculate dashboard stats based on actual data
  const calculateStats = () => {
    // This will be called after models, files, and predictions are loaded
    // to calculate real statistics instead of using mock data
    let activeModelCount = 0;
    let totalAccuracy = 0;
    let accuracyCount = 0;
    
    models.forEach(model => {
      if (model.status !== "failed" && model.status !== "training") {
        activeModelCount++;
        
        // If the model has an r2 value in its evaluation, use it for accuracy
        if (model.evaluation?.r2) {
          totalAccuracy += model.evaluation.r2;
          accuracyCount++;
        }
      }
    });
    
    setStats({
      activeModels: activeModelCount,
      modelAccuracy: accuracyCount > 0 ? +(totalAccuracy / accuracyCount * 100).toFixed(1) : 0,
      predictionsGenerated: predictions.length,
      datasetCount: files.length
    });
  };
  
  const refreshModels = async () => {
    setLoading(prev => ({ ...prev, models: true }));
    
    try {
      const data = await modelApi.listModels();
      
      if (data && data.models && Array.isArray(data.models)) {
        // Format models to match our interface
        const formattedModels = data.models.map((model: ModelMetadata): Model => ({
          ...model,
          // Add status field if it doesn't exist (most models are active)
          status: model.status || "active",
          // Add a name field derived from model_id if it doesn't exist
          name: model.name || formatModelName(model.model_id, model.model_type)
        }));
        
        setModels(formattedModels);
      }
    } catch (error) {
      console.error("Error fetching models:", error);
      // In case of error, keep existing models
    } finally {
      setLoading(prev => ({ ...prev, models: false }));
    }
  };
  
  const formatModelName = (modelId: string, modelType: string) => {
    // Format model_id into a readable name
    const typeFormatted = modelType
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
    
    return `${typeFormatted} Model ${modelId.split('_').pop()}`;
  };
  
  const refreshFiles = async () => {
    setLoading(prev => ({ ...prev, files: true }));
    
    try {
      // Note: If there's no dedicated files listing endpoint, we may need to implement this differently
      // or use a different approach to track files in the frontend
      // This is a placeholder for when a files API is available
      const response = await fileApi.listFiles();
      
      if (response && Array.isArray(response)) {
        setFiles(response);
      }
    } catch (error) {
      console.error("Error fetching files:", error);
      // In case of error or missing endpoint, keep existing files
    } finally {
      setLoading(prev => ({ ...prev, files: false }));
    }
  };
  
  const refreshPredictions = async () => {
    setLoading(prev => ({ ...prev, predictions: true }));
    const allPredictions: Prediction[] = [];
    
    try {
      // Since we don't have a single endpoint to list all predictions,
      // we need to iterate through each model and get its predictions
      for (const model of models) {
        try {
          let response;
          
          switch (model.model_type) {
            case 'order_volume':
              response = await predictionApi.getOrderVolumePredictions(model.model_id);
              if (response) {
                // Format the response as needed
                const prediction: Prediction = {
                  prediction_id: response.prediction_id || `pred-${Date.now()}`,
                  model_id: model.model_id,
                  model_type: model.model_type,
                  created_at: response.created_at || new Date().toISOString(),
                  prediction_count: response.total_predictions || response.predictions?.length || 0,
                  metrics: response.metrics,
                  title: `Order Volume Prediction for ${model.model_id}`,
                  lanes: response.filtered_predictions || response.predictions?.length || 0
                };
                allPredictions.push(prediction);
              }
              break;
              
            case 'tender_performance':
              response = await predictionApi.getTenderPerformancePredictions(model.model_id);
              if (response) {
                const prediction: Prediction = {
                  prediction_id: response.prediction_id || `pred-${Date.now()}`,
                  model_id: model.model_id,
                  model_type: model.model_type,
                  created_at: response.created_at || new Date().toISOString(),
                  prediction_count: response.prediction_count || 0,
                  metrics: response.metrics,
                  title: `Tender Performance Prediction for ${model.model_id}`,
                  lanes: response.prediction_count || 0
                };
                allPredictions.push(prediction);
              }
              break;
              
            case 'carrier_performance':
              response = await predictionApi.getCarrierPerformancePredictions(model.model_id);
              if (response) {
                const prediction: Prediction = {
                  prediction_id: response.prediction_id || `pred-${Date.now()}`,
                  model_id: model.model_id,
                  model_type: model.model_type,
                  created_at: response.created_at || new Date().toISOString(),
                  prediction_count: response.prediction_count || 0,
                  metrics: response.metrics,
                  title: `Carrier Performance Prediction for ${model.model_id}`,
                  lanes: response.prediction_count || 0
                };
                allPredictions.push(prediction);
              }
              break;
          }
        } catch (error) {
          console.error(`Error fetching predictions for model ${model.model_id}:`, error);
          // Continue with other models in case of error
          continue;
        }
      }
      
      setPredictions(allPredictions);
    } catch (error) {
      console.error("Error in prediction refresh process:", error);
      // In case of error, keep existing predictions
    } finally {
      setLoading(prev => ({ ...prev, predictions: false }));
      calculateStats();
    }
  };
  
  const addModel = (model: Model) => {
    setModels(prev => [model, ...prev]);
    // Refresh stats after adding a model
    calculateStats();
  };
  
  const addFile = (file: File) => {
    setFiles(prev => [file, ...prev]);
    // Refresh stats after adding a file
    calculateStats();
  };
  
  const addPrediction = (prediction: Prediction) => {
    setPredictions(prev => [prediction, ...prev]);
    // Refresh stats after adding a prediction
    calculateStats();
  };
  
  const value = {
    models,
    files,
    predictions,
    stats,
    locations,
    loading,
    refreshModels,
    refreshFiles,
    refreshPredictions,
    addModel,
    addFile,
    addPrediction
  };
  
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error("useApp must be used within an AppProvider");
  }
  return context;
};
