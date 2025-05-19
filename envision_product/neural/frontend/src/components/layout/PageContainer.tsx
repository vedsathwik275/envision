
import React from "react";
import { cn } from "@/lib/utils";

interface PageContainerProps {
  children: React.ReactNode;
  className?: string;
}

export function PageContainer({ children, className }: PageContainerProps) {
  return (
    <div className={cn("container mx-auto p-4 md:p-6 animate-fade-in", className)}>
      {children}
    </div>
  );
}

export function PageHeader({ children, className }: PageContainerProps) {
  return (
    <div className={cn("mb-6", className)}>
      {children}
    </div>
  );
}

export function PageContent({ children, className }: PageContainerProps) {
  return (
    <div className={cn("space-y-6", className)}>
      {children}
    </div>
  );
}
