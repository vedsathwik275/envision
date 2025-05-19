import React, { useState } from "react";
import { BarChart, FileText, CheckCircle, ArrowRight } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatCard } from "@/components/dashboard/StatCard";
import { ModelCard } from "@/components/dashboard/ModelCard";
import { RecentPrediction } from "@/components/dashboard/RecentPrediction";
import { PageContainer, PageHeader, PageContent } from "@/components/layout/PageContainer";
import { useApp } from "@/context/AppContext";
import { BarChart as ModelPerformanceChart } from "@/components/visualizations/BarChart";
import { Link } from "react-router-dom";

const Dashboard = () => {
  const { models, predictions, stats, loading } = useApp();
  
  // Get top performing models (one of each type)
  const topModels = models
    .filter(model => model.status === "active")
    .sort((a, b) => b.accuracy - a.accuracy)
    .reduce((acc: any[], model) => {
      // Keep only one model of each type with highest accuracy
      const existingModelIndex = acc.findIndex(m => m.type === model.type);
      if (existingModelIndex === -1 || acc[existingModelIndex].accuracy < model.accuracy) {
        if (existingModelIndex !== -1) {
          acc[existingModelIndex] = model;
        } else {
          acc.push(model);
        }
      }
      return acc;
    }, [])
    .slice(0, 3);
  
  // Latest 4 predictions
  const recentPredictions = [...predictions]
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .slice(0, 4);
  
  // Chart data for model performance
  const modelPerformanceData = models
    .filter(model => model.status === "active")
    .map(model => ({
      name: model.name.length > 20 ? model.name.substring(0, 20) + "..." : model.name,
      value: model.accuracy
    }))
    .slice(0, 8);

  return (
    <PageContainer>
      <PageHeader>
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground">
              Envision Neural transportation logistics prediction platform
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button asChild>
              <Link to="/data/upload">Upload Data</Link>
            </Button>
            <Button variant="outline" asChild>
              <Link to="/models">
                View Models
              </Link>
            </Button>
          </div>
        </div>
      </PageHeader>

      <PageContent>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatCard
            title="Active Models"
            value={stats.activeModels}
            icon={<BarChart />}
            loading={loading.models}
          />
          <StatCard
            title="Avg. Model Accuracy"
            value={`${stats.modelAccuracy}%`}
            trend="up"
            change="+2.1% from last month"
            icon={<CheckCircle />}
            loading={loading.models}
          />
          <StatCard
            title="Predictions Generated"
            value={stats.predictionsGenerated}
            icon={<FileText />}
            loading={loading.predictions}
          />
          <StatCard
            title="Available Datasets"
            value={stats.datasetCount}
            icon={<FileText />}
            loading={loading.files}
          />
        </div>

        <div className="grid gap-4 md:grid-cols-7">
          <Card className="md:col-span-4">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div className="space-y-1">
                <CardTitle>Model Performance</CardTitle>
                <CardDescription>
                  Accuracy comparison across active models
                </CardDescription>
              </div>
              <Button variant="ghost" size="sm" asChild>
                <Link to="/models">
                  View all
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                {loading.models ? (
                  <div className="flex h-full items-center justify-center">
                    <div className="text-sm text-muted-foreground">Loading model data...</div>
                  </div>
                ) : (
                  <ModelPerformanceChart data={modelPerformanceData} />
                )}
              </div>
            </CardContent>
          </Card>
          <div className="grid gap-4 md:col-span-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <div className="space-y-1">
                  <CardTitle>Recent Predictions</CardTitle>
                  <CardDescription>
                    Latest prediction results
                  </CardDescription>
                </div>
                <Button variant="ghost" size="sm" asChild>
                  <Link to="/predictions/order-volume">
                    View all
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {loading.predictions ? (
                    <div className="flex h-[200px] items-center justify-center">
                      <div className="text-sm text-muted-foreground">Loading predictions...</div>
                    </div>
                  ) : recentPredictions.length > 0 ? (
                    recentPredictions.map((prediction) => (
                      <RecentPrediction
                        key={prediction.id}
                        id={prediction.id}
                        title={prediction.title}
                        type={prediction.type}
                        createdAt={prediction.createdAt}
                        lanes={prediction.lanes}
                      />
                    ))
                  ) : (
                    <div className="flex h-[200px] items-center justify-center">
                      <div className="text-sm text-muted-foreground">No predictions yet</div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <h2 className="text-2xl font-bold tracking-tight">Top Performing Models</h2>
        
        <div className="grid gap-4 md:grid-cols-3">
          {loading.models ? (
            <>
              <Card className="animate-pulse">
                <CardContent className="p-6">
                  <div className="space-y-3">
                    <div className="h-5 w-1/3 rounded-md bg-muted" />
                    <div className="h-20 w-full rounded-md bg-muted" />
                  </div>
                </CardContent>
              </Card>
              <Card className="animate-pulse">
                <CardContent className="p-6">
                  <div className="space-y-3">
                    <div className="h-5 w-1/3 rounded-md bg-muted" />
                    <div className="h-20 w-full rounded-md bg-muted" />
                  </div>
                </CardContent>
              </Card>
              <Card className="animate-pulse">
                <CardContent className="p-6">
                  <div className="space-y-3">
                    <div className="h-5 w-1/3 rounded-md bg-muted" />
                    <div className="h-20 w-full rounded-md bg-muted" />
                  </div>
                </CardContent>
              </Card>
            </>
          ) : topModels.length > 0 ? (
            topModels.map((model) => (
              <ModelCard
                key={model.id}
                id={model.id}
                name={model.name}
                type={model.type}
                accuracy={model.accuracy}
                status={model.status}
                lastUpdated={model.lastUpdated}
              />
            ))
          ) : (
            <div className="md:col-span-3 flex justify-center p-10">
              <div className="text-center">
                <p className="text-lg font-medium">No models available</p>
                <p className="text-sm text-muted-foreground mb-4">
                  Start by training your first model
                </p>
                <Button asChild>
                  <Link to="/models/train">Train First Model</Link>
                </Button>
              </div>
            </div>
          )}
        </div>
      </PageContent>
    </PageContainer>
  );
};

export default Dashboard;
