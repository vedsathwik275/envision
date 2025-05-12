import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { generatePredictions, getPredictions, exportPredictions } from '../services/prediction.service';
import { PredictionResults } from '../types/data.types';
import { ApiError } from '../types/api.types';

interface PredictionState {
  predictionResults: PredictionResults | null;
  isGenerating: boolean;
  isExporting: boolean;
  isFetching: boolean;
  exportedBlob: Blob | null;
  error: string | null;
}

const initialState: PredictionState = {
  predictionResults: null,
  isGenerating: false,
  isExporting: false,
  isFetching: false,
  exportedBlob: null,
  error: null,
};

// Async thunks
export const generateModelPredictions = createAsyncThunk<
  PredictionResults,
  { modelId: string; months?: number },
  { rejectValue: ApiError }
>('prediction/generatePredictions', async ({ modelId, months }, { rejectWithValue }) => {
  try {
    return await generatePredictions(modelId, months);
  } catch (error) {
    return rejectWithValue(error as ApiError);
  }
});

export const fetchPredictionResults = createAsyncThunk<
  PredictionResults,
  string,
  { rejectValue: ApiError }
>('prediction/fetchResults', async (modelId, { rejectWithValue }) => {
  try {
    return await getPredictions(modelId);
  } catch (error) {
    return rejectWithValue(error as ApiError);
  }
});

export const exportPredictionResults = createAsyncThunk<
  Blob,
  { modelId: string; format?: string },
  { rejectValue: ApiError }
>('prediction/exportResults', async ({ modelId, format }, { rejectWithValue }) => {
  try {
    return await exportPredictions(modelId, format);
  } catch (error) {
    return rejectWithValue(error as ApiError);
  }
});

const predictionSlice = createSlice({
  name: 'prediction',
  initialState,
  reducers: {
    clearPredictionState: (state) => {
      Object.assign(state, initialState);
    },
    clearExportedBlob: (state) => {
      state.exportedBlob = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Generate predictions
      .addCase(generateModelPredictions.pending, (state) => {
        state.isGenerating = true;
        state.error = null;
      })
      .addCase(generateModelPredictions.fulfilled, (state, action) => {
        state.isGenerating = false;
        state.predictionResults = action.payload;
      })
      .addCase(generateModelPredictions.rejected, (state, action) => {
        state.isGenerating = false;
        state.error = action.payload?.message || 'Failed to generate predictions';
      })
      // Fetch prediction results
      .addCase(fetchPredictionResults.pending, (state) => {
        state.isFetching = true;
        state.error = null;
      })
      .addCase(fetchPredictionResults.fulfilled, (state, action) => {
        state.isFetching = false;
        state.predictionResults = action.payload;
      })
      .addCase(fetchPredictionResults.rejected, (state, action) => {
        state.isFetching = false;
        state.error = action.payload?.message || 'Failed to fetch prediction results';
      })
      // Export prediction results
      .addCase(exportPredictionResults.pending, (state) => {
        state.isExporting = true;
        state.error = null;
        state.exportedBlob = null;
      })
      .addCase(exportPredictionResults.fulfilled, (state, action) => {
        state.isExporting = false;
        state.exportedBlob = action.payload;
      })
      .addCase(exportPredictionResults.rejected, (state, action) => {
        state.isExporting = false;
        state.error = action.payload?.message || 'Failed to export prediction results';
      });
  },
});

export const { clearPredictionState, clearExportedBlob } = predictionSlice.actions;

export default predictionSlice.reducer; 