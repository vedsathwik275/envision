import { configureStore } from '@reduxjs/toolkit';
import uploadReducer from './uploadSlice';
import modelReducer from './modelSlice';
import trainingReducer from './trainingSlice';
import predictionReducer from './predictionSlice';

export const store = configureStore({
  reducer: {
    upload: uploadReducer,
    model: modelReducer,
    training: trainingReducer,
    prediction: predictionReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore non-serializable values for specific action paths
        ignoredActions: ['upload/setFile'],
        ignoredPaths: ['upload.file'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 