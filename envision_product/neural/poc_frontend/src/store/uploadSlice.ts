import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { uploadFile, getDataPreview, validateFileForModel } from '../services/upload.service';
import { UploadResponse, DataPreview } from '../types/data.types';
import { ApiError } from '../types/api.types';

interface UploadState {
  file: File | null;
  fileId: string | null;
  preview: DataPreview | null;
  isUploading: boolean;
  uploadProgress: number;
  error: string | null;
  validationErrors: string[] | null;
  isValidForModel: boolean | null;
}

const initialState: UploadState = {
  file: null,
  fileId: null,
  preview: null,
  isUploading: false,
  uploadProgress: 0,
  error: null,
  validationErrors: null,
  isValidForModel: null,
};

// Async thunks
export const uploadDataFile = createAsyncThunk<
  UploadResponse,
  File,
  { rejectValue: ApiError }
>('upload/uploadDataFile', async (file, { rejectWithValue }) => {
  try {
    return await uploadFile(file);
  } catch (error) {
    return rejectWithValue(error as ApiError);
  }
});

export const fetchDataPreview = createAsyncThunk<
  DataPreview,
  string,
  { rejectValue: ApiError }
>('upload/fetchDataPreview', async (fileId, { rejectWithValue }) => {
  try {
    return await getDataPreview(fileId);
  } catch (error) {
    return rejectWithValue(error as ApiError);
  }
});

export const validateFile = createAsyncThunk<
  { isValid: boolean; errors?: string[] },
  { fileId: string; modelId: string },
  { rejectValue: ApiError }
>('upload/validateFile', async ({ fileId, modelId }, { rejectWithValue }) => {
  try {
    return await validateFileForModel(fileId, modelId);
  } catch (error) {
    return rejectWithValue(error as ApiError);
  }
});

const uploadSlice = createSlice({
  name: 'upload',
  initialState,
  reducers: {
    setFile: (state, action: PayloadAction<File | null>) => {
      state.file = action.payload;
      // Reset other states when a new file is set
      if (action.payload === null) {
        state.fileId = null;
        state.preview = null;
        state.isValidForModel = null;
        state.validationErrors = null;
      }
    },
    setUploadProgress: (state, action: PayloadAction<number>) => {
      state.uploadProgress = action.payload;
    },
    clearUploadState: (state) => {
      // Reset to initial state
      Object.assign(state, initialState);
    },
  },
  extraReducers: (builder) => {
    builder
      // Upload file
      .addCase(uploadDataFile.pending, (state) => {
        state.isUploading = true;
        state.error = null;
        state.uploadProgress = 0;
      })
      .addCase(uploadDataFile.fulfilled, (state, action) => {
        state.isUploading = false;
        state.fileId = action.payload.fileId;
        state.preview = action.payload.preview;
        state.uploadProgress = 100;
      })
      .addCase(uploadDataFile.rejected, (state, action) => {
        state.isUploading = false;
        state.error = action.payload?.message || 'Upload failed';
      })
      // Fetch data preview
      .addCase(fetchDataPreview.pending, (state) => {
        state.error = null;
      })
      .addCase(fetchDataPreview.fulfilled, (state, action) => {
        state.preview = action.payload;
      })
      .addCase(fetchDataPreview.rejected, (state, action) => {
        state.error = action.payload?.message || 'Failed to fetch data preview';
      })
      // Validate file
      .addCase(validateFile.pending, (state) => {
        state.isValidForModel = null;
        state.validationErrors = null;
        state.error = null;
      })
      .addCase(validateFile.fulfilled, (state, action) => {
        state.isValidForModel = action.payload.isValid;
        state.validationErrors = action.payload.errors || null;
      })
      .addCase(validateFile.rejected, (state, action) => {
        state.error = action.payload?.message || 'Validation failed';
      });
  },
});

export const { setFile, setUploadProgress, clearUploadState } = uploadSlice.actions;

export default uploadSlice.reducer; 