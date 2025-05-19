
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import { Layout } from "./components/layout/Layout";
import { AppProvider } from "./context/AppContext";

import Dashboard from "./pages/Dashboard";
import DataUpload from "./pages/DataUpload";
import Models from "./pages/Models";
import ModelDetail from "./pages/ModelDetail";
import ModelTraining from "./pages/ModelTraining";
import PredictionList from "./pages/PredictionList";
import PredictionGeneration from "./pages/PredictionGeneration";
import PredictionResults from "./pages/PredictionResults";
import LaneExplorer from "./pages/LaneExplorer";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";
import Index from "./pages/Index";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AppProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Layout><Index /></Layout>} />
            <Route path="/dashboard" element={<Layout><Dashboard /></Layout>} />
            
            {/* Data Routes */}
            <Route path="/data/upload" element={<Layout><DataUpload /></Layout>} />
            
            {/* Model Routes */}
            <Route path="/models" element={<Layout><Models /></Layout>} />
            <Route path="/models/train" element={<Layout><ModelTraining /></Layout>} />
            <Route path="/models/:modelType/:modelId" element={<Layout><ModelDetail /></Layout>} />
            
            {/* Prediction Routes */}
            <Route path="/predictions/:modelType" element={<Layout><PredictionList /></Layout>} />
            <Route path="/predictions/:modelType/new" element={<Layout><PredictionGeneration /></Layout>} />
            <Route path="/predictions/:modelType/:predictionId" element={<Layout><PredictionResults /></Layout>} />
            
            {/* Lane Analysis Routes */}
            <Route path="/lanes" element={<Layout><LaneExplorer /></Layout>} />
            
            {/* Settings */}
            <Route path="/settings" element={<Layout><Settings /></Layout>} />
            
            {/* Catch-all route */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AppProvider>
  </QueryClientProvider>
);

export default App;
