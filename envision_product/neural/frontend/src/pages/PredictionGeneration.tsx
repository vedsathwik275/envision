
import React from "react";
import { PageContainer, PageHeader, PageContent } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/button";
import { useApp } from "@/context/AppContext";
import { PredictionForm } from "@/components/predictions/PredictionForm";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { toast } from "sonner";
import { format } from "date-fns";
import { useNavigate } from "react-router-dom";

const PredictionGeneration = () => {
  const { modelType = "order-volume" } = useParams<{ modelType: string }>();
  const [searchParams] = useSearchParams();
  const selectedModelId = searchParams.get("model") || undefined;
  const { models, loading, addPrediction } = useApp();
  const navigate = useNavigate();

  // Model type display names
  const modelTypeLabels: Record<string, string> = {
    "order-volume": "Order Volume",
    "tender-performance": "Tender Performance",
    "carrier-performance": "Carrier Performance"
  };

  const handleGeneratePrediction = async (data: any) => {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Create a mock prediction and add to context
    const newPrediction = {
      id: `pred-${Date.now()}`,
      title: data.predictionName,
      type: modelType,
      modelId: data.modelId,
      createdAt: format(new Date(), "PP"),
      lanes: Math.floor(Math.random() * 40) + 10,
      status: "completed"
    };
    
    addPrediction(newPrediction);
    
    toast.success("Prediction generated successfully", {
      description: `Your ${modelTypeLabels[modelType]} prediction has been created.`
    });
    
    // Navigate to the prediction results
    navigate(`/predictions/${modelType}/${newPrediction.id}`);
    
    return Promise.resolve();
  };

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
        </div>
        <div className="mt-2">
          <h1 className="text-3xl font-bold tracking-tight">Generate {modelTypeLabels[modelType]} Prediction</h1>
          <p className="text-muted-foreground">
            Create a new prediction using your trained models
          </p>
        </div>
      </PageHeader>

      <PageContent>
        <PredictionForm
          modelType={modelType as any}
          models={models}
          selectedModelId={selectedModelId}
          onSubmit={handleGeneratePrediction}
          loading={loading.models}
        />
      </PageContent>
    </PageContainer>
  );
};

export default PredictionGeneration;
