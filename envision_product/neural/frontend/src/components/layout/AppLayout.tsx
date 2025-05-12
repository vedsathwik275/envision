
import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { ChartLine, FileUp, LayoutDashboard, ChartBar } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Sidebar, SidebarContent, SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarTrigger, useSidebar } from "@/components/ui/sidebar";

const navigationItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Upload Data', path: '/upload-data', icon: FileUp },
  { name: 'Model Training', path: '/model-training', icon: ChartLine },
  { name: 'Results', path: '/results', icon: ChartBar }
];

export default function AppLayout() {
  const { state } = useSidebar();
  const isCollapsed = state === "collapsed";

  return (
    <div className="min-h-screen flex w-full">
      <Sidebar className={isCollapsed ? "w-14" : "w-64"} collapsible="icon">
        <div className="flex flex-col h-full">
          <div className="p-4 flex items-center justify-between">
            {!isCollapsed && <span className="text-xl font-semibold text-neural-primary">Envision</span>}
            <SidebarTrigger className={isCollapsed ? "mx-auto" : ""} />
          </div>
          
          <SidebarContent>
            <SidebarGroup>
              <SidebarGroupLabel>Navigation</SidebarGroupLabel>
              
              <SidebarGroupContent>
                <SidebarMenu>
                  {navigationItems.map(item => (
                    <SidebarMenuItem key={item.name}>
                      <SidebarMenuButton asChild>
                        <NavLink 
                          to={item.path} 
                          end={item.path === '/'} 
                          className={({isActive}) => cn(
                            "flex items-center py-2 px-3 rounded-md w-full",
                            isActive ? "bg-accent text-neural-primary font-medium" : "hover:bg-muted/50"
                          )}
                        >
                          <item.icon className="h-5 w-5" />
                          {!isCollapsed && <span className="ml-3">{item.name}</span>}
                        </NavLink>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>
        </div>
      </Sidebar>
      
      <div className="flex-1 flex flex-col">
        <header className="border-b py-4 px-6">
          <h1 className="text-xl font-semibold">Prediction Platform</h1>
        </header>
        <main className="flex-1 p-6 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
