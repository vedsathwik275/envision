
import React from "react";
import { PageContainer, PageHeader, PageContent } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/button";
import { useApp } from "@/context/AppContext";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Link, useParams } from "react-router-dom";
import { Search, Plus, BarChart, ArrowRight } from "lucide-react";
import { useState } from "react";

const PredictionList = () => {
  const { modelType = "order-volume" } = useParams<{ modelType: string }>();
  const { predictions, loading } = useApp();
  const [searchTerm, setSearchTerm] = useState("");
  
  // Model type display names
  const modelTypeLabels: Record<string, string> = {
    "order-volume": "Order Volume",
    "tender-performance": "Tender Performance",
    "carrier-performance": "Carrier Performance"
  };
  
  // Filter predictions by model type and search term
  const filteredPredictions = predictions
    .filter(prediction => prediction.type === modelType)
    .filter(prediction => 
      prediction.title.toLowerCase().includes(searchTerm.toLowerCase())
    );

  return (
    <PageContainer>
      <PageHeader>
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{modelTypeLabels[modelType]} Predictions</h1>
            <p className="text-muted-foreground">
              View and manage your {modelTypeLabels[modelType].toLowerCase()} predictions
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button asChild>
              <Link to={`/predictions/${modelType}/new`}>
                <Plus className="mr-2 h-4 w-4" />
                New Prediction
              </Link>
            </Button>
          </div>
        </div>
      </PageHeader>

      <PageContent>
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search predictions..."
              className="pl-8 w-full md:w-[300px]"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
        
        {loading.predictions ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader>
                  <div className="h-5 bg-muted rounded w-3/4"></div>
                  <div className="h-4 bg-muted rounded w-1/2 mt-2"></div>
                </CardHeader>
                <CardContent>
                  <div className="h-16 bg-muted rounded"></div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : filteredPredictions.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredPredictions.map((prediction) => (
              <Link 
                to={`/predictions/${modelType}/${prediction.id}`}
                key={prediction.id}
                className="transition-all hover:shadow-md"
              >
                <Card>
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <Badge variant="secondary">{modelTypeLabels[prediction.type]}</Badge>
                      {prediction.status === "completed" && (
                        <Badge className="bg-neural-success text-white">Completed</Badge>
                      )}
                      {prediction.status === "processing" && (
                        <Badge className="bg-neural-warning text-neural-dark">Processing</Badge>
                      )}
                      {prediction.status === "failed" && (
                        <Badge className="bg-neural-error text-white">Failed</Badge>
                      )}
                    </div>
                    <CardTitle className="mt-2 truncate">{prediction.title}</CardTitle>
                    <p className="text-sm text-muted-foreground">
                      Created: {prediction.createdAt} • Model: {prediction.modelId}
                    </p>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-muted">
                          <BarChart className="h-5 w-5 text-muted-foreground" />
                        </div>
                        <div className="ml-3">
                          <p className="text-sm text-muted-foreground">Lanes</p>
                          <p className="text-lg font-bold">{prediction.lanes}</p>
                        </div>
                      </div>
                      <Button variant="ghost" size="sm" className="gap-1">
                        View Details
                        <ArrowRight className="h-4 w-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12 text-center">
              <BarChart className="h-12 w-12 text-muted-foreground mb-4" />
              <h2 className="text-xl font-medium mb-2">No Predictions Found</h2>
              <p className="text-muted-foreground mb-6 max-w-md">
                {searchTerm 
                  ? `No ${modelTypeLabels[modelType]} predictions match your search criteria.`
                  : `You haven't created any ${modelTypeLabels[modelType]} predictions yet.`
                }
              </p>
              <Button asChild>
                <Link to={`/predictions/${modelType}/new`}>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Your First Prediction
                </Link>
              </Button>
            </CardContent>
          </Card>
        )}
      </PageContent>
    </PageContainer>
  );
};

export default PredictionList;
