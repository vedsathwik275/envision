
import React from "react";
import { PageContainer, PageHeader, PageContent } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/button";
import { useApp } from "@/context/AppContext";
import { ModelTrainingForm } from "@/components/models/ModelTrainingForm";
import { Link } from "react-router-dom";
import { format } from "date-fns";
import { ArrowLeft } from "lucide-react";
import { toast } from "sonner";

const ModelTraining = () => {
  const { files, loading, addModel } = useApp();

  const handleTrainModel = async (data: any) => {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Create a mock model and add to context
    const newModel = {
      id: `model-${Date.now()}`,
      name: data.modelName,
      type: data.modelType,
      accuracy: Math.round(Math.random() * 10 + 85), // Random between 85-95%
      status: "training",
      createdAt: format(new Date(), "PP"),
      lastUpdated: format(new Date(), "PP")
    };
    
    addModel(newModel);
    
    toast.success("Model training started", {
      description: `${data.modelName} is now training. You'll be notified when it's complete.`
    });
    
    return Promise.resolve();
  };

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
          <h1 className="text-3xl font-bold tracking-tight">Train New Model</h1>
          <p className="text-muted-foreground">
            Configure and train a new predictive model for your logistics data
          </p>
        </div>
      </PageHeader>

      <PageContent>
        <ModelTrainingForm
          onSubmit={handleTrainModel}
          files={files}
          loading={loading.files}
        />
      </PageContent>
    </PageContainer>
  );
};

export default ModelTraining;
