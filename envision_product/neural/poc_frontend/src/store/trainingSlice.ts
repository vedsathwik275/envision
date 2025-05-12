import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { startTraining } from '../services/model.service';
import { getTrainingStatus, getTrainingResult, cancelTraining } from '../services/training.service';
import { TrainingJob, TrainingStatus, TrainingResult } from '../types/model.types';
import { ApiError } from '../types/api.types';

interface TrainingState {
  trainingJob: TrainingJob | null;
  trainingStatus: TrainingStatus | null;
  trainingResult: TrainingResult | null;
  isStartingTraining: boolean;
  isCancellingTraining: boolean;
  isFetchingStatus: boolean;
  error: string | null;
}

const initialState: TrainingState = {
  trainingJob: null,
  trainingStatus: null,
  trainingResult: null,
  isStartingTraining: false,
  isCancellingTraining: false,
  isFetchingStatus: false,
  error: null,
};

// Async thunks
export const startModelTraining = createAsyncThunk<
  TrainingJob,
  { fileId: string; modelType: string },
  { rejectValue: ApiError }
>('training/startTraining', async ({ fileId, modelType }, { rejectWithValue }) => {
  try {
    return await startTraining(fileId, modelType);
  } catch (error) {
    return rejectWithValue(error as ApiError);
  }
});

export const fetchTrainingStatus = createAsyncThunk<
  TrainingStatus,
  string,
  { rejectValue: ApiError }
>('training/fetchStatus', async (jobId, { rejectWithValue }) => {
  try {
    return await getTrainingStatus(jobId);
  } catch (error) {
    return rejectWithValue(error as ApiError);
  }
});

export const fetchTrainingResult = createAsyncThunk<
  TrainingResult,
  string,
  { rejectValue: ApiError }
>('training/fetchResult', async (jobId, { rejectWithValue }) => {
  try {
    return await getTrainingResult(jobId);
  } catch (error) {
    return rejectWithValue(error as ApiError);
  }
});

export const cancelModelTraining = createAsyncThunk<
  { success: boolean },
  string,
  { rejectValue: ApiError }
>('training/cancelTraining', async (jobId, { rejectWithValue }) => {
  try {
    return await cancelTraining(jobId);
  } catch (error) {
    return rejectWithValue(error as ApiError);
  }
});

const trainingSlice = createSlice({
  name: 'training',
  initialState,
  reducers: {
    updateTrainingStatus: (state, action: PayloadAction<TrainingStatus>) => {
      state.trainingStatus = action.payload;
      // If training is complete, update the job status as well
      if (state.trainingJob && ['completed', 'failed'].includes(action.payload.status)) {
        state.trainingJob.status = action.payload.status;
        state.trainingJob.progress = action.payload.progress;
      }
    },
    clearTrainingState: (state) => {
      Object.assign(state, initialState);
    },
  },
  extraReducers: (builder) => {
    builder
      // Start training
      .addCase(startModelTraining.pending, (state) => {
        state.isStartingTraining = true;
        state.error = null;
      })
      .addCase(startModelTraining.fulfilled, (state, action) => {
        state.isStartingTraining = false;
        state.trainingJob = action.payload;
        state.trainingStatus = {
          status: action.payload.status,
          progress: 0,
        };
      })
      .addCase(startModelTraining.rejected, (state, action) => {
        state.isStartingTraining = false;
        state.error = action.payload?.message || 'Failed to start training';
      })
      // Fetch training status
      .addCase(fetchTrainingStatus.pending, (state) => {
        state.isFetchingStatus = true;
      })
      .addCase(fetchTrainingStatus.fulfilled, (state, action) => {
        state.isFetchingStatus = false;
        state.trainingStatus = action.payload;
        // If job exists, update its status too
        if (state.trainingJob) {
          state.trainingJob.status = action.payload.status;
          state.trainingJob.progress = action.payload.progress;
        }
      })
      .addCase(fetchTrainingStatus.rejected, (state, action) => {
        state.isFetchingStatus = false;
        state.error = action.payload?.message || 'Failed to fetch training status';
      })
      // Fetch training result
      .addCase(fetchTrainingResult.pending, (state) => {
        state.error = null;
      })
      .addCase(fetchTrainingResult.fulfilled, (state, action) => {
        state.trainingResult = action.payload;
      })
      .addCase(fetchTrainingResult.rejected, (state, action) => {
        state.error = action.payload?.message || 'Failed to fetch training result';
      })
      // Cancel training
      .addCase(cancelModelTraining.pending, (state) => {
        state.isCancellingTraining = true;
        state.error = null;
      })
      .addCase(cancelModelTraining.fulfilled, (state) => {
        state.isCancellingTraining = false;
        if (state.trainingJob) {
          state.trainingJob.status = 'failed';
        }
        if (state.trainingStatus) {
          state.trainingStatus.status = 'failed';
        }
      })
      .addCase(cancelModelTraining.rejected, (state, action) => {
        state.isCancellingTraining = false;
        state.error = action.payload?.message || 'Failed to cancel training';
      });
  },
});

export const { updateTrainingStatus, clearTrainingState } = trainingSlice.actions;

export default trainingSlice.reducer; 