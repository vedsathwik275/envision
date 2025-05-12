import React, { useState, useEffect } from 'react';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Box,
  Typography,
  TextField,
  InputAdornment,
  Chip,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { PredictionResult } from '../../types/data.types';
import { formatYearMonth } from '../../utils/formatters';

interface ResultsTableProps {
  results: PredictionResult[];
}

const ResultsTable: React.FC<ResultsTableProps> = ({ results }) => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredResults, setFilteredResults] = useState<PredictionResult[]>([]);

  // Filter results based on search term
  useEffect(() => {
    if (!results) {
      setFilteredResults([]);
      return;
    }

    if (!searchTerm) {
      setFilteredResults(results);
      return;
    }

    const lowerCaseSearch = searchTerm.toLowerCase();
    const filtered = results.filter((result) => {
      return (
        result['SOURCE CITY'].toLowerCase().includes(lowerCaseSearch) ||
        result['DESTINATION CITY'].toLowerCase().includes(lowerCaseSearch) ||
        result['ORDER TYPE'].toLowerCase().includes(lowerCaseSearch) ||
        result['PREDICTION DATE'].toLowerCase().includes(lowerCaseSearch)
      );
    });

    setFilteredResults(filtered);
    setPage(0); // Reset to first page when filtering
  }, [results, searchTerm]);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  if (!results || results.length === 0) {
    return (
      <Typography variant="body1" align="center">
        No prediction results available
      </Typography>
    );
  }

  return (
    <Paper sx={{ width: '100%', mt: 3 }}>
      <Box sx={{ p: 2 }}>
        <TextField
          fullWidth
          placeholder="Search results..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          variant="outlined"
          size="small"
        />
      </Box>
      
      <TableContainer>
        <Table sx={{ minWidth: 650 }} size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Source City</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Destination City</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Order Type</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Date</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Predicted Volume</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredResults
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((result, index) => (
                <TableRow key={index} hover>
                  <TableCell>{result['SOURCE CITY']}</TableCell>
                  <TableCell>{result['DESTINATION CITY']}</TableCell>
                  <TableCell>
                    <Chip 
                      label={result['ORDER TYPE']} 
                      size="small" 
                      color={
                        result['ORDER TYPE'] === 'Prepaid' ? 'primary' :
                        result['ORDER TYPE'] === 'Collect' ? 'secondary' : 'default'
                      }
                    />
                  </TableCell>
                  <TableCell>{formatYearMonth(result['PREDICTION DATE'])}</TableCell>
                  <TableCell>{result['PREDICTED ORDER VOLUME']}</TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
      </TableContainer>
      
      <TablePagination
        rowsPerPageOptions={[10, 25, 50, 100]}
        component="div"
        count={filteredResults.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </Paper>
  );
};

export default ResultsTable; 