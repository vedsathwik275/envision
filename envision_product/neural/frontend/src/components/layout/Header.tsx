
import React from "react";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";
import { useLocation } from "react-router-dom";

const pageTitles: Record<string, string> = {
  "/": "Dashboard",
  "/data/upload": "Data Upload & Preview",
  "/models": "Model Overview",
  "/models/order-volume": "Order Volume Models",
  "/models/tender-performance": "Tender Performance Models",
  "/models/carrier-performance": "Carrier Performance Models",
  "/predictions/order-volume": "Order Volume Predictions",
  "/predictions/tender-performance": "Tender Performance Predictions",
  "/predictions/carrier-performance": "Carrier Performance Predictions",
  "/lanes": "Lane Explorer",
  "/settings": "Settings"
};

export function Header() {
  const location = useLocation();
  const pageTitle = pageTitles[location.pathname] || "Envision Neural";
  
  // Generate breadcrumbs from path
  const pathSegments = location.pathname.split('/').filter(Boolean);
  const breadcrumbs = pathSegments.map((segment, index) => {
    const displayText = segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' ');
    return {
      text: displayText,
      path: '/' + pathSegments.slice(0, index + 1).join('/')
    };
  });

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b bg-background px-4">
      <div className="flex items-center gap-4">
        <SidebarTrigger />
        <div>
          <h1 className="text-xl font-semibold">{pageTitle}</h1>
          {breadcrumbs.length > 0 && (
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <span className="cursor-pointer hover:text-foreground" onClick={() => window.location.href = "/"}>
                Home
              </span>
              {breadcrumbs.map((crumb, i) => (
                <React.Fragment key={i}>
                  <span className="mx-1">/</span>
                  <span 
                    className="cursor-pointer hover:text-foreground"
                    onClick={() => window.location.href = crumb.path}
                  >
                    {crumb.text}
                  </span>
                </React.Fragment>
              ))}
            </div>
          )}
        </div>
      </div>
      <div className="flex items-center gap-2">
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <input
            type="search"
            placeholder="Search..."
            className="h-9 w-[200px] rounded-md border border-input bg-background pl-8 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <Button size="sm" variant="outline">Help</Button>
      </div>
    </header>
  );
}
