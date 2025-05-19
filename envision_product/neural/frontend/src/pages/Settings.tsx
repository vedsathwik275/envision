
import React from "react";
import { PageContainer, PageHeader, PageContent } from "@/components/layout/PageContainer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { toast } from "sonner";
import { Save } from "lucide-react";

const Settings = () => {
  const handleSaveSettings = () => {
    toast.success("Settings saved successfully");
  };

  return (
    <PageContainer>
      <PageHeader>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">
            Manage your account and application preferences
          </p>
        </div>
      </PageHeader>

      <PageContent>
        <Tabs defaultValue="general">
          <div className="flex flex-col space-y-8 lg:flex-row lg:space-x-12 lg:space-y-0">
            <div className="flex-1">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="general">General</TabsTrigger>
                <TabsTrigger value="api">API</TabsTrigger>
                <TabsTrigger value="notifications">Notifications</TabsTrigger>
              </TabsList>
              
              <TabsContent value="general" className="space-y-6 pt-6">
                <Card>
                  <CardHeader>
                    <CardTitle>General Settings</CardTitle>
                    <CardDescription>
                      Manage your account settings and preferences
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-4">
                      <h3 className="text-lg font-medium">Account Information</h3>
                      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                        <div className="space-y-2">
                          <Label htmlFor="display-name">Display Name</Label>
                          <Input id="display-name" placeholder="Jane Doe" />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="email">Email</Label>
                          <Input id="email" placeholder="jane.doe@example.com" type="email" disabled />
                        </div>
                      </div>
                    </div>
                    
                    <Separator />
                    
                    <div className="space-y-4">
                      <h3 className="text-lg font-medium">Application Theme</h3>
                      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                        <div className="space-y-2">
                          <Label htmlFor="theme">Theme Mode</Label>
                          <select
                            id="theme"
                            className="w-full rounded-md border border-input bg-background px-3 py-2"
                          >
                            <option value="light">Light</option>
                            <option value="dark">Dark</option>
                            <option value="system">System</option>
                          </select>
                        </div>
                      </div>
                    </div>
                    
                    <Separator />
                    
                    <div className="space-y-4">
                      <h3 className="text-lg font-medium">Data Display</h3>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <Label htmlFor="default-view-table">Default to Table View</Label>
                            <p className="text-sm text-muted-foreground">
                              Show results in table view by default
                            </p>
                          </div>
                          <Switch id="default-view-table" defaultChecked />
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <div>
                            <Label htmlFor="auto-refresh">Auto-refresh Data</Label>
                            <p className="text-sm text-muted-foreground">
                              Automatically refresh data every 5 minutes
                            </p>
                          </div>
                          <Switch id="auto-refresh" />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <div className="flex justify-end">
                  <Button onClick={handleSaveSettings}>
                    <Save className="mr-2 h-4 w-4" />
                    Save Settings
                  </Button>
                </div>
              </TabsContent>
              
              <TabsContent value="api" className="space-y-6 pt-6">
                <Card>
                  <CardHeader>
                    <CardTitle>API Access</CardTitle>
                    <CardDescription>
                      Manage API keys and access settings
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-4">
                      <h3 className="text-lg font-medium">API Keys</h3>
                      <div className="space-y-2">
                        <Label htmlFor="api-key">Your API Key</Label>
                        <div className="flex space-x-2">
                          <Input
                            id="api-key"
                            value="········································"
                            disabled
                            className="flex-1"
                          />
                          <Button variant="outline">Show</Button>
                          <Button variant="outline">Regenerate</Button>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          Use this key to authenticate API requests
                        </p>
                      </div>
                    </div>
                    
                    <Separator />
                    
                    <div className="space-y-4">
                      <h3 className="text-lg font-medium">API Access Control</h3>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <Label htmlFor="enable-api">Enable API Access</Label>
                            <p className="text-sm text-muted-foreground">
                              Allow external applications to access the API
                            </p>
                          </div>
                          <Switch id="enable-api" defaultChecked />
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <div>
                            <Label htmlFor="rate-limiting">Enforce Rate Limiting</Label>
                            <p className="text-sm text-muted-foreground">
                              Limit API requests to 100 per minute
                            </p>
                          </div>
                          <Switch id="rate-limiting" defaultChecked />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <div className="flex justify-end">
                  <Button onClick={handleSaveSettings}>
                    <Save className="mr-2 h-4 w-4" />
                    Save API Settings
                  </Button>
                </div>
              </TabsContent>
              
              <TabsContent value="notifications" className="space-y-6 pt-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Notification Settings</CardTitle>
                    <CardDescription>
                      Configure how you receive notifications
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-4">
                      <h3 className="text-lg font-medium">Email Notifications</h3>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <Label htmlFor="model-completion">Model Training Completion</Label>
                            <p className="text-sm text-muted-foreground">
                              Notify when model training is complete
                            </p>
                          </div>
                          <Switch id="model-completion" defaultChecked />
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <div>
                            <Label htmlFor="prediction-completion">Prediction Completion</Label>
                            <p className="text-sm text-muted-foreground">
                              Notify when predictions are generated
                            </p>
                          </div>
                          <Switch id="prediction-completion" defaultChecked />
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <div>
                            <Label htmlFor="system-updates">System Updates</Label>
                            <p className="text-sm text-muted-foreground">
                              Receive updates about system changes
                            </p>
                          </div>
                          <Switch id="system-updates" />
                        </div>
                      </div>
                    </div>
                    
                    <Separator />
                    
                    <div className="space-y-4">
                      <h3 className="text-lg font-medium">In-App Notifications</h3>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <Label htmlFor="show-notifications">Show Notifications</Label>
                            <p className="text-sm text-muted-foreground">
                              Display notifications in the application
                            </p>
                          </div>
                          <Switch id="show-notifications" defaultChecked />
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <div>
                            <Label htmlFor="notification-sound">Notification Sound</Label>
                            <p className="text-sm text-muted-foreground">
                              Play sound for important notifications
                            </p>
                          </div>
                          <Switch id="notification-sound" />
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <div className="flex justify-end">
                  <Button onClick={handleSaveSettings}>
                    <Save className="mr-2 h-4 w-4" />
                    Save Notification Settings
                  </Button>
                </div>
              </TabsContent>
            </div>
          </div>
        </Tabs>
      </PageContent>
    </PageContainer>
  );
};

export default Settings;
