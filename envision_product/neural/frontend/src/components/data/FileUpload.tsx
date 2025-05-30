import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Loader, Upload, File, CheckCircle, AlertCircle } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";

interface FileUploadProps {
  accept?: string;
  maxSize?: number; // in bytes
  onUpload: (file: File) => Promise<void>;
  className?: string;
}

export function FileUpload({
  accept = ".csv",
  maxSize = 10 * 1024 * 1024, // 10MB default
  onUpload,
  className
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  
  const resetState = () => {
    setFile(null);
    setProgress(0);
    setUploadStatus("idle");
  };
  
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };
  
  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };
  
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    const droppedFile = e.dataTransfer.files?.[0];
    handleFile(droppedFile);
  };
  
  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    handleFile(selectedFile);
  };
  
  const handleFile = (selectedFile?: File) => {
    if (!selectedFile) return;
    
    // Check file type
    const fileType = selectedFile.type;
    if (!fileType.includes("csv") && !accept.includes(fileType)) {
      toast.error("Invalid file type", {
        description: `Please upload a ${accept} file.`
      });
      return;
    }
    
    // Check file size
    if (selectedFile.size > maxSize) {
      toast.error("File too large", {
        description: `File size should be less than ${Math.round(maxSize / (1024 * 1024))}MB.`
      });
      return;
    }
    
    setFile(selectedFile);
  };
  
  const handleUpload = async () => {
    if (!file) return;
    
    setIsUploading(true);
    setUploadStatus("uploading");
    
    // Simulate progress
    const progressInterval = setInterval(() => {
      setProgress((prevProgress) => {
        const newProgress = prevProgress + 5;
        return newProgress >= 90 ? 90 : newProgress;
      });
    }, 100);
    
    try {
      await onUpload(file);
      clearInterval(progressInterval);
      setProgress(100);
      setUploadStatus("success");
      toast.success("File uploaded successfully", {
        description: `${file.name} has been uploaded.`
      });
    } catch (error) {
      clearInterval(progressInterval);
      setUploadStatus("error");
      toast.error("Upload failed", {
        description: error instanceof Error ? error.message : "An unknown error occurred."
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Card className={className}>
      <CardContent className="p-6">
        <div
          className={cn(
            "border-2 border-dashed rounded-lg p-8 text-center transition-all",
            isDragging ? "border-neural-primary bg-neural-primary/5" : "border-border",
            file && uploadStatus === "idle" && "border-neural-success bg-neural-success/5",
            uploadStatus === "success" && "border-neural-success bg-neural-success/5",
            uploadStatus === "error" && "border-neural-error bg-neural-error/5"
          )}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {uploadStatus === "idle" && !file && (
            <div className="space-y-4">
              <div className="flex justify-center">
                <div className="rounded-full bg-muted p-4">
                  <Upload className="h-8 w-8 text-muted-foreground" />
                </div>
              </div>
              <div>
                <h3 className="text-lg font-medium">Upload a CSV file</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Drag and drop or click to browse
                </p>
              </div>
              <input
                type="file"
                id="file-upload"
                className="hidden"
                accept={accept}
                onChange={handleFileInput}
              />
              <Button
                variant="outline"
                onClick={() => document.getElementById("file-upload")?.click()}
              >
                Browse Files
              </Button>
              <p className="text-xs text-muted-foreground">
                Max file size: {Math.round(maxSize / (1024 * 1024))}MB
              </p>
            </div>
          )}
          
          {file && uploadStatus === "idle" && (
            <div className="space-y-4">
              <div className="flex justify-center">
                <div className="rounded-full bg-neural-success/20 p-4">
                  <CheckCircle className="h-8 w-8 text-neural-success" />
                </div>
              </div>
              <div>
                <h3 className="text-lg font-medium text-neural-success">{file.name}</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {(file.size / 1024).toFixed(1)} KB • {file.type || "CSV"}
                </p>
                <p className="text-sm text-neural-success mt-1 font-medium">
                  File selected successfully!
                </p>
              </div>
              <div className="flex space-x-2 justify-center">
                <Button onClick={handleUpload}>Upload File</Button>
                <Button variant="outline" onClick={resetState}>
                  Cancel
                </Button>
              </div>
            </div>
          )}
          
          {uploadStatus === "uploading" && (
            <div className="space-y-4">
              <div className="flex justify-center">
                <div className="rounded-full bg-muted p-4">
                  <Loader className="h-8 w-8 text-primary animate-spin" />
                </div>
              </div>
              <div>
                <h3 className="text-lg font-medium">Uploading...</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {file?.name}
                </p>
              </div>
              <div className="space-y-2">
                <Progress value={progress} className="h-2" />
                <p className="text-xs text-muted-foreground">
                  {progress}% complete
                </p>
              </div>
            </div>
          )}
          
          {uploadStatus === "success" && (
            <div className="space-y-4">
              <div className="flex justify-center">
                <div className="rounded-full bg-neural-success/20 p-4">
                  <CheckCircle className="h-8 w-8 text-neural-success" />
                </div>
              </div>
              <div>
                <h3 className="text-lg font-medium text-neural-success">Upload Complete</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {file?.name} has been successfully uploaded
                </p>
              </div>
              <Button onClick={resetState}>Upload Another File</Button>
            </div>
          )}
          
          {uploadStatus === "error" && (
            <div className="space-y-4">
              <div className="flex justify-center">
                <div className="rounded-full bg-neural-error/20 p-4">
                  <AlertCircle className="h-8 w-8 text-neural-error" />
                </div>
              </div>
              <div>
                <h3 className="text-lg font-medium text-neural-error">Upload Failed</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  There was a problem uploading {file?.name}
                </p>
              </div>
              <div className="flex space-x-2 justify-center">
                <Button onClick={handleUpload}>Try Again</Button>
                <Button variant="outline" onClick={resetState}>
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
