import React, { useState, useEffect } from "react";
import { PageContainer, PageHeader, PageContent } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/button";
import { useApp } from "@/context/AppContext";
import { PredictionResults as PredictionResultsComponent } from "@/components/predictions/PredictionResults";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, ChevronRight } from "lucide-react";
import { predictionApi } from "@/services/api";
import { toast } from "sonner";

const PredictionResults = () => {
  const { modelType = "", predictionId = "" } = useParams<{ modelType: string, predictionId: string }>();
  const { predictions, models } = useApp();
  const [prediction, setPrediction] = useState<any | null>(null);
  const [results, setResults] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Model type display names
  const modelTypeLabels: Record<string, string> = {
    "order-volume": "Order Volume",
    "tender-performance": "Tender Performance",
    "carrier-performance": "Carrier Performance"
  };

  // Map model type URL param to actual API model type
  const modelTypeMap: Record<string, string> = {
    "order-volume": "order_volume",
    "tender-performance": "tender_performance",
    "carrier-performance": "carrier_performance"
  };
  
  useEffect(() => {
    // Find the prediction in the context
    const foundPrediction = predictions.find(p => p.prediction_id === predictionId);
    setIsLoading(true);
    
    const loadPredictionData = async () => {
      try {
        if (foundPrediction) {
          setPrediction(foundPrediction);
          
          // Get the model_id from the prediction
          const { model_id, model_type } = foundPrediction;
          
          // Fetch prediction results based on model type
          let apiResponse;
          let formattedResults: any[] = [];
          
          switch (model_type) {
            case "order_volume":
              apiResponse = await predictionApi.getOrderVolumePredictions(model_id);
              formattedResults = apiResponse.data?.predictions 
                ? apiResponse.data.predictions.map(item => ({
                    id: `${item.source_city}-${item.destination_city}-${item.month}`,
                    origin: item.source_city,
                    destination: item.destination_city,
                    date: item.month,
                    value: item.predicted_volume,
                    confidence: 0.85 // Confidence not provided in API, using placeholder
                  }))
                : [];
              break;
            
            case "tender_performance":
              apiResponse = await predictionApi.getTenderPerformancePredictions(model_id);
              formattedResults = apiResponse.data?.predictions 
                ? apiResponse.data.predictions.map(item => ({
                    id: `${item.carrier}-${item.source_city}-${item.dest_city}`,
                    origin: item.source_city,
                    destination: item.dest_city,
                    carrier: item.carrier,
                    value: item.predicted_performance / 100, // Convert percentage to decimal
                    confidence: 0.9 // Confidence not provided in API, using placeholder
                  }))
                : [];
              break;
            
            case "carrier_performance":
              apiResponse = await predictionApi.getCarrierPerformancePredictions(model_id);
              formattedResults = apiResponse.data?.predictions 
                ? apiResponse.data.predictions.map(item => ({
                    id: `${item.carrier}-${item.source_city}-${item.dest_city}`,
                    origin: item.source_city,
                    destination: item.dest_city,
                    carrier: item.carrier,
                    value: item.predicted_ontime_performance / 100, // Convert percentage to decimal
                    confidence: 0.9 // Confidence not provided in API, using placeholder
                  }))
                : [];
              break;
          }
          
          setResults(formattedResults);
        }
      } catch (error: any) {
        console.error("Error fetching prediction results:", error);
        toast.error("Failed to load prediction results", {
          description: error.message || "There was an error loading the prediction data."
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    loadPredictionData();
  }, [predictionId, predictions, modelType]);

  return (
    <PageContainer>
      <PageHeader>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" asChild>
            <Link to={`/predictions/${modelType}`}>
              <ArrowLeft className="h-4 w-4 mr-1" />
              Back to {modelTypeLabels[modelType]} Predictions
            </Link>
          </Button>
          {prediction && (
            <>
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">{prediction.title}</span>
            </>
          )}
        </div>
        <div className="mt-2">
          <h1 className="text-3xl font-bold tracking-tight">
            {isLoading ? "Loading Prediction..." : prediction ? prediction.title : "Prediction Not Found"}
          </h1>
          {prediction && (
            <p className="text-muted-foreground">
              {modelTypeLabels[modelType]} Prediction • Created: {new Date(prediction.created_at).toLocaleDateString()}
            </p>
          )}
        </div>
      </PageHeader>

      <PageContent>
        {isLoading ? (
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-muted rounded w-1/4"></div>
            <div className="h-96 bg-muted rounded"></div>
          </div>
        ) : prediction ? (
          <PredictionResultsComponent
            predictionId={predictionId}
            modelType={modelType as any}
            title={prediction.title}
            description={`${modelTypeLabels[modelType]} prediction using model ${prediction.model_id}`}
            results={results}
            createdAt={prediction.created_at}
          />
        ) : (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <h2 className="text-2xl font-semibold">Prediction Not Found</h2>
            <p className="text-muted-foreground mt-2 mb-6">
              The requested prediction could not be found or has been deleted.
            </p>
            <Button asChild>
              <Link to={`/predictions/${modelType}/new`}>Generate New Prediction</Link>
            </Button>
          </div>
        )}
      </PageContent>
    </PageContainer>
  );
};

export default PredictionResults;
