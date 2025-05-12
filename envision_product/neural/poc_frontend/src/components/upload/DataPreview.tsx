import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
} from '@mui/material';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';

interface DataPreviewProps {
  onContinue: () => void;
  onBack: () => void;
}

const DataPreview: React.FC<DataPreviewProps> = ({ onContinue, onBack }) => {
  const { preview } = useSelector((state: RootState) => state.upload);

  if (!preview) {
    return (
      <Typography variant="body1" align="center">
        No data available for preview
      </Typography>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h6" gutterBottom>
        File Preview: {preview.fileName}
      </Typography>
      <Typography variant="body2" color="textSecondary" gutterBottom>
        Total rows: {preview.totalRows}
      </Typography>

      <TableContainer component={Paper} sx={{ my: 3, maxHeight: 400 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              {preview.columns.map((column, index) => (
                <TableCell key={index} sx={{ fontWeight: 'bold' }}>
                  {column}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {preview.sampleRows.map((row, rowIndex) => (
              <TableRow key={rowIndex} hover>
                {row.map((cell, cellIndex) => (
                  <TableCell key={`${rowIndex}-${cellIndex}`}>{cell}</TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
        <Button variant="outlined" onClick={onBack}>
          Back
        </Button>
        <Button variant="contained" color="primary" onClick={onContinue}>
          Continue to Model Selection
        </Button>
      </Box>
    </Box>
  );
};

export default DataPreview; 