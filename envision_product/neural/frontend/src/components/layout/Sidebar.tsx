
import React from "react";
import { Link, useLocation } from "react-router-dom";
import { 
  LayoutDashboard, 
  BarChart, 
  FileText, 
  Settings, 
  Server,
  Folder,
  Route,
  ChevronRight,
  ChevronDown,
  Loader
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { 
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar 
} from "@/components/ui/sidebar";

interface NavLinkProps {
  to: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  end?: boolean;
}

const NavLink = ({ to, icon, children, end = false }: NavLinkProps) => {
  const location = useLocation();
  const isActive = end ? location.pathname === to : location.pathname.startsWith(to);
  const { state } = useSidebar();
  
  // Check if sidebar is collapsed based on state
  const isCollapsed = state === "collapsed";

  return (
    <Link 
      to={to} 
      className={cn(
        "flex items-center space-x-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
        isActive 
          ? "bg-sidebar-accent text-sidebar-accent-foreground" 
          : "transparent hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground"
      )}
    >
      {icon}
      {!isCollapsed && <span>{children}</span>}
    </Link>
  );
};

export interface SidebarNavProps {
  className?: string;
}

export function MainSidebar({ className }: SidebarNavProps) {
  const { state } = useSidebar();
  const location = useLocation();
  
  // Check if sidebar is collapsed based on state
  const isCollapsed = state === "collapsed";
  
  // Check if the current path is within a section
  const isActiveSection = (path: string) => location.pathname.startsWith(path);
  
  // Model Management Section
  const isModelSection = isActiveSection("/models");
  
  // Data Management Section
  const isDataSection = isActiveSection("/data");
  
  // Predictions Section
  const isPredictionSection = isActiveSection("/predictions");
  
  // Lane Analysis Section
  const isLaneSection = isActiveSection("/lanes");

  return (
    <Sidebar
      className={cn(
        isCollapsed ? "w-16" : "w-64",
        "border-r transition-all duration-300 ease-in-out",
        className
      )}
    >
      <div className="flex h-16 items-center justify-center border-b px-4">
        {isCollapsed ? (
          <div className="h-8 w-8 rounded-md bg-neural-primary flex items-center justify-center text-white font-bold">
            EN
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-md bg-neural-primary flex items-center justify-center text-white font-bold">
              EN
            </div>
            <span className="text-lg font-semibold">Envision Neural</span>
          </div>
        )}
      </div>

      <SidebarContent className="p-2">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <NavLink to="/" icon={<LayoutDashboard size={20} />} end>
                Dashboard
              </NavLink>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>

        {/* Data Management */}
        <SidebarGroup>
          <div className="flex items-center justify-between px-3 py-2">
            {!isCollapsed && <SidebarGroupLabel>Data</SidebarGroupLabel>}
            {isCollapsed ? (
              <Folder size={20} className="mx-auto" />
            ) : (
              <ChevronRight size={16} className={cn("transition-transform", isDataSection && "rotate-90")} />
            )}
          </div>
          
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <NavLink to="/data/upload" icon={<FileText size={20} />}>
                    Upload & Preview
                  </NavLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Model Management */}
        <SidebarGroup>
          <div className="flex items-center justify-between px-3 py-2">
            {!isCollapsed && <SidebarGroupLabel>Models</SidebarGroupLabel>}
            {isCollapsed ? (
              <Server size={20} className="mx-auto" />
            ) : (
              <ChevronRight size={16} className={cn("transition-transform", isModelSection && "rotate-90")} />
            )}
          </div>
          
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <NavLink to="/models" icon={<BarChart size={20} />} end>
                    Model Overview
                  </NavLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <NavLink to="/models/order-volume" icon={<BarChart size={20} />}>
                    Order Volume
                  </NavLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <NavLink to="/models/tender-performance" icon={<BarChart size={20} />}>
                    Tender Performance
                  </NavLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <NavLink to="/models/carrier-performance" icon={<BarChart size={20} />}>
                    Carrier Performance
                  </NavLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Predictions */}
        <SidebarGroup>
          <div className="flex items-center justify-between px-3 py-2">
            {!isCollapsed && <SidebarGroupLabel>Predictions</SidebarGroupLabel>}
            {isCollapsed ? (
              <BarChart size={20} className="mx-auto" />
            ) : (
              <ChevronRight size={16} className={cn("transition-transform", isPredictionSection && "rotate-90")} />
            )}
          </div>
          
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <NavLink to="/predictions/order-volume" icon={<BarChart size={20} />}>
                    Order Volume
                  </NavLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <NavLink to="/predictions/tender-performance" icon={<BarChart size={20} />}>
                    Tender Performance
                  </NavLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <NavLink to="/predictions/carrier-performance" icon={<BarChart size={20} />}>
                    Carrier Performance
                  </NavLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Lane Analysis */}
        <SidebarGroup>
          <div className="flex items-center justify-between px-3 py-2">
            {!isCollapsed && <SidebarGroupLabel>Lane Analysis</SidebarGroupLabel>}
            {isCollapsed ? (
              <Route size={20} className="mx-auto" />
            ) : (
              <ChevronRight size={16} className={cn("transition-transform", isLaneSection && "rotate-90")} />
            )}
          </div>
          
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <NavLink to="/lanes" icon={<Route size={20} />}>
                    Lane Explorer
                  </NavLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <Separator className="my-2" />

        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <NavLink to="/settings" icon={<Settings size={20} />}>
                Settings
              </NavLink>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarContent>
    </Sidebar>
  );
}
