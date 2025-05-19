import React, { useState } from "react";
import { FileUpload } from "@/components/data/FileUpload";
import { DataPreview } from "@/components/data/DataPreview";
import { PageContainer, PageHeader, PageContent } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useApp } from "@/context/AppContext";
import { fileApi, FileMetadata, DataPreview as DataPreviewType } from "@/services/api";
import { format } from "date-fns";
import { toast } from "sonner";
import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

const DataUpload = () => {
  const { files, addFile } = useApp();
  const [previewData, setPreviewData] = useState<DataPreviewType | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isLoadingPreview, setIsLoadingPreview] = useState<boolean>(false);
  const [uploadedFileId, setUploadedFileId] = useState<string>("");
  
  const handleFileUpload = async (file: File) => {
    setSelectedFile(file);
    setIsLoadingPreview(true);
    
    try {
      // Upload the file using the real API
      const uploadResponse = await fileApi.uploadCSV(file, (progress) => {
        console.log(`Upload progress: ${progress}%`);
      });
      
      // Store the file ID for later use
      setUploadedFileId(uploadResponse.file_id);
      
      // Add file to context with real metadata
      const newFile = {
        file_id: uploadResponse.file_id,
        filename: uploadResponse.filename,
        content_type: uploadResponse.content_type,
        timestamp: uploadResponse.timestamp || format(new Date(), "yyyy-MM-dd'T'HH:mm:ss")
      };
      
      addFile(newFile);
      
      // Get the preview data for the uploaded file
      const previewResponse = await fileApi.getPreview(uploadResponse.file_id);
      setPreviewData(previewResponse);
      
      toast.success("File uploaded successfully", {
        description: "Your data is ready for preview."
      });
      
    } catch (error: any) {
      console.error("Error uploading file:", error);
      toast.error("Upload failed", {
        description: error.message || "There was an error uploading your file."
      });
    } finally {
      setIsLoadingPreview(false);
    }
    
    return Promise.resolve();
  };
  
  const handleNextSteps = () => {
    toast.success("Data validated successfully", {
      description: "Your data is ready for model training."
    });
  };

  return (
    <PageContainer>
      <PageHeader>
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Data Upload & Preview</h1>
            <p className="text-muted-foreground">
              Upload CSV files containing your logistics data
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button asChild>
              <Link to="/models/train">
                Train Model
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </PageHeader>

      <PageContent>
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Upload Data</CardTitle>
            </CardHeader>
            <CardContent>
              <FileUpload
                accept=".csv"
                maxSize={20 * 1024 * 1024} // 20MB
                onUpload={handleFileUpload}
              />
            </CardContent>
          </Card>
          
          {isLoadingPreview && (
            <DataPreview
              columns={[]}
              rows={[]}
              totalRows={0}
              fileName={selectedFile?.name || "Loading..."}
              loading={true}
            />
          )}
          
          {previewData && !isLoadingPreview && (
            <>
              <DataPreview
                columns={previewData.column_info ? Object.keys(previewData.column_info).map(name => ({ 
                  name, 
                  type: previewData.column_info[name].type 
                })) : []}
                rows={previewData.sample_rows || []}
                totalRows={previewData.total_rows}
                fileName={selectedFile?.name || previewData.file_id}
              />
              
              <div className="flex justify-end gap-2">
                <Button variant="outline">Cancel</Button>
                <Button 
                  onClick={handleNextSteps}
                  disabled={!uploadedFileId}
                >
                  Proceed to Training
                </Button>
              </div>
            </>
          )}
          
          {!previewData && !isLoadingPreview && files.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Available Data Files</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="rounded-md border">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="px-4 py-3 text-left text-sm font-medium">Filename</th>
                        <th className="px-4 py-3 text-left text-sm font-medium">Type</th>
                        <th className="px-4 py-3 text-left text-sm font-medium">Uploaded</th>
                        <th className="px-4 py-3 text-left text-sm font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {files.map((file) => (
                        <tr key={file.file_id} className="border-b">
                          <td className="px-4 py-3 text-sm">{file.filename}</td>
                          <td className="px-4 py-3 text-sm">{file.content_type}</td>
                          <td className="px-4 py-3 text-sm">{file.timestamp ? new Date(file.timestamp).toLocaleDateString() : 'Unknown'}</td>
                          <td className="px-4 py-3 text-sm">
                            <Button 
                              variant="outline" 
                              size="sm" 
                              onClick={async () => {
                                setIsLoadingPreview(true);
                                try {
                                  const preview = await fileApi.getPreview(file.file_id);
                                  setPreviewData(preview);
                                  setUploadedFileId(file.file_id);
                                } catch (error) {
                                  console.error("Error fetching preview:", error);
                                  toast.error("Error loading preview");
                                } finally {
                                  setIsLoadingPreview(false);
                                }
                              }}
                            >
                              Preview
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </PageContent>
    </PageContainer>
  );
};

export default DataUpload;
