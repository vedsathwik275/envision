
import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Search, MapPin, Loader } from "lucide-react";
import { ComparativeBarChart } from "../visualizations/ComparativeBarChart";
import { toast } from "sonner";

interface CarrierPerformance {
  carrierId: string;
  carrierName: string;
  onTimePerformance: number;
  tenderAcceptance: number;
  avgTransitTime: number;
  costPerMile?: number;
}

interface LaneDetail {
  origin: string;
  destination: string;
  distance: number;
  avgVolume: number;
  carrierPerformance: CarrierPerformance[];
}

interface LaneExplorerProps {
  origins: string[];
  destinations: string[];
  onSearch: (origin: string, destination: string) => Promise<LaneDetail>;
  loading?: boolean;
}

export function LaneExplorer({
  origins,
  destinations,
  onSearch,
  loading = false
}: LaneExplorerProps) {
  const [origin, setOrigin] = useState<string>("");
  const [destination, setDestination] = useState<string>("");
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [laneDetail, setLaneDetail] = useState<LaneDetail | null>(null);
  const [comparisonMetric, setComparisonMetric] = useState<"onTimePerformance" | "tenderAcceptance" | "avgTransitTime" | "costPerMile">("onTimePerformance");
  const [searchHistory, setSearchHistory] = useState<{origin: string, destination: string}[]>([]);
  
  const handleSearch = async () => {
    if (!origin || !destination) {
      toast.error("Please select both origin and destination");
      return;
    }
    
    setIsSearching(true);
    
    try {
      const result = await onSearch(origin, destination);
      setLaneDetail(result);
      
      // Add to search history if not already present
      const searchExists = searchHistory.some(
        item => item.origin === origin && item.destination === destination
      );
      
      if (!searchExists) {
        setSearchHistory(prev => [
          { origin, destination }, 
          ...prev.slice(0, 4) // Keep only the 5 most recent
        ]);
      }
    } catch (error) {
      toast.error("Failed to load lane data", {
        description: error instanceof Error ? error.message : "An unknown error occurred."
      });
    } finally {
      setIsSearching(false);
    }
  };
  
  const loadHistoryItem = (item: {origin: string, destination: string}) => {
    setOrigin(item.origin);
    setDestination(item.destination);
    handleSearch();
  };
  
  // Format metric values for display
  const formatMetricValue = (metric: string, value: number) => {
    switch (metric) {
      case "onTimePerformance":
      case "tenderAcceptance":
        return `${(value * 100).toFixed(1)}%`;
      case "avgTransitTime":
        return `${value.toFixed(1)} hrs`;
      case "costPerMile":
        return `$${value.toFixed(2)}`;
      default:
        return value.toString();
    }
  };
  
  const metricLabels = {
    onTimePerformance: "On-Time Performance",
    tenderAcceptance: "Tender Acceptance",
    avgTransitTime: "Avg Transit Time",
    costPerMile: "Cost Per Mile"
  };
  
  // Prepare chart data
  const prepareChartData = () => {
    if (!laneDetail) return [];
    
    return laneDetail.carrierPerformance.map(carrier => ({
      name: carrier.carrierName,
      value: comparisonMetric === "avgTransitTime" 
        ? carrier.avgTransitTime 
        : comparisonMetric === "costPerMile"
        ? (carrier.costPerMile || 0)
        : carrier[comparisonMetric] * 100 // Convert to percentage for display
    }));
  };
  
  const chartData = prepareChartData();
  
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Lane Explorer</CardTitle>
          <CardDescription>Loading lane data...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center p-8">
            <Loader className="h-8 w-8 animate-spin text-primary" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Lane Explorer</CardTitle>
        <CardDescription>
          Compare carrier performance across specific lanes
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label className="text-sm font-medium mb-1 block">Origin</label>
              <Select value={origin} onValueChange={setOrigin}>
                <SelectTrigger>
                  <SelectValue placeholder="Select origin" />
                </SelectTrigger>
                <SelectContent>
                  {origins.map(loc => (
                    <SelectItem key={loc} value={loc}>{loc}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <label className="text-sm font-medium mb-1 block">Destination</label>
              <Select value={destination} onValueChange={setDestination}>
                <SelectTrigger>
                  <SelectValue placeholder="Select destination" />
                </SelectTrigger>
                <SelectContent>
                  {destinations.map(loc => (
                    <SelectItem key={loc} value={loc}>{loc}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div className="flex flex-wrap gap-2 items-center">
            <Button 
              onClick={handleSearch} 
              disabled={isSearching || !origin || !destination}
              className="flex-shrink-0"
            >
              {isSearching ? (
                <>
                  <Loader className="mr-2 h-4 w-4 animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="mr-2 h-4 w-4" />
                  Search Lane
                </>
              )}
            </Button>
            
            <div className="text-sm text-muted-foreground ml-auto">
              <span className="font-medium">Recent searches:</span>
            </div>
            
            <div className="flex flex-wrap gap-1">
              {searchHistory.map((item, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => loadHistoryItem(item)}
                  className="text-xs"
                >
                  {item.origin} → {item.destination}
                </Button>
              ))}
              {searchHistory.length === 0 && (
                <span className="text-xs text-muted-foreground italic">
                  None yet
                </span>
              )}
            </div>
          </div>
          
          {laneDetail ? (
            <div className="mt-6 space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium flex items-center">
                    <MapPin className="h-5 w-5 mr-1 text-neural-primary" />
                    {laneDetail.origin} → {laneDetail.destination}
                  </h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    {laneDetail.distance} miles • Avg. volume: {laneDetail.avgVolume.toLocaleString()} shipments/month
                  </p>
                </div>
                <div className="text-sm">
                  <span className="font-medium mr-2">Compare:</span>
                  <Select value={comparisonMetric} onValueChange={(v) => setComparisonMetric(v as any)}>
                    <SelectTrigger className="w-[180px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="onTimePerformance">On-Time Performance</SelectItem>
                      <SelectItem value="tenderAcceptance">Tender Acceptance</SelectItem>
                      <SelectItem value="avgTransitTime">Avg Transit Time</SelectItem>
                      <SelectItem value="costPerMile">Cost Per Mile</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="rounded-md border p-4">
                <h3 className="text-base font-medium mb-4">
                  Carrier {metricLabels[comparisonMetric]} Comparison
                </h3>
                <div className="h-[300px]">
                  <ComparativeBarChart data={chartData} />
                </div>
              </div>
              
              <div className="rounded-md border">
                <Tabs defaultValue="performance">
                  <TabsList className="w-full grid grid-cols-3">
                    <TabsTrigger value="performance">Performance</TabsTrigger>
                    <TabsTrigger value="tender">Tender Acceptance</TabsTrigger>
                    <TabsTrigger value="transit">Transit Time</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="performance" className="p-4">
                    <div className="space-y-4">
                      <h3 className="text-base font-medium">Carrier On-Time Performance</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {laneDetail.carrierPerformance.map(carrier => (
                          <div 
                            key={carrier.carrierId}
                            className="border rounded-md p-4 flex justify-between items-center"
                          >
                            <div>
                              <p className="font-medium">{carrier.carrierName}</p>
                              <p className="text-sm text-muted-foreground">
                                ID: {carrier.carrierId}
                              </p>
                            </div>
                            <div className="text-right">
                              <p className="text-2xl font-bold text-neural-primary">
                                {formatMetricValue("onTimePerformance", carrier.onTimePerformance)}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                On-Time Rate
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="tender" className="p-4">
                    <div className="space-y-4">
                      <h3 className="text-base font-medium">Carrier Tender Acceptance</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {laneDetail.carrierPerformance.map(carrier => (
                          <div 
                            key={carrier.carrierId}
                            className="border rounded-md p-4 flex justify-between items-center"
                          >
                            <div>
                              <p className="font-medium">{carrier.carrierName}</p>
                              <p className="text-sm text-muted-foreground">
                                ID: {carrier.carrierId}
                              </p>
                            </div>
                            <div className="text-right">
                              <p className="text-2xl font-bold text-neural-secondary">
                                {formatMetricValue("tenderAcceptance", carrier.tenderAcceptance)}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                Acceptance Rate
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="transit" className="p-4">
                    <div className="space-y-4">
                      <h3 className="text-base font-medium">Average Transit Times</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {laneDetail.carrierPerformance.map(carrier => (
                          <div 
                            key={carrier.carrierId}
                            className="border rounded-md p-4 flex justify-between items-center"
                          >
                            <div>
                              <p className="font-medium">{carrier.carrierName}</p>
                              <p className="text-sm text-muted-foreground">
                                ID: {carrier.carrierId}
                              </p>
                            </div>
                            <div className="text-right">
                              <p className="text-2xl font-bold text-neural-accent">
                                {formatMetricValue("avgTransitTime", carrier.avgTransitTime)}
                              </p>
                              <div className="flex items-center justify-end">
                                <p className="text-xs text-muted-foreground mr-2">
                                  Avg. Transit Time
                                </p>
                                {carrier.costPerMile && (
                                  <p className="text-xs bg-muted rounded px-1 py-0.5">
                                    {formatMetricValue("costPerMile", carrier.costPerMile)}
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>
              </div>
            </div>
          ) : (
            <div className="border rounded-md py-12 flex flex-col items-center justify-center">
              <MapPin className="h-12 w-12 text-muted-foreground/50 mb-4" />
              <h3 className="text-lg font-medium">Select a lane to explore</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Choose an origin and destination to view detailed carrier performance
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
