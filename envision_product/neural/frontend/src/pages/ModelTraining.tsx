import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { useModelStore } from '@/store/modelStore';
import { toast } from 'sonner';
import { ChartLine, Loader2 } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { v4 as uuid } from 'uuid';

const modelParameters = {
  'order-volume': [
    { id: 'epochs', name: 'Epochs', default: 100, min: 10, max: 500 },
    { id: 'learning-rate', name: 'Learning Rate', default: 0.001, min: 0.0001, max: 0.1 },
    { id: 'batch-size', name: 'Batch Size', default: 32, min: 8, max: 128 }
  ]
};

const ModelTraining = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { 
    models, 
    selectedModelId, 
    selectModel, 
    updateTrainingProgress, 
    trainingProgress,
    uploadedFile,
    addPredictionResult
  } = useModelStore();
  
  const [modelId, setModelId] = useState(selectedModelId || searchParams.get('id') || models[0]?.id);
  const [parameters, setParameters] = useState<Record<string, number>>({});
  const [validationSplit, setValidationSplit] = useState(0.2);
  
  const selectedModel = models.find(m => m.id === modelId);

  // Set initial parameters
  useEffect(() => {
    if (selectedModel && selectedModel.type) {
      const defaultParams = modelParameters[selectedModel.type].reduce(
        (acc, param) => ({ ...acc, [param.id]: param.default }),
        {}
      );
      setParameters(defaultParams);
    }
  }, [selectedModel]);

  const handleModelSelect = (id: string) => {
    setModelId(id);
    selectModel(id);
  };

  const handleParameterChange = (id: string, value: number) => {
    setParameters(prev => ({ ...prev, [id]: value }));
  };
  
  const handleTrainModel = () => {
    if (!uploadedFile) {
      toast.error('Please upload data before training the model');
      navigate('/upload-data');
      return;
    }
    
    if (!selectedModel) {
      toast.error('Please select a model to train');
      return;
    }
    
    // Start training progress
    updateTrainingProgress({
      modelId,
      progress: 0,
      status: 'training',
      message: 'Initializing training...'
    });
    
    // Simulate training progress
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 5;
      
      if (progress >= 100) {
        clearInterval(interval);
        progress = 100;
        
        // Complete training
        updateTrainingProgress({
          modelId,
          progress: 100,
          status: 'completed',
          message: 'Training completed successfully!'
        });
        
        // Create a mock prediction result
        const today = new Date().toISOString();
        
        // Generate sample chart data
        const chartData = Array.from({ length: 12 }, (_, i) => {
          const actual = 100 + Math.round(Math.random() * 60);
          const deviation = Math.random() * 15;
          const predicted = Math.max(0, actual + (Math.random() > 0.5 ? deviation : -deviation));
          
          return {
            name: `Day ${i + 1}`,
            actual,
            predicted: Math.round(predicted)
          };
        });
        
        // Add new prediction result
        const newResult = {
          id: uuid(),
          modelId,
          modelName: selectedModel?.name || 'Unknown Model',
          dateCreated: today,
          metrics: {
            accuracy: 0.87 + Math.random() * 0.1,
            precision: 0.85 + Math.random() * 0.1,
            recall: 0.82 + Math.random() * 0.1,
            f1Score: 0.83 + Math.random() * 0.1
          },
          chartData
        };
        
        addPredictionResult(newResult);
        
        // Show success toast
        toast.success('Model trained successfully!', {
          action: {
            label: 'View Results',
            onClick: () => navigate(`/results?id=${newResult.id}`)
          }
        });
      } else {
        // Update progress
        updateTrainingProgress({
          modelId,
          progress,
          status: 'training',
          message: getProgressMessage(progress)
        });
      }
    }, 500);
    
    return () => clearInterval(interval);
  };
  
  const getProgressMessage = (progress: number) => {
    if (progress < 10) return 'Preparing data...';
    if (progress < 25) return 'Initializing model...';
    if (progress < 50) return 'Training in progress...';
    if (progress < 75) return 'Optimizing parameters...';
    if (progress < 90) return 'Validating results...';
    return 'Finalizing model...';
  };
  
  const isTraining = trainingProgress?.status === 'training';
  const isCompleted = trainingProgress?.status === 'completed';

  return (
    <div className="max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Model Training</h2>
      
      {!uploadedFile && (
        <Alert className="mb-6">
          <AlertTitle>No data uploaded</AlertTitle>
          <AlertDescription>
            Please upload your dataset first to proceed with model training.
            <Button variant="link" className="p-0 ml-1" onClick={() => navigate('/upload-data')}>
              Upload data
            </Button>
          </AlertDescription>
        </Alert>
      )}
      
      <div className="mb-8">
        <h3 className="text-lg font-semibold mb-4">Select Model</h3>
        <RadioGroup 
          value={modelId} 
          onValueChange={handleModelSelect}
          className="grid grid-cols-1 md:grid-cols-2 gap-4"
        >
          {models.map((model) => (
            <div key={model.id} className="flex items-center space-x-2">
              <RadioGroupItem value={model.id} id={`model-${model.id}`} disabled={isTraining} />
              <Label htmlFor={`model-${model.id}`} className="text-base cursor-pointer">
                {model.name}
              </Label>
            </div>
          ))}
        </RadioGroup>
      </div>
      
      {selectedModel && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>
              <div className="flex items-center">
                <ChartLine className="h-5 w-5 mr-2 text-neural-primary" />
                {selectedModel.name} Configuration
              </div>
            </CardTitle>
          </CardHeader>
          
          <CardContent className="space-y-6">
            <div>
              <h3 className="font-medium mb-3">Model Parameters</h3>
              <div className="space-y-4">
                {selectedModel.type && modelParameters[selectedModel.type].map((param) => (
                  <div key={param.id} className="space-y-1">
                    <div className="flex justify-between">
                      <Label htmlFor={param.id}>{param.name}</Label>
                      <span className="text-sm text-neural-primary font-medium">
                        {parameters[param.id]}
                      </span>
                    </div>
                    <input
                      id={param.id}
                      type="range"
                      min={param.min}
                      max={param.max}
                      step={param.id === 'learning-rate' ? 0.0001 : 1}
                      value={parameters[param.id] || param.default}
                      onChange={(e) => handleParameterChange(param.id, parseFloat(e.target.value))}
                      disabled={isTraining}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>{param.min}</span>
                      <span>{param.max}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div>
              <h3 className="font-medium mb-3">Validation Split</h3>
              <div className="space-y-1">
                <div className="flex justify-between">
                  <Label htmlFor="validation-split">Training/Validation Ratio</Label>
                  <span className="text-sm text-neural-primary font-medium">
                    {Math.round((1 - validationSplit) * 100)}% / {Math.round(validationSplit * 100)}%
                  </span>
                </div>
                <input
                  id="validation-split"
                  type="range"
                  min={0.1}
                  max={0.4}
                  step={0.05}
                  value={validationSplit}
                  onChange={(e) => setValidationSplit(parseFloat(e.target.value))}
                  disabled={isTraining}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>90/10</span>
                  <span>60/40</span>
                </div>
              </div>
            </div>
          </CardContent>
          
          <CardFooter>
            <Button 
              onClick={handleTrainModel} 
              disabled={isTraining || !uploadedFile}
              className="w-full"
            >
              {isTraining && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {isTraining ? 'Training in Progress...' : isCompleted ? 'Train Again' : 'Train Model'}
            </Button>
          </CardFooter>
        </Card>
      )}
      
      {trainingProgress && (
        <div className="mt-8">
          <h3 className="text-lg font-semibold mb-4">Training Progress</h3>
          <div className="space-y-4">
            <Progress value={trainingProgress.progress} />
            
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">{trainingProgress.message}</span>
              <span className="font-medium">{Math.round(trainingProgress.progress)}%</span>
            </div>
            
            {isCompleted && (
              <div className="flex justify-end">
                <Button onClick={() => navigate('/results')}>View Results</Button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelTraining;
