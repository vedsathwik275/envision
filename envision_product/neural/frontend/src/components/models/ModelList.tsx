
import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Link } from "react-router-dom";
import { ArrowUpDown, Search, Filter, ArrowRight } from "lucide-react";

interface Model {
  id: string;
  name: string;
  type: "order-volume" | "tender-performance" | "carrier-performance";
  accuracy: number;
  status: "active" | "training" | "failed";
  createdAt: string;
  lastUpdated: string;
}

interface ModelListProps {
  models: Model[];
  loading?: boolean;
}

export function ModelList({ models, loading = false }: ModelListProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [sortField, setSortField] = useState<keyof Model>("lastUpdated");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");
  const [typeFilter, setTypeFilter] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  
  const handleSort = (field: keyof Model) => {
    if (field === sortField) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
  };
  
  const sortedModels = [...models].sort((a, b) => {
    if (a[sortField] < b[sortField]) return sortDirection === "asc" ? -1 : 1;
    if (a[sortField] > b[sortField]) return sortDirection === "asc" ? 1 : -1;
    return 0;
  });
  
  const filteredModels = sortedModels.filter((model) => {
    const searchMatch = model.name.toLowerCase().includes(searchTerm.toLowerCase());
    const typeMatch = typeFilter ? model.type === typeFilter : true;
    const statusMatch = statusFilter ? model.status === statusFilter : true;
    return searchMatch && typeMatch && statusMatch;
  });
  
  const modelTypeLabels: Record<string, string> = {
    "order-volume": "Order Volume",
    "tender-performance": "Tender Performance",
    "carrier-performance": "Carrier Performance"
  };
  
  const statusColors: Record<string, string> = {
    active: "bg-neural-success text-white",
    training: "bg-neural-warning text-neural-dark",
    failed: "bg-neural-error text-white"
  };
  
  const statusLabels: Record<string, string> = {
    active: "Active",
    training: "Training",
    failed: "Failed"
  };
  
  const getAccuracyColor = (acc: number) => {
    if (acc >= 90) return "text-neural-success";
    if (acc >= 70) return "text-neural-warning";
    return "text-neural-error";
  };
  
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Loading models...</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-10 bg-muted rounded"></div>
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, index) => (
                <div key={index} className="h-16 bg-muted rounded"></div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-col space-y-4 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
        <CardTitle>Models</CardTitle>
        <div className="flex flex-col space-y-2 sm:flex-row sm:space-x-2 sm:space-y-0">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search models..."
              className="pl-8 w-full sm:w-[200px]"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <Button variant="outline" className="sm:w-auto w-full" asChild>
            <Link to="/models/train">
              Train New Model
            </Link>
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="mb-4 flex flex-wrap gap-2">
          <Badge
            variant={typeFilter === null ? "default" : "outline"}
            className="cursor-pointer hover:bg-primary/90"
            onClick={() => setTypeFilter(null)}
          >
            All Types
          </Badge>
          {Object.entries(modelTypeLabels).map(([type, label]) => (
            <Badge
              key={type}
              variant={typeFilter === type ? "default" : "outline"}
              className="cursor-pointer hover:bg-primary/90"
              onClick={() => setTypeFilter(type === typeFilter ? null : type)}
            >
              {label}
            </Badge>
          ))}
          
          <div className="ml-auto"></div>
          
          <Badge
            variant={statusFilter === null ? "default" : "outline"}
            className="cursor-pointer hover:bg-primary/90"
            onClick={() => setStatusFilter(null)}
          >
            All Status
          </Badge>
          {Object.entries(statusLabels).map(([status, label]) => (
            <Badge
              key={status}
              variant={statusFilter === status ? "default" : "outline"}
              className="cursor-pointer hover:bg-primary/90"
              onClick={() => setStatusFilter(status === statusFilter ? null : status)}
            >
              {label}
            </Badge>
          ))}
        </div>
        
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead 
                  className="cursor-pointer"
                  onClick={() => handleSort("name")}
                >
                  <div className="flex items-center">
                    Name
                    {sortField === "name" && (
                      <ArrowUpDown className="ml-2 h-4 w-4" />
                    )}
                  </div>
                </TableHead>
                <TableHead 
                  className="cursor-pointer"
                  onClick={() => handleSort("type")}
                >
                  <div className="flex items-center">
                    Type
                    {sortField === "type" && (
                      <ArrowUpDown className="ml-2 h-4 w-4" />
                    )}
                  </div>
                </TableHead>
                <TableHead 
                  className="cursor-pointer"
                  onClick={() => handleSort("accuracy")}
                >
                  <div className="flex items-center">
                    Accuracy
                    {sortField === "accuracy" && (
                      <ArrowUpDown className="ml-2 h-4 w-4" />
                    )}
                  </div>
                </TableHead>
                <TableHead 
                  className="cursor-pointer"
                  onClick={() => handleSort("status")}
                >
                  <div className="flex items-center">
                    Status
                    {sortField === "status" && (
                      <ArrowUpDown className="ml-2 h-4 w-4" />
                    )}
                  </div>
                </TableHead>
                <TableHead 
                  className="cursor-pointer"
                  onClick={() => handleSort("lastUpdated")}
                >
                  <div className="flex items-center">
                    Last Updated
                    {sortField === "lastUpdated" && (
                      <ArrowUpDown className="ml-2 h-4 w-4" />
                    )}
                  </div>
                </TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredModels.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                    No models found
                  </TableCell>
                </TableRow>
              ) : (
                filteredModels.map((model) => (
                  <TableRow key={model.id}>
                    <TableCell className="font-medium">{model.name}</TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {modelTypeLabels[model.type]}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <span className={getAccuracyColor(model.accuracy)}>
                        {model.accuracy}%
                      </span>
                    </TableCell>
                    <TableCell>
                      <Badge className={statusColors[model.status]}>
                        {statusLabels[model.status]}
                      </Badge>
                    </TableCell>
                    <TableCell>{model.lastUpdated}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Button variant="ghost" size="sm" asChild>
                          <Link to={`/models/${model.type}/${model.id}`}>
                            Details
                          </Link>
                        </Button>
                        <Button variant="outline" size="sm" asChild>
                          <Link to={`/predictions/${model.type}/new?model=${model.id}`}>
                            Predict
                            <ArrowRight className="ml-1 h-3 w-3" />
                          </Link>
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
