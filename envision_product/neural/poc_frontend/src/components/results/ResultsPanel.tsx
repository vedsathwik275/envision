import React, { useState } from 'react';
import { Box, Tabs, Tab, Paper, Typography, CircularProgress } from '@mui/material';
import PredictionChart from './PredictionChart';
import ResultsTable from './ResultsTable';
import { PredictionResult } from '../../types/data.types';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`results-tabpanel-${index}`}
      aria-labelledby={`results-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

interface ResultsPanelProps {
  results: PredictionResult[];
  isLoading?: boolean;
  error?: string | null;
}

const ResultsPanel: React.FC<ResultsPanelProps> = ({ 
  results, 
  isLoading = false,
  error = null 
}) => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  // Show loading indicator
  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '300px' }}>
        <CircularProgress />
      </Box>
    );
  }

  // Show error state
  if (error) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center', mt: 3 }}>
        <Typography variant="subtitle1" color="error">
          {error}
        </Typography>
      </Paper>
    );
  }

  // Show empty state
  if (!results || results.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center', mt: 3 }}>
        <Typography variant="subtitle1">
          No prediction results available. Please run a prediction to see results.
        </Typography>
      </Paper>
    );
  }

  return (
    <Box sx={{ width: '100%', mt: 4 }}>
      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab label="Chart View" id="results-tab-0" aria-controls="results-tabpanel-0" />
          <Tab label="Table View" id="results-tab-1" aria-controls="results-tabpanel-1" />
        </Tabs>
      </Paper>

      <TabPanel value={activeTab} index={0}>
        <PredictionChart results={results} title="Predicted Order Volume Over Time" />
      </TabPanel>
      
      <TabPanel value={activeTab} index={1}>
        <ResultsTable results={results} />
      </TabPanel>
    </Box>
  );
};

export default ResultsPanel; 