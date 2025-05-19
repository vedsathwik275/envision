
import React from "react";
import { PageContainer, PageHeader, PageContent } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/button";
import { useApp } from "@/context/AppContext";
import { ModelList } from "@/components/models/ModelList";
import { Link } from "react-router-dom";
import { Plus } from "lucide-react";

const Models = () => {
  const { models, loading } = useApp();

  return (
    <PageContainer>
      <PageHeader>
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Models</h1>
            <p className="text-muted-foreground">
              View, manage, and train your predictive models
            </p>
          </div>
          <div>
            <Button asChild>
              <Link to="/models/train">
                <Plus className="mr-2 h-4 w-4" />
                Train New Model
              </Link>
            </Button>
          </div>
        </div>
      </PageHeader>

      <PageContent>
        <ModelList models={models} loading={loading.models} />
      </PageContent>
    </PageContainer>
  );
};

export default Models;
