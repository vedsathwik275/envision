
import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { FileUp, X, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Link } from 'react-router-dom';
import { useModelStore } from '@/store/modelStore';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

const UploadData = () => {
  const { 
    startFileUpload, 
    updateUploadProgress, 
    completeFileUpload, 
    isUploading, 
    uploadProgress,
    uploadedFile
  } = useModelStore();
  
  const [fileError, setFileError] = useState<string | null>(null);
  
  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFileError(null);
    
    if (acceptedFiles.length === 0) {
      return;
    }
    
    const file = acceptedFiles[0];
    
    // File validation
    if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
      setFileError('Only CSV files are accepted');
      return;
    }
    
    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      setFileError('File size must be less than 10MB');
      return;
    }
    
    // Start upload
    startFileUpload(file);
    
    // Simulate upload progress
    const timer = setInterval(() => {
      const newProgress = uploadProgress + Math.floor(Math.random() * 10);
      // Fix: Pass a direct number instead of a callback function
      if (newProgress >= 99) {
        clearInterval(timer);
        updateUploadProgress(99);
        setTimeout(() => {
          completeFileUpload();
          toast.success('File uploaded successfully');
        }, 500);
      } else {
        updateUploadProgress(newProgress);
      }
    }, 500);
  }, [startFileUpload, updateUploadProgress, completeFileUpload, uploadProgress]);
  
  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragAccept,
    isDragReject
  } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    disabled: isUploading || uploadedFile !== null,
    maxFiles: 1
  });
  
  const handleReset = () => {
    setFileError(null);
    completeFileUpload();
    startFileUpload(null as unknown as File);
  };
  
  return (
    <div className="max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Upload Training Data</h2>
      
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-2">Instructions</h3>
        <ul className="list-disc pl-5 space-y-2 text-muted-foreground">
          <li>Upload a CSV file containing your dataset (max 10MB)</li>
          <li>Ensure your file has the correct format with headers for all features</li>
          <li>The first column should be your target variable for prediction</li>
          <li>Missing values should be clearly marked (e.g., with NA, NULL, or empty cells)</li>
        </ul>
      </div>
      
      <div 
        {...getRootProps()} 
        className={cn(
          'dropzone',
          isDragActive ? 'dropzone-hover' : 'dropzone-idle',
          isDragAccept && 'dropzone-accept',
          isDragReject && 'dropzone-reject',
          fileError && 'border-neural-error',
          uploadedFile && 'bg-neural-light border-neural-primary'
        )}
      >
        <input {...getInputProps()} />
        
        {uploadedFile ? (
          <div className="text-center">
            <CheckCircle className="h-16 w-16 text-neural-accent mx-auto mb-4" />
            <h4 className="text-xl font-medium mb-2">File Uploaded Successfully</h4>
            <p className="text-muted-foreground mb-4">
              {uploadedFile.name} ({(uploadedFile.size / 1024).toFixed(2)} KB)
            </p>
            <div className="flex justify-center gap-4">
              <Button variant="outline" onClick={handleReset}>
                <X className="h-4 w-4 mr-2" />
                Remove File
              </Button>
              <Button asChild>
                <Link to="/model-training">
                  Continue to Model Training
                </Link>
              </Button>
            </div>
          </div>
        ) : isUploading ? (
          <div className="text-center">
            <Loader className="h-12 w-12 text-neural-primary mx-auto mb-4 animate-spin" />
            <h4 className="text-xl font-medium mb-6">Uploading File...</h4>
            <Progress value={uploadProgress} className="w-full max-w-md mx-auto mb-4" />
            <p className="text-muted-foreground">{uploadProgress}% Complete</p>
          </div>
        ) : fileError ? (
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-neural-error mx-auto mb-4" />
            <h4 className="text-xl font-medium text-neural-error mb-2">Upload Error</h4>
            <p className="mb-4">{fileError}</p>
            <Button onClick={() => setFileError(null)}>Try Again</Button>
          </div>
        ) : (
          <div className="text-center">
            <FileUp className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h4 className="text-xl font-medium mb-2">
              {isDragActive ? 'Drop the file here...' : 'Drag & Drop File Here'}
            </h4>
            <p className="text-muted-foreground mb-4">or click to browse files</p>
            <p className="text-xs text-muted-foreground">
              Accepted format: CSV (up to 10MB)
            </p>
          </div>
        )}
      </div>
      
      <div className="mt-8">
        <h3 className="text-lg font-semibold mb-2">Sample Data Format</h3>
        <div className="overflow-x-auto border rounded-md">
          <table className="min-w-full divide-y divide-border">
            <thead>
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider bg-muted">order_volume</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider bg-muted">date</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider bg-muted">day_of_week</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider bg-muted">season</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider bg-muted">promo_active</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-border text-sm">
              <tr>
                <td className="px-4 py-2">145</td>
                <td className="px-4 py-2">2023-01-15</td>
                <td className="px-4 py-2">Sunday</td>
                <td className="px-4 py-2">Winter</td>
                <td className="px-4 py-2">Yes</td>
              </tr>
              <tr>
                <td className="px-4 py-2">132</td>
                <td className="px-4 py-2">2023-01-16</td>
                <td className="px-4 py-2">Monday</td>
                <td className="px-4 py-2">Winter</td>
                <td className="px-4 py-2">No</td>
              </tr>
              <tr>
                <td className="px-4 py-2">168</td>
                <td className="px-4 py-2">2023-01-17</td>
                <td className="px-4 py-2">Tuesday</td>
                <td className="px-4 py-2">Winter</td>
                <td className="px-4 py-2">Yes</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default UploadData;
