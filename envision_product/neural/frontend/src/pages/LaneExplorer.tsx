import React, { useState } from "react";
import { PageContainer, PageHeader, PageContent } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/button";
import { LaneExplorer as LaneExplorerComponent } from "@/components/lanes/LaneExplorer";
import { useApp } from "@/context/AppContext";
import { laneApi } from "@/services/api";
import { Map, Search } from "lucide-react";
import { Link } from "react-router-dom";
import { toast } from "sonner";

// This should match the interface in components/lanes/LaneExplorer.tsx
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

const LaneExplorer = () => {
  const { locations } = useApp();
  const [isLoading, setIsLoading] = useState(false);
  
  const handleLaneSearch = async (origin: string, destination: string): Promise<LaneDetail> => {
    setIsLoading(true);
    
    try {
      // Use the real API to get lane details
      const response = await laneApi.getLaneDetails(origin, destination);
      setIsLoading(false);
      
      // Extract data from the response and ensure it matches the required LaneDetail interface
      // Our axios interceptor already extracts the data property from the response
      const data = response as any;
      
      const laneDetail: LaneDetail = {
        origin,
        destination,
        distance: data?.distance || 0,
        avgVolume: data?.avgVolume || 0,
        carrierPerformance: Array.isArray(data?.carrierPerformance) ? 
          data.carrierPerformance.map((carrier: any) => ({
            carrierId: carrier.carrierId || '',
            carrierName: carrier.carrierName || '',
            onTimePerformance: Number(carrier.onTimePerformance) || 0,
            tenderAcceptance: Number(carrier.tenderAcceptance) || 0,
            avgTransitTime: Number(carrier.avgTransitTime) || 0,
            costPerMile: carrier.costPerMile !== undefined ? Number(carrier.costPerMile) : undefined
          })) : []
      };
      
      return laneDetail;
    } catch (error: any) {
      console.error("Error fetching lane details:", error);
      setIsLoading(false);
      
      toast.error("Failed to fetch lane details", {
        description: error.message || "There was an error loading lane information."
      });
      
      // Return a basic lane object with default values to match the interface
      return {
        origin,
        destination,
        distance: 0,
        avgVolume: 0,
        carrierPerformance: []
      };
    }
  };

  return (
    <PageContainer>
      <PageHeader>
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Lane Explorer</h1>
            <p className="text-muted-foreground">
              Analyze carrier performance across specific lanes
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" asChild>
              <Link to="/predictions/order-volume/new">
                <Search className="mr-2 h-4 w-4" />
                New Prediction
              </Link>
            </Button>
          </div>
        </div>
      </PageHeader>

      <PageContent>
        <LaneExplorerComponent 
          origins={locations}
          destinations={locations}
          onSearch={handleLaneSearch}
          loading={isLoading}
        />
      </PageContent>
    </PageContainer>
  );
};

export default LaneExplorer;
