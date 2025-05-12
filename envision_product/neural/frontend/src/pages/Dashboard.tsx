
import React from 'react';
import { Link } from 'react-router-dom';
import { FileUp, ChartLine, ChartBar } from 'lucide-react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useModelStore } from '@/store/modelStore';
import { format } from 'date-fns';

const Dashboard = () => {
  const {
    models,
    predictionResults
  } = useModelStore();
  
  const recentResults = predictionResults.slice(0, 3);
  
  return (
    <div className="space-y-8">
      <section className="space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold">Envision</h2>
            <p className="text-muted-foreground mt-1">Training Platform</p>
          </div>
          <Button size="lg" asChild>
            <Link to="/upload-data">Start New Prediction</Link>
          </Button>
        </div>
        
        <Card className="bg-gradient-to-r from-neural-primary/10 to-neural-secondary/10 border-none">
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Link to="/upload-data" className="block">
                <div className="bg-white rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center mb-4">
                    <div className="p-3 rounded-full bg-neural-primary/10 text-neural-primary">
                      <FileUp className="h-6 w-6" />
                    </div>
                    <h3 className="ml-4 font-semibold text-lg">Upload Data</h3>
                  </div>
                  <p className="text-muted-foreground text-sm">
                    Upload your CSV dataset for model training and prediction
                  </p>
                </div>
              </Link>
              
              <Link to="/model-training" className="block">
                <div className="bg-white rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center mb-4">
                    <div className="p-3 rounded-full bg-neural-secondary/10 text-neural-secondary">
                      <ChartLine className="h-6 w-6" />
                    </div>
                    <h3 className="ml-4 font-semibold text-lg">Train Model</h3>
                  </div>
                  <p className="text-muted-foreground text-sm">
                    Train machine learning models with your data
                  </p>
                </div>
              </Link>
              
              <Link to="/results" className="block">
                <div className="bg-white rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center mb-4">
                    <div className="p-3 rounded-full bg-neural-accent/10 text-neural-accent">
                      <ChartBar className="h-6 w-6" />
                    </div>
                    <h3 className="ml-4 font-semibold text-lg">View Results</h3>
                  </div>
                  <p className="text-muted-foreground text-sm">
                    Analyze and export your prediction results
                  </p>
                </div>
              </Link>
            </div>
          </CardContent>
        </Card>
      </section>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <section>
          <h3 className="text-xl font-semibold mb-4">Available Models</h3>
          {models.map(model => (
            <Card key={model.id} className="mb-4">
              <CardHeader>
                <CardTitle>{model.name}</CardTitle>
                <CardDescription>{model.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-muted-foreground">Last Trained:</span>
                    <p>{model.lastTrained ? format(new Date(model.lastTrained), 'PPpp') : 'Never'}</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Accuracy:</span>
                    <p>{model.accuracy ? `${(model.accuracy * 100).toFixed(2)}%` : 'N/A'}</p>
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button variant="outline" asChild>
                  <Link to={`/model-training?id=${model.id}`}>Train Model</Link>
                </Button>
              </CardFooter>
            </Card>
          ))}
        </section>
        
        <section>
          <h3 className="text-xl font-semibold mb-4">Recent Predictions</h3>
          
          {recentResults.length > 0 ? (
            recentResults.map(result => (
              <Card key={result.id} className="mb-4">
                <CardHeader>
                  <CardTitle>{result.modelName}</CardTitle>
                  <CardDescription>
                    Created on {format(new Date(result.dateCreated), 'PPp')}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-muted-foreground">Accuracy:</span>
                      <p>{`${(result.metrics.accuracy * 100).toFixed(2)}%`}</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">F1 Score:</span>
                      <p>{`${(result.metrics.f1Score * 100).toFixed(2)}%`}</p>
                    </div>
                  </div>
                </CardContent>
                <CardFooter>
                  <Button variant="outline" asChild className="w-full">
                    <Link to={`/results?id=${result.id}`}>View Details</Link>
                  </Button>
                </CardFooter>
              </Card>
            ))
          ) : (
            <Card>
              <CardContent className="py-8 text-center">
                <p className="text-muted-foreground">No predictions yet</p>
                <Button variant="outline" className="mt-4" asChild>
                  <Link to="/upload-data">Create your first prediction</Link>
                </Button>
              </CardContent>
            </Card>
          )}
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
