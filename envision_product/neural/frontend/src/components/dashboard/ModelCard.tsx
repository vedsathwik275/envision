
import React from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { BarChart, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

interface ModelCardProps {
  id: string;
  name: string;
  type: "order-volume" | "tender-performance" | "carrier-performance";
  accuracy: number;
  status: "active" | "training" | "failed";
  lastUpdated: string;
  className?: string;
}

export function ModelCard({
  id,
  name,
  type,
  accuracy,
  status,
  lastUpdated,
  className
}: ModelCardProps) {
  const modelTypeLabels = {
    "order-volume": "Order Volume",
    "tender-performance": "Tender Performance",
    "carrier-performance": "Carrier Performance"
  };

  const statusColors = {
    active: "bg-neural-success text-white",
    training: "bg-neural-warning text-neural-dark",
    failed: "bg-neural-error text-white"
  };

  const statusLabels = {
    active: "Active",
    training: "Training",
    failed: "Failed"
  };

  const getAccuracyColor = (acc: number) => {
    if (acc >= 90) return "text-neural-success";
    if (acc >= 70) return "text-neural-warning";
    return "text-neural-error";
  };

  return (
    <Card className={cn("overflow-hidden h-full flex flex-col", className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <Badge variant="outline">{modelTypeLabels[type]}</Badge>
          <Badge className={statusColors[status]}>{statusLabels[status]}</Badge>
        </div>
        <CardTitle className="mt-2">{name}</CardTitle>
        <CardDescription>Last updated: {lastUpdated}</CardDescription>
      </CardHeader>
      <CardContent className="pb-0 flex-grow">
        <div className="flex items-center space-x-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
            <BarChart className="h-6 w-6 text-primary" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Accuracy</p>
            <p className={cn("text-2xl font-bold", getAccuracyColor(accuracy))}>
              {accuracy}%
            </p>
          </div>
        </div>
      </CardContent>
      <CardFooter className="pt-4">
        <div className="flex w-full justify-between">
          <Button asChild variant="ghost" size="sm">
            <Link to={`/models/${type}/${id}`}>
              Details
            </Link>
          </Button>
          <Button asChild variant="outline" size="sm">
            <Link to={`/predictions/${type}/new?model=${id}`}>
              Generate Prediction
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}
