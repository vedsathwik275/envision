
import React from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { BarChart, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

interface RecentPredictionProps {
  id: string;
  title: string;
  type: "order-volume" | "tender-performance" | "carrier-performance";
  createdAt: string;
  lanes: number;
  className?: string;
}

export function RecentPrediction({
  id,
  title,
  type,
  createdAt,
  lanes,
  className
}: RecentPredictionProps) {
  const predictionTypeLabels = {
    "order-volume": "Order Volume",
    "tender-performance": "Tender Performance",
    "carrier-performance": "Carrier Performance"
  };

  const predictionTypeColors = {
    "order-volume": "border-l-4 border-l-blue-500",
    "tender-performance": "border-l-4 border-l-amber-500",
    "carrier-performance": "border-l-4 border-l-green-500"
  };

  return (
    <Card className={cn("overflow-hidden", predictionTypeColors[type], className)}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <Badge variant="secondary">{predictionTypeLabels[type]}</Badge>
        </div>
        <CardTitle className="mt-2 truncate">{title}</CardTitle>
        <CardDescription>Created: {createdAt}</CardDescription>
      </CardHeader>
      <CardContent className="pb-0">
        <div className="flex items-center space-x-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-muted">
            <BarChart className="h-5 w-5 text-muted-foreground" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Lanes</p>
            <p className="text-xl font-bold">{lanes}</p>
          </div>
        </div>
      </CardContent>
      <CardFooter className="pt-4">
        <Button asChild variant="ghost" size="sm" className="w-full justify-center">
          <Link to={`/predictions/${type}/${id}`}>
            View Details
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </CardFooter>
    </Card>
  );
}
