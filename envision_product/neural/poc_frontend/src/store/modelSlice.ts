import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { getAvailableModels, getModelById } from '../services/model.service';
import { Model } from '../types/model.types';
import { ApiError } from '../types/api.types';

interface ModelState {
  models: Model[];
  selectedModelId: string | null;
  selectedModel: Model | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: ModelState = {
  models: [],
  selectedModelId: null,
  selectedModel: null,
  isLoading: false,
  error: null,
};

// Async thunks
export const fetchModels = createAsyncThunk<
  Model[],
  void,
  { rejectValue: ApiError }
>('model/fetchModels', async (_, { rejectWithValue }) => {
  try {
    return await getAvailableModels();
  } catch (error) {
    return rejectWithValue(error as ApiError);
  }
});

export const fetchModelById = createAsyncThunk<
  Model,
  string,
  { rejectValue: ApiError }
>('model/fetchModelById', async (modelId, { rejectWithValue }) => {
  try {
    return await getModelById(modelId);
  } catch (error) {
    return rejectWithValue(error as ApiError);
  }
});

const modelSlice = createSlice({
  name: 'model',
  initialState,
  reducers: {
    selectModel: (state, action: PayloadAction<string | null>) => {
      state.selectedModelId = action.payload;
      state.selectedModel = state.models.find(model => model.id === action.payload) || null;
    },
    clearModelState: (state) => {
      state.selectedModelId = null;
      state.selectedModel = null;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch models
      .addCase(fetchModels.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchModels.fulfilled, (state, action) => {
        state.isLoading = false;
        state.models = action.payload;
      })
      .addCase(fetchModels.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload?.message || 'Failed to fetch models';
      })
      // Fetch model by ID
      .addCase(fetchModelById.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchModelById.fulfilled, (state, action) => {
        state.isLoading = false;
        state.selectedModel = action.payload;
        state.selectedModelId = action.payload.id;
      })
      .addCase(fetchModelById.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload?.message || 'Failed to fetch model details';
      });
  },
});

export const { selectModel, clearModelState } = modelSlice.actions;

export default modelSlice.reducer; 