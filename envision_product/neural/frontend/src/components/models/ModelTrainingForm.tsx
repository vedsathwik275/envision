
import React, { useState } from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";
import { Loader } from "lucide-react";

interface ModelTrainingFormProps {
  onSubmit: (data: any) => Promise<void>;
  files: { id: string; name: string }[];
  loading?: boolean;
}

export function ModelTrainingForm({ onSubmit, files, loading = false }: ModelTrainingFormProps) {
  const [modelType, setModelType] = useState<string>("order-volume");
  const [modelName, setModelName] = useState<string>("");
  const [selectedFileId, setSelectedFileId] = useState<string>("");
  const [splitRatio, setSplitRatio] = useState<number>(80);
  const [hyperparameters, setHyperparameters] = useState({
    epochs: 100,
    batchSize: 32,
    learningRate: 0.001,
    useFeatureScaling: true,
    useEarlyStopping: true
  });
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!modelName.trim()) {
      toast.error("Please enter a model name");
      return;
    }
    
    if (!selectedFileId) {
      toast.error("Please select a training file");
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      await onSubmit({
        modelType,
        modelName,
        fileId: selectedFileId,
        trainTestSplit: splitRatio / 100,
        hyperparameters
      });
      
      toast.success("Model training started", {
        description: `Your ${getModelTypeLabel(modelType)} model "${modelName}" is now training.`
      });
      
      // Reset form
      setModelName("");
      setSelectedFileId("");
    } catch (error) {
      toast.error("Training request failed", {
        description: error instanceof Error ? error.message : "An unknown error occurred."
      });
    } finally {
      setIsSubmitting(false);
    }
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
          <CardTitle>Train New Model</CardTitle>
          <CardDescription>Loading training options...</CardDescription>
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
        <CardTitle>Train New Model</CardTitle>
        <CardDescription>
          Configure and train a new predictive model
        </CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-6">
          <Tabs defaultValue="order-volume" onValueChange={(value) => setModelType(value)}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="order-volume">Order Volume</TabsTrigger>
              <TabsTrigger value="tender-performance">Tender Performance</TabsTrigger>
              <TabsTrigger value="carrier-performance">Carrier Performance</TabsTrigger>
            </TabsList>
            
            {/* Basic settings are shared between tabs */}
            <div className="space-y-4 mt-6">
              <div className="space-y-2">
                <Label htmlFor="model-name">Model Name</Label>
                <Input
                  id="model-name"
                  placeholder={`My ${getModelTypeLabel(modelType)} Model`}
                  value={modelName}
                  onChange={(e) => setModelName(e.target.value)}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="training-file">Training Data</Label>
                <Select value={selectedFileId} onValueChange={setSelectedFileId}>
                  <SelectTrigger id="training-file">
                    <SelectValue placeholder="Select a file" />
                  </SelectTrigger>
                  <SelectContent>
                    {files.map((file) => (
                      <SelectItem key={file.id} value={file.id}>
                        {file.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground mt-1">
                  {files.length === 0 
                    ? "No data files available. Please upload data first." 
                    : "Select the CSV file containing your training data."}
                </p>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="split-ratio">Train/Test Split</Label>
                  <span className="text-sm">{splitRatio}% / {100 - splitRatio}%</span>
                </div>
                <Slider
                  id="split-ratio"
                  min={50}
                  max={90}
                  step={5}
                  value={[splitRatio]}
                  onValueChange={(values) => setSplitRatio(values[0])}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Percentage of data used for training vs. testing
                </p>
              </div>
              
              <div className="border rounded-md p-4 space-y-4">
                <h3 className="text-sm font-medium">Advanced Settings</h3>
                
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="epochs">Epochs</Label>
                    <Input
                      id="epochs"
                      type="number"
                      min={10}
                      max={1000}
                      value={hyperparameters.epochs}
                      onChange={(e) => setHyperparameters({
                        ...hyperparameters,
                        epochs: parseInt(e.target.value)
                      })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="batch-size">Batch Size</Label>
                    <Input
                      id="batch-size"
                      type="number"
                      min={8}
                      max={256}
                      step={8}
                      value={hyperparameters.batchSize}
                      onChange={(e) => setHyperparameters({
                        ...hyperparameters,
                        batchSize: parseInt(e.target.value)
                      })}
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="learning-rate">Learning Rate</Label>
                  <div className="flex items-center justify-between">
                    <span className="text-xs">0.0001</span>
                    <span className="text-xs">0.01</span>
                  </div>
                  <Slider
                    id="learning-rate"
                    min={0.0001}
                    max={0.01}
                    step={0.0001}
                    value={[hyperparameters.learningRate]}
                    onValueChange={(values) => setHyperparameters({
                      ...hyperparameters,
                      learningRate: values[0]
                    })}
                  />
                  <div className="flex justify-center">
                    <span className="text-sm">{hyperparameters.learningRate}</span>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="feature-scaling"
                      checked={hyperparameters.useFeatureScaling}
                      onCheckedChange={(checked) => setHyperparameters({
                        ...hyperparameters,
                        useFeatureScaling: checked
                      })}
                    />
                    <Label htmlFor="feature-scaling">Use Feature Scaling</Label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="early-stopping"
                      checked={hyperparameters.useEarlyStopping}
                      onCheckedChange={(checked) => setHyperparameters({
                        ...hyperparameters,
                        useEarlyStopping: checked
                      })}
                    />
                    <Label htmlFor="early-stopping">Use Early Stopping</Label>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Model-specific tabs */}
            <TabsContent value="order-volume">
              <div className="space-y-4 mt-4">
                <p className="text-sm">
                  Order Volume models predict the expected number of shipments between 
                  specific origin-destination pairs based on historical data patterns.
                </p>
              </div>
            </TabsContent>
            
            <TabsContent value="tender-performance">
              <div className="space-y-4 mt-4">
                <p className="text-sm">
                  Tender Performance models analyze and predict tender acceptance rates 
                  for specific lanes and carriers.
                </p>
              </div>
            </TabsContent>
            
            <TabsContent value="carrier-performance">
              <div className="space-y-4 mt-4">
                <p className="text-sm">
                  Carrier Performance models predict on-time delivery rates and service 
                  metrics for carriers across different lanes.
                </p>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
        <CardFooter className="flex justify-between">
          <Button variant="outline">Cancel</Button>
          <Button type="submit" disabled={isSubmitting || files.length === 0}>
            {isSubmitting ? (
              <>
                <Loader className="mr-2 h-4 w-4 animate-spin" />
                Training...
              </>
            ) : (
              "Start Training"
            )}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
