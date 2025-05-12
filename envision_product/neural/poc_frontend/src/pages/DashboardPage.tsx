import React, { useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box,
  Card, 
  CardContent, 
  CardActions, 
  Button, 
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Paper
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../components/layout/MainLayout';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../store';
import { fetchModels } from '../store/modelSlice';
import VisibilityIcon from '@mui/icons-material/Visibility';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import BarChartIcon from '@mui/icons-material/BarChart';
import { formatDateTime } from '../utils/formatters';

// Import MUI v5's Grid from this package
import Grid from '@mui/material/Grid';

// Define model state interface
interface ModelState {
  models: Array<{
    id: string;
    name: string;
    description: string;
  }>;
  isLoading: boolean;
  error: string | null;
}

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  
  // Get models from store with type casting
  const { models, isLoading: isLoadingModels, error: modelsError } = useSelector(
    (state: RootState) => state.model as ModelState
  );

  // Get prediction results from store (mock data for now)
  const recentPredictions = [
    { id: 'pred-1', modelId: 'model-123', name: 'Q2 2023 Forecast', timestamp: new Date().toISOString() },
    { id: 'pred-2', modelId: 'model-456', name: 'Summer 2023 Forecast', timestamp: new Date(Date.now() - 86400000).toISOString() },
  ];

  useEffect(() => {
    dispatch(fetchModels());
  }, [dispatch]);

  const handleNewPrediction = () => {
    navigate('/upload');
  };

  const handleViewModel = (modelId: string) => {
    navigate(`/models/${modelId}`);
  };

  const handleViewResults = (modelId: string) => {
    navigate(`/results/${modelId}`);
  };

  return (
    <MainLayout title="Dashboard">
      <Container maxWidth="lg">
        <Box sx={{ my: 4 }}>
          {/* Use sx props directly instead of using Grid for layout */}
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr', gap: 4, mb: 4 }}>
            {/* Welcome Section */}
            <Card>
              <CardContent>
                <Typography variant="h5" gutterBottom>
                  Welcome to the Neural Network Training Platform
                </Typography>
                <Typography variant="body1">
                  Upload your data, train models, and visualize predictions for your order volume forecasting.
                </Typography>
              </CardContent>
              <CardActions>
                <Button 
                  variant="contained" 
                  color="primary" 
                  startIcon={<PlayArrowIcon />}
                  onClick={handleNewPrediction}
                >
                  Start New Prediction
                </Button>
              </CardActions>
            </Card>
          </Box>
          
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 4 }}>
            {/* Models Section */}
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Available Models
                </Typography>
                
                {isLoadingModels ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                    <CircularProgress />
                  </Box>
                ) : modelsError ? (
                  <Typography color="error" variant="body2">
                    {modelsError}
                  </Typography>
                ) : (
                  <List>
                    {models.map((model: { id: string; name: string; description: string }) => (
                      <ListItem key={model.id} divider>
                        <ListItemText
                          primary={model.name}
                          secondary={model.description}
                        />
                        <ListItemSecondaryAction>
                          <IconButton 
                            edge="end" 
                            aria-label="view"
                            onClick={() => handleViewModel(model.id)}
                          >
                            <VisibilityIcon />
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                    
                    {models.length === 0 && (
                      <ListItem>
                        <ListItemText
                          primary="No models available"
                          secondary="Train a model to get started"
                        />
                      </ListItem>
                    )}
                  </List>
                )}
              </CardContent>
            </Card>
            
            {/* Recent Predictions Section */}
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Predictions
                </Typography>
                
                <List>
                  {recentPredictions.map((prediction) => (
                    <ListItem key={prediction.id} divider>
                      <ListItemText
                        primary={prediction.name}
                        secondary={`Created: ${formatDateTime(prediction.timestamp)}`}
                      />
                      <ListItemSecondaryAction>
                        <IconButton 
                          edge="end" 
                          aria-label="view results"
                          onClick={() => handleViewResults(prediction.modelId)}
                        >
                          <BarChartIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                  
                  {recentPredictions.length === 0 && (
                    <ListItem>
                      <ListItemText
                        primary="No recent predictions"
                        secondary="Generate a prediction to get started"
                      />
                    </ListItem>
                  )}
                </List>
              </CardContent>
            </Card>
          </Box>
        </Box>
      </Container>
    </MainLayout>
  );
};

export default DashboardPage; 