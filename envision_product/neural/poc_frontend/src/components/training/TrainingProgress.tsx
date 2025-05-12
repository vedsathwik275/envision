import React, { useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  LinearProgress,
  Button,
  Paper,
  Chip,
  CircularProgress,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../../store';
import {
  startModelTraining,
  fetchTrainingStatus,
  cancelModelTraining,
  updateTrainingStatus,
} from '../../store/trainingSlice';
import { formatTimeRemaining } from '../../utils/formatters';
import { pollTrainingStatus } from '../../services/training.service';

interface TrainingProgressProps {
  fileId: string;
  modelId: string;
  onComplete: () => void;
  onCancel: () => void;
}

const TrainingProgress: React.FC<TrainingProgressProps> = ({
  fileId,
  modelId,
  onComplete,
  onCancel,
}) => {
  const dispatch = useDispatch<AppDispatch>();
  const {
    trainingJob,
    trainingStatus,
    isStartingTraining,
    isCancellingTraining,
    error,
  } = useSelector((state: RootState) => state.training);
  const { selectedModel } = useSelector((state: RootState) => state.model);

  // Start training when component mounts
  useEffect(() => {
    if (!trainingJob && !isStartingTraining) {
      dispatch(startModelTraining({ fileId, modelType: modelId }));
    }
  }, [dispatch, fileId, modelId, trainingJob, isStartingTraining]);

  // Setup polling for training status
  useEffect(() => {
    let stopPolling: (() => void) | null = null;

    if (trainingJob?.jobId) {
      stopPolling = pollTrainingStatus(
        trainingJob.jobId,
        2000, // Poll every 2 seconds
        (status) => {
          dispatch(updateTrainingStatus(status));
          
          // If training is complete, call onComplete
          if (status.status === 'completed') {
            onComplete();
          }
        },
        (error) => {
          console.error('Error polling training status:', error);
        }
      );
    }

    // Clean up polling when component unmounts
    return () => {
      if (stopPolling) {
        stopPolling();
      }
    };
  }, [dispatch, trainingJob?.jobId, onComplete]);

  // Handle cancel training
  const handleCancel = useCallback(async () => {
    if (trainingJob?.jobId) {
      await dispatch(cancelModelTraining(trainingJob.jobId)).unwrap();
      onCancel();
    }
  }, [dispatch, trainingJob?.jobId, onCancel]);

  // Show loading state while starting training
  if (isStartingTraining) {
    return (
      <Box sx={{ textAlign: 'center', my: 4 }}>
        <CircularProgress />
        <Typography variant="body1" sx={{ mt: 2 }}>
          Preparing training job...
        </Typography>
      </Box>
    );
  }

  // Show error state
  if (error) {
    return (
      <Box sx={{ textAlign: 'center', my: 4 }}>
        <Typography color="error" variant="body1">
          {error}
        </Typography>
        <Button variant="outlined" color="primary" onClick={onCancel} sx={{ mt: 2 }}>
          Back
        </Button>
      </Box>
    );
  }

  // Show training progress
  return (
    <Paper sx={{ p: 3, maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h6" gutterBottom>
        Training in Progress
      </Typography>
      
      {selectedModel && (
        <Typography variant="body2" color="textSecondary" gutterBottom>
          Model: {selectedModel.name}
        </Typography>
      )}
      
      <Box sx={{ mt: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2" color="textSecondary">
            Status:
          </Typography>
          <Chip
            label={trainingStatus?.status || 'Initializing'}
            color={
              trainingStatus?.status === 'completed'
                ? 'success'
                : trainingStatus?.status === 'failed'
                ? 'error'
                : 'primary'
            }
            size="small"
          />
        </Box>
        
        <LinearProgress
          variant="determinate"
          value={trainingStatus?.progress || 0}
          sx={{ height: 10, borderRadius: 5, my: 2 }}
        />
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
          <Typography variant="body2" color="textSecondary">
            Progress: {trainingStatus?.progress || 0}%
          </Typography>
          {trainingStatus?.timeRemaining && (
            <Typography variant="body2" color="textSecondary">
              Time remaining: {formatTimeRemaining(trainingStatus.timeRemaining)}
            </Typography>
          )}
        </Box>
        
        {trainingStatus?.currentEpoch && trainingStatus?.totalEpochs && (
          <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
            Epoch: {trainingStatus.currentEpoch} / {trainingStatus.totalEpochs}
          </Typography>
        )}
        
        {trainingStatus?.metrics && (
          <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
            <Typography variant="subtitle2" gutterBottom>
              Current Metrics
            </Typography>
            <Typography variant="body2">
              Loss: {trainingStatus.metrics.loss.toFixed(4)}
            </Typography>
            <Typography variant="body2">
              Accuracy: {(trainingStatus.metrics.accuracy * 100).toFixed(2)}%
            </Typography>
          </Box>
        )}
      </Box>
      
      <Box sx={{ mt: 3, textAlign: 'center' }}>
        <Button
          variant="outlined"
          color="error"
          onClick={handleCancel}
          disabled={isCancellingTraining}
        >
          {isCancellingTraining ? 'Cancelling...' : 'Cancel Training'}
        </Button>
      </Box>
    </Paper>
  );
};

export default TrainingProgress; 