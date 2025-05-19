
import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Download, Search, Filter, BarChart } from "lucide-react";
import { BarChart as PredictionChart } from "../visualizations/BarChart";
import { LineChart } from "../visualizations/LineChart";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";

interface PredictionResult {
  id: string;
  origin: string;
  destination: string;
  date?: string;
  carrier?: string;
  value: number;
  confidence: number;
  metadata?: Record<string, any>;
}

interface PredictionResultsProps {
  predictionId: string;
  modelType: "order-volume" | "tender-performance" | "carrier-performance";
  title: string;
  description?: string;
  results: PredictionResult[];
  createdAt: string;
  loading?: boolean;
}

export function PredictionResults({
  predictionId,
  modelType,
  title,
  description,
  results,
  createdAt,
  loading = false
}: PredictionResultsProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [viewMode, setViewMode] = useState<"table" | "chart">("table");
  const [originFilter, setOriginFilter] = useState<string | null>(null);
  const [destinationFilter, setDestinationFilter] = useState<string | null>(null);
  const [carrierFilter, setCarrierFilter] = useState<string | null>(null);
  const [chartType, setChartType] = useState<"bar" | "line">("bar");
  
  // Extract unique values for filters
  const origins = [...new Set(results.map(result => result.origin))].sort();
  const destinations = [...new Set(results.map(result => result.destination))].sort();
  const carriers = [...new Set(results.map(result => result.carrier).filter(Boolean))].sort();
  
  // Apply filters
  const filteredResults = results.filter(result => {
    const searchMatch = 
      result.origin.toLowerCase().includes(searchTerm.toLowerCase()) ||
      result.destination.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (result.carrier && result.carrier.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const originMatch = originFilter ? result.origin === originFilter : true;
    const destMatch = destinationFilter ? result.destination === destinationFilter : true;
    const carrierMatch = carrierFilter ? result.carrier === carrierFilter : true;
    
    return searchMatch && originMatch && destMatch && carrierMatch;
  });
  
  // Prepare chart data
  const prepareChartData = () => {
    if (modelType === "order-volume") {
      return filteredResults.map(result => ({
        name: `${result.origin}-${result.destination}`,
        value: result.value
      })).slice(0, 20); // Limit for readability
    }
    
    if (modelType === "tender-performance") {
      return filteredResults.map(result => ({
        name: result.carrier || "Unknown",
        value: result.value * 100 // Assuming value is a percentage in decimal form
      })).slice(0, 20);
    }
    
    if (modelType === "carrier-performance") {
      return filteredResults.map(result => ({
        name: result.carrier || "Unknown",
        value: result.value * 100 // Assuming value is a percentage in decimal form
      })).slice(0, 20);
    }
    
    return [];
  };
  
  const chartData = prepareChartData();
  
  // Format values according to model type
  const formatValue = (type: string, value: number) => {
    switch (type) {
      case "order-volume":
        return Math.round(value).toLocaleString();
      case "tender-performance":
      case "carrier-performance":
        return `${(value * 100).toFixed(1)}%`;
      default:
        return value.toString();
    }
  };
  
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return "text-neural-success";
    if (confidence >= 0.7) return "text-neural-warning";
    return "text-neural-error";
  };
  
  const handleDownload = () => {
    // Convert results to CSV
    const headers = ["Origin", "Destination", "Date", "Carrier", "Value", "Confidence"];
    const csvRows = [headers];
    
    filteredResults.forEach(result => {
      csvRows.push([
        result.origin,
        result.destination,
        result.date || "",
        result.carrier || "",
        result.value.toString(),
        result.confidence.toString()
      ]);
    });
    
    const csvContent = csvRows.map(row => row.join(",")).join("\n");
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${modelType}-prediction-${predictionId}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Loading results...</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-6 bg-muted rounded w-1/3"></div>
            <div className="h-6 bg-muted rounded w-1/4"></div>
            <div className="h-72 bg-muted rounded w-full"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-xl">{title}</CardTitle>
        {description && (
          <CardDescription>{description}</CardDescription>
        )}
        <p className="text-sm text-muted-foreground">
          Created: {createdAt} • {results.length} results
        </p>
      </CardHeader>
      <CardContent>
        <div className="mb-6 flex flex-wrap gap-4 md:flex-row">
          <div className="relative flex-grow">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search results..."
              className="pl-8 w-full"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          <div className="flex gap-2">
            <Button
              variant={viewMode === "table" ? "default" : "outline"}
              size="sm"
              onClick={() => setViewMode("table")}
            >
              Table
            </Button>
            <Button
              variant={viewMode === "chart" ? "default" : "outline"}
              size="sm"
              onClick={() => setViewMode("chart")}
            >
              Chart
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleDownload}
            >
              <Download className="h-4 w-4 mr-1" />
              Export
            </Button>
          </div>
        </div>
        
        <div className="mb-4 flex flex-wrap gap-2">
          <div className="flex items-center gap-2 min-w-[150px]">
            <span className="text-sm font-medium">Origin:</span>
            <Select value={originFilter || ""} onValueChange={(val) => setOriginFilter(val || null)}>
              <SelectTrigger className="h-8 text-xs">
                <SelectValue placeholder="All" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All</SelectItem>
                {origins.map(origin => (
                  <SelectItem key={origin} value={origin}>{origin}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div className="flex items-center gap-2 min-w-[150px]">
            <span className="text-sm font-medium">Dest:</span>
            <Select value={destinationFilter || ""} onValueChange={(val) => setDestinationFilter(val || null)}>
              <SelectTrigger className="h-8 text-xs">
                <SelectValue placeholder="All" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All</SelectItem>
                {destinations.map(destination => (
                  <SelectItem key={destination} value={destination}>{destination}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          {(modelType === "tender-performance" || modelType === "carrier-performance") && (
            <div className="flex items-center gap-2 min-w-[150px]">
              <span className="text-sm font-medium">Carrier:</span>
              <Select value={carrierFilter || ""} onValueChange={(val) => setCarrierFilter(val || null)}>
                <SelectTrigger className="h-8 text-xs">
                  <SelectValue placeholder="All" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All</SelectItem>
                  {carriers.map(carrier => carrier && (
                    <SelectItem key={carrier} value={carrier}>{carrier}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
          
          {viewMode === "chart" && (
            <div className="flex items-center gap-2 min-w-[150px] ml-auto">
              <span className="text-sm font-medium">Chart:</span>
              <Select value={chartType} onValueChange={(val) => setChartType(val as "bar" | "line")}>
                <SelectTrigger className="h-8 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="bar">Bar Chart</SelectItem>
                  <SelectItem value="line">Line Chart</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}
        </div>
        
        {filteredResults.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-8 text-center">
            <div className="rounded-full bg-muted p-4 mb-4">
              <Filter className="h-6 w-6 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-medium">No Results Found</h3>
            <p className="text-sm text-muted-foreground mt-1">
              Try adjusting your filters or search term
            </p>
          </div>
        ) : (
          <>
            {viewMode === "table" && (
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Origin</TableHead>
                      <TableHead>Destination</TableHead>
                      {(modelType === "tender-performance" || modelType === "carrier-performance") && (
                        <TableHead>Carrier</TableHead>
                      )}
                      {modelType === "order-volume" && (
                        <TableHead>Date</TableHead>
                      )}
                      <TableHead>Predicted {modelType === "order-volume" ? "Volume" : "Performance"}</TableHead>
                      <TableHead>Confidence</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredResults.map((result, index) => (
                      <TableRow key={index}>
                        <TableCell>{result.origin}</TableCell>
                        <TableCell>{result.destination}</TableCell>
                        {(modelType === "tender-performance" || modelType === "carrier-performance") && (
                          <TableCell>{result.carrier || "-"}</TableCell>
                        )}
                        {modelType === "order-volume" && (
                          <TableCell>{result.date || "-"}</TableCell>
                        )}
                        <TableCell className="font-medium">
                          {formatValue(modelType, result.value)}
                        </TableCell>
                        <TableCell>
                          <span className={getConfidenceColor(result.confidence)}>
                            {(result.confidence * 100).toFixed(0)}%
                          </span>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
            
            {viewMode === "chart" && (
              <div className="mt-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-base font-medium">
                    {modelType === "order-volume" ? "Predicted Volumes" : "Predicted Performance"}
                  </h3>
                  <Badge variant="outline" className="bg-muted">
                    Showing {filteredResults.length} results
                    {filteredResults.length > 20 && " (top 20 in chart)"}
                  </Badge>
                </div>
                <div className="h-[400px] w-full">
                  {chartType === "bar" ? (
                    <PredictionChart data={chartData} />
                  ) : (
                    <LineChart data={chartData} />
                  )}
                </div>
                {filteredResults.length > 20 && (
                  <p className="text-xs text-muted-foreground text-center mt-2">
                    * Chart showing top 20 results. Use table view or filters to see all data.
                  </p>
                )}
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
