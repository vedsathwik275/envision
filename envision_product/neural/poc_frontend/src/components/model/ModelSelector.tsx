import React, { useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  CircularProgress,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../../store';
import { fetchModels, selectModel } from '../../store/modelSlice';

interface ModelSelectorProps {
  onBack: () => void;
  onContinue: () => void;
}

const ModelSelector: React.FC<ModelSelectorProps> = ({ onBack, onContinue }) => {
  const dispatch = useDispatch<AppDispatch>();
  const { models, selectedModelId, isLoading, error } = useSelector(
    (state: RootState) => state.model
  );

  useEffect(() => {
    if (models.length === 0 && !isLoading) {
      dispatch(fetchModels());
    }
  }, [dispatch, models.length, isLoading]);

  const handleModelSelect = (modelId: string) => {
    dispatch(selectModel(modelId));
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Typography color="error" variant="body1" align="center">
        {error}
      </Typography>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Select a Model Type
      </Typography>

      <FormControl component="fieldset" sx={{ width: '100%' }}>
        <RadioGroup
          aria-label="model-selection"
          value={selectedModelId || ''}
          onChange={(e) => handleModelSelect(e.target.value)}
        >
          {models.map((model) => (
            <Card
              key={model.id}
              sx={{
                mb: 2,
                border: model.id === selectedModelId ? 2 : 1,
                borderColor: model.id === selectedModelId ? 'primary.main' : 'divider',
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                  <FormControlLabel
                    value={model.id}
                    control={<Radio />}
                    label={
                      <Typography variant="h6" component="div">
                        {model.name}
                      </Typography>
                    }
                  />
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  {model.description}
                </Typography>
                {!model.isAvailable && (
                  <Typography variant="body2" color="error" sx={{ mt: 1 }}>
                    This model is currently unavailable
                  </Typography>
                )}
              </CardContent>
            </Card>
          ))}
        </RadioGroup>
      </FormControl>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
        <Button variant="outlined" onClick={onBack}>
          Back to Data Preview
        </Button>
        <Button
          variant="contained"
          color="primary"
          onClick={onContinue}
          disabled={!selectedModelId || models.length === 0}
        >
          Train Model
        </Button>
      </Box>
    </Box>
  );
};

export default ModelSelector; 