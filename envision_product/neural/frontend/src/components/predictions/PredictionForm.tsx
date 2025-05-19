
import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DatePicker } from "../ui/date-picker";
import { FileUpload } from "../data/FileUpload";
import { toast } from "sonner";
import { Loader } from "lucide-react";

interface Model {
  id: string;
  name: string;
  type: "order-volume" | "tender-performance" | "carrier-performance";
  accuracy: number;
}

interface PredictionFormProps {
  modelType: "order-volume" | "tender-performance" | "carrier-performance";
  models: Model[];
  selectedModelId?: string;
  onSubmit: (data: any) => Promise<void>;
  loading?: boolean;
}

export function PredictionForm({
  modelType,
  models,
  selectedModelId,
  onSubmit,
  loading = false
}: PredictionFormProps) {
  const [predictionName, setPredictionName] = useState<string>("");
  const [modelId, setModelId] = useState<string>(selectedModelId || "");
  const [inputMethod, setInputMethod] = useState<"file" | "manual">("file");
  const [startDate, setStartDate] = useState<Date | undefined>(new Date());
  const [endDate, setEndDate] = useState<Date | undefined>(
    new Date(new Date().setDate(new Date().getDate() + 30)) // Default to 30 days from now
  );
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  
  const filteredModels = models.filter(model => model.type === modelType);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!predictionName.trim()) {
      toast.error("Please enter a prediction name");
      return;
    }
    
    if (!modelId) {
      toast.error("Please select a model");
      return;
    }
    
    if (inputMethod === "file" && !uploadedFile) {
      toast.error("Please upload input data file");
      return;
    }
    
    if (inputMethod === "manual" && (!startDate || !endDate)) {
      toast.error("Please specify date range");
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      await onSubmit({
        predictionName,
        modelId,
        inputMethod,
        startDate,
        endDate,
        file: uploadedFile
      });
      
      toast.success("Prediction generated", {
        description: `Your ${getModelTypeLabel(modelType)} prediction "${predictionName}" has been created.`
      });
      
      // Reset form
      setPredictionName("");
    } catch (error) {
      toast.error("Prediction generation failed", {
        description: error instanceof Error ? error.message : "An unknown error occurred."
      });
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const handleFileUpload = async (file: File) => {
    setUploadedFile(file);
  };
  
  const getModelTypeLabel = (type: string) => {
    switch (type) {
      case "order-volume":
        return "Order Volume";
      case "tender-performance":
        return "Tender Performance";
      case "carrier-performance":
        return "Carrier Performance";
      default:
        return type;
    }
  };
  
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Generate {getModelTypeLabel(modelType)} Prediction</CardTitle>
          <CardDescription>Loading prediction options...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center p-8">
            <Loader className="h-8 w-8 animate-spin text-primary" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Generate {getModelTypeLabel(modelType)} Prediction</CardTitle>
        <CardDescription>
          Generate predictions using your trained models
        </CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="prediction-name">Prediction Name</Label>
              <Input
                id="prediction-name"
                placeholder={`${getModelTypeLabel(modelType)} Prediction - ${new Date().toLocaleDateString()}`}
                value={predictionName}
                onChange={(e) => setPredictionName(e.target.value)}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="model-select">Select Model</Label>
              <Select value={modelId} onValueChange={setModelId}>
                <SelectTrigger id="model-select">
                  <SelectValue placeholder="Choose a model" />
                </SelectTrigger>
                <SelectContent>
                  {filteredModels.length === 0 ? (
                    <SelectItem value="none" disabled>No models available</SelectItem>
                  ) : (
                    filteredModels.map((model) => (
                      <SelectItem key={model.id} value={model.id}>
                        {model.name} ({model.accuracy}% accuracy)
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
              {filteredModels.length === 0 && (
                <p className="text-xs text-neural-error mt-1">
                  No models available. Please train a model first.
                </p>
              )}
            </div>
            
            <div className="space-y-2">
              <Label>Input Method</Label>
              <Tabs defaultValue="file" onValueChange={(value) => setInputMethod(value as "file" | "manual")}>
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="file">Upload File</TabsTrigger>
                  <TabsTrigger value="manual">Date Range</TabsTrigger>
                </TabsList>
                
                <TabsContent value="file" className="mt-4">
                  <FileUpload
                    accept=".csv"
                    maxSize={5 * 1024 * 1024} // 5MB
                    onUpload={handleFileUpload}
                  />
                </TabsContent>
                
                <TabsContent value="manual" className="mt-4 space-y-4">
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div className="space-y-2">
                      <Label>Start Date</Label>
                      <DatePicker date={startDate} setDate={setStartDate} />
                    </div>
                    <div className="space-y-2">
                      <Label>End Date</Label>
                      <DatePicker date={endDate} setDate={setEndDate} />
                    </div>
                  </div>
                  
                  <div className="p-4 border rounded-md bg-muted/50">
                    <p className="text-sm">
                      {modelType === "order-volume" && "Predictions will be generated for shipment volumes in this date range."}
                      {modelType === "tender-performance" && "Predictions will analyze tender acceptance rates during this period."}
                      {modelType === "carrier-performance" && "On-time performance will be predicted for carriers in this date range."}
                    </p>
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          </div>
        </CardContent>
        <CardFooter className="flex justify-between">
          <Button variant="outline" type="button">Cancel</Button>
          <Button
            type="submit"
            disabled={isSubmitting || filteredModels.length === 0 || (inputMethod === "file" && !uploadedFile)}
          >
            {isSubmitting ? (
              <>
                <Loader className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              "Generate Prediction"
            )}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
