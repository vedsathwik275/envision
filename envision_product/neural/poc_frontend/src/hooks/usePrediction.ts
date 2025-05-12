import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../store';
import { 
  fetchPredictionResults, 
  generateModelPredictions, 
  exportPredictionResults,
  clearPredictionState
} from '../store/predictionSlice';
import { PredictionResults } from '../types/data.types';

// Define the prediction state shape for type safety
interface PredictionState {
  predictionResults: PredictionResults | null;
  isGenerating: boolean;
  isExporting: boolean;
  isFetching: boolean;
  error: string | null;
  exportedBlob: Blob | null;
}

/**
 * Custom hook for prediction functionality
 */
export const usePrediction = () => {
  const dispatch = useDispatch<AppDispatch>();
  
  // Safely access the prediction state with proper typing
  const predictionState = useSelector((state: RootState) => {
    return state.prediction as PredictionState;
  });

  /**
   * Fetch prediction results for a model
   */
  const fetchResults = (modelId: string) => {
    return dispatch(fetchPredictionResults(modelId));
  };

  /**
   * Generate predictions
   */
  const generatePredictions = (modelId: string, months?: number) => {
    return dispatch(generateModelPredictions({ modelId, months }));
  };

  /**
   * Export prediction results
   */
  const exportResults = (modelId: string, format?: string) => {
    return dispatch(exportPredictionResults({ modelId, format }));
  };

  /**
   * Clear prediction state
   */
  const clearState = () => {
    dispatch(clearPredictionState());
  };

  return {
    // State
    ...predictionState,
    
    // Actions
    fetchResults,
    generatePredictions,
    exportResults,
    clearState
  };
}; 