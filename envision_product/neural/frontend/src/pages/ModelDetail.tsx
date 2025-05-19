
import React, { useState, useEffect } from "react";
import { PageContainer, PageHeader, PageContent } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/button";
import { useApp } from "@/context/AppContext";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BarChart, LineChart } from "recharts";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ArrowLeft, BarChart as BarChartIcon, ChevronRight, FileText, Info, Route, TableIcon, CheckCircle } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { BarChart as ModelPerformanceChart } from "@/components/visualizations/BarChart";
import { LineChart as ModelAccuracyChart } from "@/components/visualizations/LineChart";

const ModelDetail = () => {
  const { modelType = "", modelId = "" } = useParams<{ modelType: string, modelId: string }>();
  const { models, loading } = useApp();
  const [model, setModel] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // Model type display names
  const modelTypeLabels: Record<string, string> = {
    "order-volume": "Order Volume",
    "tender-performance": "Tender Performance",
    "carrier-performance": "Carrier Performance"
  };
  
  // Status colors
  const statusColors = {
    active: "bg-neural-success text-white",
    training: "bg-neural-warning text-neural-dark",
    failed: "bg-neural-error text-white"
  };
  
  // Status labels
  const statusLabels = {
    active: "Active",
    training: "Training",
    failed: "Failed"
  };
  
  useEffect(() => {
    // Find the model in the context
    const foundModel = models.find(m => m.id === modelId);
    
    // Simulate API delay
    setTimeout(() => {
      if (foundModel) {
        setModel({
          ...foundModel,
          // Add additional detail data that wouldn't be in the list view
          metrics: {
            mae: Math.random() * 5 + 2, // Mean Absolute Error
            rmse: Math.random() * 10 + 5, // Root Mean Square Error
            r2: Math.random() * 0.3 + 0.7, // R-squared value
            trainTime: Math.round(Math.random() * 500 + 100) // Training time in seconds
          },
          parameters: {
            epochs: Math.round(Math.random() * 100 + 50),
            batchSize: Math.pow(2, Math.round(Math.random() * 4 + 3)), // 8, 16, 32, 64, 128
            learningRate: Math.random() * 0.01,
            optimizer: ["Adam", "RMSprop", "SGD"][Math.floor(Math.random() * 3)],
            featureCount: Math.round(Math.random() * 20 + 5)
          },
          dataset: {
            name: `shipping_data_${Math.floor(Math.random() * 10000)}.csv`,
            rows: Math.round(Math.random() * 50000 + 10000),
            trainRows: Math.round(Math.random() * 40000 + 8000),
            testRows: Math.round(Math.random() * 10000 + 2000),
            trainTestSplit: Math.random() * 0.2 + 0.7 // 70-90% train split
          }
        });
      }
      setIsLoading(false);
    }, 500);
  }, [modelId, models]);
  
  // Generate performance history data for the chart
  const generatePerformanceData = () => {
    const data = [];
    const baseAccuracy = model ? model.accuracy - 5 : 85;
    
    for (let i = 1; i <= 10; i++) {
      data.push({
        name: `Epoch ${i * 10}`,
        value: baseAccuracy + (i / 2)
      });
    }
    
    return data;
  };
  
  // Generate feature importance data
  const generateFeatureData = () => {
    const features = [
      "distance", "carrier_rating", "weight", "volume", 
      "day_of_week", "month", "transit_time", "fuel_price", 
      "weather_condition", "carrier_capacity"
    ];
    
    return features.map(feature => ({
      name: feature,
      value: Math.random() * 100
    })).sort((a, b) => b.value - a.value);
  };
  
  const performanceData = model ? generatePerformanceData() : [];
  const featureData = model ? generateFeatureData() : [];

  if (isLoading || loading.models) {
    return (
      <PageContainer>
        <PageHeader>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" asChild>
              <Link to="/models">
                <ArrowLeft className="h-4 w-4 mr-1" />
                Back to Models
              </Link>
            </Button>
          </div>
          <div className="mt-2">
            <div className="h-8 w-64 bg-muted rounded animate-pulse"></div>
            <div className="h-4 w-96 bg-muted rounded mt-2 animate-pulse"></div>
          </div>
        </PageHeader>

        <PageContent>
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <div className="h-6 w-32 bg-muted rounded animate-pulse"></div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="h-4 w-full bg-muted rounded animate-pulse"></div>
                  <div className="h-4 w-3/4 bg-muted rounded animate-pulse"></div>
                  <div className="h-4 w-1/2 bg-muted rounded animate-pulse"></div>
                </div>
              </CardContent>
            </Card>
          </div>
        </PageContent>
      </PageContainer>
    );
  }
  
  if (!model) {
    return (
      <PageContainer>
        <PageHeader>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" asChild>
              <Link to="/models">
                <ArrowLeft className="h-4 w-4 mr-1" />
                Back to Models
              </Link>
            </Button>
          </div>
          <div className="mt-2">
            <h1 className="text-3xl font-bold tracking-tight">Model Not Found</h1>
            <p className="text-muted-foreground">
              The requested model could not be found
            </p>
          </div>
        </PageHeader>

        <PageContent>
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-10">
              <Info className="h-16 w-16 text-muted-foreground mb-4" />
              <h2 className="text-xl font-medium mb-2">Model Not Found</h2>
              <p className="text-muted-foreground text-center max-w-md mb-6">
                The model you are looking for doesn't exist or has been removed.
              </p>
              <Button asChild>
                <Link to="/models">View All Models</Link>
              </Button>
            </CardContent>
          </Card>
        </PageContent>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageHeader>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/models">
              <ArrowLeft className="h-4 w-4 mr-1" />
              Back to Models
            </Link>
          </Button>
          <ChevronRight className="h-4 w-4 text-muted-foreground" />
          <Button variant="ghost" size="sm" asChild>
            <Link to={`/models/${modelType}`}>
              {modelTypeLabels[modelType] || modelType}
            </Link>
          </Button>
        </div>
        <div className="mt-2 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h1 className="text-3xl font-bold tracking-tight">{model.name}</h1>
              <Badge className={statusColors[model.status as keyof typeof statusColors]}>
                {statusLabels[model.status as keyof typeof statusLabels]}
              </Badge>
            </div>
            <p className="text-muted-foreground">
              {modelTypeLabels[modelType]} Model • Created: {model.createdAt}
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" asChild>
              <Link to={`/models/train?clone=${model.id}`}>
                Clone
              </Link>
            </Button>
            <Button asChild>
              <Link to={`/predictions/${modelType}/new?model=${model.id}`}>
                Generate Prediction
              </Link>
            </Button>
          </div>
        </div>
      </PageHeader>

      <PageContent>
        <div className="grid gap-6 md:grid-cols-3">
          <Card className="md:col-span-1">
            <CardHeader>
              <CardTitle>Model Performance</CardTitle>
              <CardDescription>Key performance metrics</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex flex-col items-center justify-center">
                <div className="relative flex h-32 w-32 items-center justify-center">
                  <svg className="h-full w-full" viewBox="0 0 100 100">
                    <circle
                      className="stroke-muted"
                      cx="50"
                      cy="50"
                      r="40"
                      strokeWidth="8"
                      fill="none"
                    />
                    <circle
                      className="stroke-neural-primary"
                      cx="50"
                      cy="50"
                      r="40"
                      strokeWidth="8"
                      fill="none"
                      strokeDasharray={`${2.5 * Math.PI * 40 * model.accuracy / 100} ${2.5 * Math.PI * 40}`}
                      strokeDashoffset={2.5 * Math.PI * 10}
                      transform="rotate(-90 50 50)"
                    />
                  </svg>
                  <div className="absolute flex flex-col items-center justify-center">
                    <span className="text-3xl font-bold">{model.accuracy}%</span>
                    <span className="text-xs text-muted-foreground">Accuracy</span>
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <span className="text-xs text-muted-foreground">MAE</span>
                  <p className="text-lg font-medium">{model.metrics.mae.toFixed(2)}</p>
                </div>
                <div className="space-y-1">
                  <span className="text-xs text-muted-foreground">RMSE</span>
                  <p className="text-lg font-medium">{model.metrics.rmse.toFixed(2)}</p>
                </div>
                <div className="space-y-1">
                  <span className="text-xs text-muted-foreground">R² Score</span>
                  <p className="text-lg font-medium">{model.metrics.r2.toFixed(3)}</p>
                </div>
                <div className="space-y-1">
                  <span className="text-xs text-muted-foreground">Training Time</span>
                  <p className="text-lg font-medium">{model.metrics.trainTime}s</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>Training History</CardTitle>
              <CardDescription>Model performance across epochs</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[250px]">
                <LineChart data={performanceData} />
              </div>
            </CardContent>
          </Card>
        </div>
        
        <Tabs defaultValue="overview">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="features">Features</TabsTrigger>
            <TabsTrigger value="dataset">Dataset</TabsTrigger>
          </TabsList>
          <TabsContent value="overview" className="space-y-4 pt-4">
            <Card>
              <CardHeader>
                <CardTitle>Hyperparameters</CardTitle>
                <CardDescription>Model training configuration</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-y-4 sm:grid-cols-3">
                  <div className="space-y-1">
                    <span className="text-xs text-muted-foreground">Epochs</span>
                    <p className="font-medium">{model.parameters.epochs}</p>
                  </div>
                  <div className="space-y-1">
                    <span className="text-xs text-muted-foreground">Batch Size</span>
                    <p className="font-medium">{model.parameters.batchSize}</p>
                  </div>
                  <div className="space-y-1">
                    <span className="text-xs text-muted-foreground">Learning Rate</span>
                    <p className="font-medium">{model.parameters.learningRate.toExponential(2)}</p>
                  </div>
                  <div className="space-y-1">
                    <span className="text-xs text-muted-foreground">Optimizer</span>
                    <p className="font-medium">{model.parameters.optimizer}</p>
                  </div>
                  <div className="space-y-1">
                    <span className="text-xs text-muted-foreground">Feature Count</span>
                    <p className="font-medium">{model.parameters.featureCount}</p>
                  </div>
                  <div className="space-y-1">
                    <span className="text-xs text-muted-foreground">Train/Test Split</span>
                    <p className="font-medium">{Math.round(model.dataset.trainTestSplit * 100)}% / {Math.round((1 - model.dataset.trainTestSplit) * 100)}%</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Prediction Types</CardTitle>
                <CardDescription>What this model can predict</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {modelType === "order-volume" && (
                    <>
                      <div className="flex items-start gap-4">
                        <div className="rounded-md bg-primary/10 p-2">
                          <TableIcon className="h-6 w-6 text-primary" />
                        </div>
                        <div>
                          <h4 className="text-base font-medium">Shipment Volume Predictions</h4>
                          <p className="text-sm text-muted-foreground">
                            Forecast expected order volumes between specific origin-destination pairs
                            based on historical data patterns and seasonality.
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-start gap-4">
                        <div className="rounded-md bg-primary/10 p-2">
                          <BarChartIcon className="h-6 w-6 text-primary" />
                        </div>
                        <div>
                          <h4 className="text-base font-medium">Capacity Planning</h4>
                          <p className="text-sm text-muted-foreground">
                            Plan ahead for resource allocation by understanding future shipping demand
                            across different lanes.
                          </p>
                        </div>
                      </div>
                    </>
                  )}
                  
                  {modelType === "tender-performance" && (
                    <>
                      <div className="flex items-start gap-4">
                        <div className="rounded-md bg-primary/10 p-2">
                          <TableIcon className="h-6 w-6 text-primary" />
                        </div>
                        <div>
                          <h4 className="text-base font-medium">Tender Acceptance Predictions</h4>
                          <p className="text-sm text-muted-foreground">
                            Forecast the likelihood of carriers accepting loads on specific lanes
                            based on historical performance and market conditions.
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-start gap-4">
                        <div className="rounded-md bg-primary/10 p-2">
                          <BarChartIcon className="h-6 w-6 text-primary" />
                        </div>
                        <div>
                          <h4 className="text-base font-medium">Carrier Recommendation</h4>
                          <p className="text-sm text-muted-foreground">
                            Identify the carriers most likely to accept tenders for specific lanes
                            to improve tender acceptance rates.
                          </p>
                        </div>
                      </div>
                    </>
                  )}
                  
                  {modelType === "carrier-performance" && (
                    <>
                      <div className="flex items-start gap-4">
                        <div className="rounded-md bg-primary/10 p-2">
                          <TableIcon className="h-6 w-6 text-primary" />
                        </div>
                        <div>
                          <h4 className="text-base font-medium">On-Time Performance Predictions</h4>
                          <p className="text-sm text-muted-foreground">
                            Forecast carrier on-time delivery performance for specific lanes and routes
                            based on historical data and current conditions.
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-start gap-4">
                        <div className="rounded-md bg-primary/10 p-2">
                          <Route className="h-6 w-6 text-primary" />
                        </div>
                        <div>
                          <h4 className="text-base font-medium">Carrier Comparison</h4>
                          <p className="text-sm text-muted-foreground">
                            Compare expected performance metrics across different carriers for the same lane
                            to make optimal carrier assignment decisions.
                          </p>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </CardContent>
              <CardFooter>
                <Button variant="outline" asChild className="w-full">
                  <Link to={`/predictions/${modelType}/new?model=${model.id}`}>
                    Generate New Prediction
                  </Link>
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>
          
          <TabsContent value="features" className="space-y-4 pt-4">
            <Card>
              <CardHeader>
                <CardTitle>Feature Importance</CardTitle>
                <CardDescription>Impact of different features on model predictions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[400px]">
                  <ModelPerformanceChart data={featureData} />
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="dataset" className="space-y-4 pt-4">
            <Card>
              <CardHeader>
                <CardTitle>Training Dataset</CardTitle>
                <CardDescription>Information about the data used to train this model</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="grid grid-cols-2 gap-y-4 sm:grid-cols-3">
                    <div className="space-y-1">
                      <span className="text-xs text-muted-foreground">Dataset</span>
                      <p className="font-medium">{model.dataset.name}</p>
                    </div>
                    <div className="space-y-1">
                      <span className="text-xs text-muted-foreground">Total Rows</span>
                      <p className="font-medium">{model.dataset.rows.toLocaleString()}</p>
                    </div>
                    <div className="space-y-1">
                      <span className="text-xs text-muted-foreground">Training Rows</span>
                      <p className="font-medium">{model.dataset.trainRows.toLocaleString()}</p>
                    </div>
                    <div className="space-y-1">
                      <span className="text-xs text-muted-foreground">Testing Rows</span>
                      <p className="font-medium">{model.dataset.testRows.toLocaleString()}</p>
                    </div>
                    <div className="space-y-1">
                      <span className="text-xs text-muted-foreground">Train/Test Split</span>
                      <p className="font-medium">{Math.round(model.dataset.trainTestSplit * 100)}% / {Math.round((1 - model.dataset.trainTestSplit) * 100)}%</p>
                    </div>
                    <div className="space-y-1">
                      <span className="text-xs text-muted-foreground">Feature Count</span>
                      <p className="font-medium">{model.parameters.featureCount}</p>
                    </div>
                  </div>
                  
                  <Separator />
                  
                  <div>
                    <h4 className="text-base font-medium">Data Processing Steps</h4>
                    <ul className="mt-2 space-y-2 text-sm">
                      <li className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-neural-success" />
                        Missing value imputation
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-neural-success" />
                        Outlier detection and handling
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-neural-success" />
                        Feature scaling and normalization
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-neural-success" />
                        Categorical variable encoding
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-neural-success" />
                        Feature engineering
                      </li>
                    </ul>
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button variant="outline" asChild className="w-full">
                  <Link to="/data/upload">
                    <FileText className="mr-2 h-4 w-4" />
                    View Raw Dataset
                  </Link>
                </Button>
              </CardFooter>
            </Card>
          </TabsContent>
        </Tabs>
      </PageContent>
    </PageContainer>
  );
};

export default ModelDetail;
