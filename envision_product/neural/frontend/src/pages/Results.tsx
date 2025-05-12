
import React, { useState, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useModelStore, PredictionResult } from '@/store/modelStore';
import { ChartBar, Download, FileDown, Search } from 'lucide-react';
import { format } from 'date-fns';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from 'sonner';

const Results = () => {
  const [searchParams] = useSearchParams();
  const selectedResultId = searchParams.get('id');
  
  const { predictionResults } = useModelStore();
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<keyof PredictionResult['metrics']>('accuracy');
  
  // Find selected result if ID is provided
  const selectedResult = selectedResultId 
    ? predictionResults.find(r => r.id === selectedResultId) 
    : predictionResults[0];
  
  // Filter and sort results
  const filteredResults = useMemo(() => {
    return predictionResults
      .filter(result => {
        if (!search) return true;
        return result.modelName.toLowerCase().includes(search.toLowerCase());
      })
      .sort((a, b) => {
        return b.metrics[sortBy] - a.metrics[sortBy];
      });
  }, [predictionResults, search, sortBy]);
  
  const handleExportCSV = () => {
    if (!selectedResult) return;
    
    // Create CSV content
    const headers = ['Day', 'Actual', 'Predicted'];
    const rows = selectedResult.chartData.map(point => 
      [point.name, point.actual, point.predicted]
    );
    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');
    
    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `prediction-${selectedResult.id}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    toast.success('CSV file downloaded successfully');
  };
  
  if (predictionResults.length === 0) {
    return (
      <div className="max-w-3xl mx-auto">
        <h2 className="text-2xl font-bold mb-6">Results</h2>
        
        <Card>
          <CardContent className="py-16 text-center">
            <ChartBar className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-xl font-medium mb-4">No prediction results yet</h3>
            <p className="text-muted-foreground mb-6">
              Upload data and train a model to see prediction results
            </p>
            <Button asChild>
              <a href="/upload-data">Start a Prediction</a>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold">Results & Visualization</h2>
      
      {selectedResult && (
        <div className="space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h3 className="text-xl font-semibold">{selectedResult.modelName}</h3>
              <p className="text-muted-foreground">
                Created on {format(new Date(selectedResult.dateCreated), 'PPp')}
              </p>
            </div>
            <Button onClick={handleExportCSV}>
              <FileDown className="h-4 w-4 mr-2" />
              Export as CSV
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">Accuracy</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {(selectedResult.metrics.accuracy * 100).toFixed(2)}%
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">Precision</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {(selectedResult.metrics.precision * 100).toFixed(2)}%
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">Recall</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {(selectedResult.metrics.recall * 100).toFixed(2)}%
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">F1 Score</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {(selectedResult.metrics.f1Score * 100).toFixed(2)}%
                </div>
              </CardContent>
            </Card>
          </div>
          
          <Card>
            <CardHeader>
              <CardTitle>Prediction Visualization</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={selectedResult.chartData}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="actual" 
                      stroke="#1976d2" 
                      name="Actual Value"
                      strokeWidth={2}
                      dot={{ r: 4 }}
                      activeDot={{ r: 8 }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="predicted" 
                      stroke="#00acc1" 
                      name="Predicted Value"
                      strokeWidth={2}
                      dot={{ r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Prediction Data</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="rounded-md border data-grid">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Day</TableHead>
                      <TableHead>Actual Value</TableHead>
                      <TableHead>Predicted Value</TableHead>
                      <TableHead>Difference</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {selectedResult.chartData.map((point, i) => {
                      const difference = Math.abs(point.actual - point.predicted);
                      const percentDiff = ((difference / point.actual) * 100).toFixed(2);
                      
                      return (
                        <TableRow key={i}>
                          <TableCell>{point.name}</TableCell>
                          <TableCell>{point.actual}</TableCell>
                          <TableCell>{point.predicted}</TableCell>
                          <TableCell>
                            <span className={difference > 10 ? "text-neural-error" : "text-neural-accent"}>
                              {difference} ({percentDiff}%)
                            </span>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
      
      <div className="mt-10">
        <h3 className="text-xl font-semibold mb-4">All Predictions</h3>
        
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input 
              placeholder="Search predictions..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
            />
          </div>
          
          <Select value={sortBy} onValueChange={(value) => setSortBy(value as any)}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="accuracy">Accuracy</SelectItem>
              <SelectItem value="precision">Precision</SelectItem>
              <SelectItem value="recall">Recall</SelectItem>
              <SelectItem value="f1Score">F1 Score</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="rounded-md border data-grid">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Model</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Accuracy</TableHead>
                <TableHead>Precision</TableHead>
                <TableHead>Recall</TableHead>
                <TableHead>F1 Score</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredResults.map((result) => (
                <TableRow key={result.id}>
                  <TableCell className="font-medium">{result.modelName}</TableCell>
                  <TableCell>{format(new Date(result.dateCreated), 'PP')}</TableCell>
                  <TableCell>{(result.metrics.accuracy * 100).toFixed(2)}%</TableCell>
                  <TableCell>{(result.metrics.precision * 100).toFixed(2)}%</TableCell>
                  <TableCell>{(result.metrics.recall * 100).toFixed(2)}%</TableCell>
                  <TableCell>{(result.metrics.f1Score * 100).toFixed(2)}%</TableCell>
                  <TableCell className="text-right">
                    <Button variant="outline" size="sm" asChild>
                      <a href={`/results?id=${result.id}`}>View</a>
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  );
};

export default Results;
