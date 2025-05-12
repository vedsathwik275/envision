import React, { useCallback } from 'react';
import { Box, Typography, Paper, Button, LinearProgress } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { useFileUpload } from '../../hooks/useFileUpload';
import { formatFileSize } from '../../utils/formatters';
import { styled } from '@mui/material/styles';

const UploadBox = styled(Paper)(({ theme }) => ({
  border: `2px dashed ${theme.palette.primary.main}`,
  padding: theme.spacing(4),
  textAlign: 'center',
  cursor: 'pointer',
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
  },
}));

const FileUploader: React.FC = () => {
  const {
    file,
    isUploading,
    uploadProgress,
    error,
    isDragActive,
    uploadFile,
    getRootProps,
    getInputProps,
  } = useFileUpload();

  const handleUpload = useCallback(() => {
    uploadFile();
  }, [uploadFile]);

  return (
    <Box sx={{ width: '100%', maxWidth: 600, mx: 'auto' }}>
      {error && (
        <Typography color="error" variant="body2" align="center" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}
      
      <UploadBox 
        elevation={3}
        {...getRootProps()}
        sx={{ 
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
        }}
      >
        <input {...getInputProps()} />
        <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive ? 'Drop the file here...' : 'Drag & Drop CSV File Here'}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          or click to browse files
        </Typography>
        
        {file && (
          <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="body1">
              {file.name} ({formatFileSize(file.size)})
            </Typography>
          </Box>
        )}
      </UploadBox>
      
      {isUploading && (
        <Box sx={{ mt: 2 }}>
          <LinearProgress variant="determinate" value={uploadProgress} />
          <Typography variant="body2" align="center" sx={{ mt: 1 }}>
            Uploading... {uploadProgress}%
          </Typography>
        </Box>
      )}
      
      {file && !isUploading && (
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleUpload}
            disabled={isUploading}
          >
            Upload File
          </Button>
        </Box>
      )}
      
      <Box sx={{ mt: 2 }}>
        <Typography variant="body2" color="textSecondary" align="center">
          Supported formats: CSV
        </Typography>
        <Typography variant="body2" color="textSecondary" align="center">
          Max file size: 10MB
        </Typography>
      </Box>
    </Box>
  );
};

export default FileUploader; 