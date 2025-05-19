
import React from "react";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface StatCardProps {
  title: string;
  value: string | number;
  change?: string;
  trend?: "up" | "down" | "neutral";
  icon?: React.ReactNode;
  className?: string;
  loading?: boolean;
}

export function StatCard({ 
  title, 
  value, 
  change, 
  trend = "neutral", 
  icon, 
  className,
  loading = false
}: StatCardProps) {
  const trendColor = {
    up: "text-neural-success",
    down: "text-neural-error",
    neutral: "text-muted-foreground"
  };

  if (loading) {
    return (
      <Card className={cn("overflow-hidden", className)}>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            <Skeleton className="h-4 w-24" />
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-8 w-16 mb-2" />
          <Skeleton className="h-4 w-20" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("overflow-hidden", className)}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="pb-2">
        <div className="text-2xl font-bold">{value}</div>
        {change && (
          <p className={cn("text-xs font-medium", trendColor[trend])}>
            {trend === "up" && "↑"}
            {trend === "down" && "↓"}
            {change}
          </p>
        )}
      </CardContent>
      {icon && (
        <CardFooter className="pb-4 pt-0">
          <div className="text-muted-foreground/50">{icon}</div>
        </CardFooter>
      )}
    </Card>
  );
}
