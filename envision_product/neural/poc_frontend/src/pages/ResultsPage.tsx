import React, { useEffect } from 'react';
import { Container, Typography, Box, Button, CircularProgress, ButtonGroup } from '@mui/material';
import ResultsPanel from '../components/results/ResultsPanel';
import { useParams, useNavigate } from 'react-router-dom';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import DownloadIcon from '@mui/icons-material/Download';
import { usePrediction } from '../hooks/usePrediction';
import MainLayout from '../components/layout/MainLayout';
import { downloadBlob } from '../services/prediction.service';

const ResultsPage: React.FC = () => {
  const { modelId } = useParams<{ modelId: string }>();
  const navigate = useNavigate();
  const { 
    predictionResults, 
    isFetching, 
    isExporting,
    error, 
    exportedBlob,
    fetchResults,
    exportResults
  } = usePrediction();

  useEffect(() => {
    if (modelId) {
      fetchResults(modelId);
    }
  }, [fetchResults, modelId]);

  // Download file if blob is available
  useEffect(() => {
    if (exportedBlob && modelId) {
      downloadBlob(exportedBlob, `prediction-results-${modelId}.csv`);
    }
  }, [exportedBlob, modelId]);

  const handleBack = () => {
    navigate('/dashboard');
  };

  const handleExport = (format: 'csv' | 'excel' = 'csv') => {
    if (modelId) {
      exportResults(modelId, format);
    }
  };

  return (
    <MainLayout title="Prediction Results">
      <Container maxWidth="lg">
        <Box sx={{ my: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Button 
                variant="outlined" 
                startIcon={<ArrowBackIcon />} 
                onClick={handleBack}
                sx={{ mr: 2 }}
              >
                Back
              </Button>
              <Typography variant="h4" component="h1">
                Prediction Results
              </Typography>
            </Box>
            
            {predictionResults && (
              <ButtonGroup variant="outlined">
                <Button 
                  startIcon={<DownloadIcon />}
                  onClick={() => handleExport('csv')}
                  disabled={isExporting}
                >
                  {isExporting ? 'Exporting...' : 'Export CSV'}
                </Button>
                <Button 
                  startIcon={<DownloadIcon />}
                  onClick={() => handleExport('excel')}
                  disabled={isExporting}
                >
                  Export Excel
                </Button>
              </ButtonGroup>
            )}
          </Box>
          
          {modelId && (
            <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 2 }}>
              Model ID: {modelId}
            </Typography>
          )}
          
          {predictionResults && predictionResults.trainingMetrics && (
            <Box sx={{ mb: 3, p: 2, bgcolor: 'background.paper', borderRadius: 1, border: 1, borderColor: 'divider' }}>
              <Typography variant="h6" gutterBottom>
                Model Performance Metrics
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Mean Absolute Error (MAE)
                  </Typography>
                  <Typography variant="h6">
                    {predictionResults.trainingMetrics.mae.toFixed(2)}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Root Mean Squared Error (RMSE)
                  </Typography>
                  <Typography variant="h6">
                    {predictionResults.trainingMetrics.rmse.toFixed(2)}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    R² Score
                  </Typography>
                  <Typography variant="h6">
                    {predictionResults.trainingMetrics.r2.toFixed(2)}
                  </Typography>
                </Box>
              </Box>
            </Box>
          )}
          
          <ResultsPanel 
            results={predictionResults ? predictionResults.results : []} 
            isLoading={isFetching}
            error={error}
          />
        </Box>
      </Container>
    </MainLayout>
  );
};

export default ResultsPage; 