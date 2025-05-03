
import { Header } from "@/components/Header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { 
  Play, 
  Pause, 
  RefreshCw, 
  ChevronUp, 
  ChevronDown, 
  ChevronLeft, 
  ChevronRight,
  Video,
  Settings,
  AlertCircle,
  Thermometer
} from "lucide-react";
import { useState } from "react";

const Control = () => {
  const [isFollowing, setIsFollowing] = useState(false);
  const [speed, setSpeed] = useState([50]);
  const [distance, setDistance] = useState([100]);
  
  return (
    <>
      <Header />
      <main className="container py-8">
        <div className="flex flex-col gap-8">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold tracking-tight">Control Panel</h1>
            <div className="flex items-center gap-2">
              <div className="flex h-2 w-2 rounded-full bg-green-500"></div>
              <span className="text-sm text-muted-foreground">Robot Connected</span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main video feed */}
            <Card className="lg:col-span-2">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Video className="h-5 w-5" />
                    Live Video Feed
                  </CardTitle>
                  <Button variant="outline" size="sm">
                    Fullscreen
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="aspect-video bg-muted rounded-md flex items-center justify-center">
                  <p className="text-muted-foreground">Video stream unavailable</p>
                </div>
                
                <div className="mt-4 flex flex-wrap gap-2">
                  <Button 
                    variant={isFollowing ? "default" : "outline"}
                    className="flex items-center gap-2"
                    onClick={() => setIsFollowing(!isFollowing)}
                  >
                    {isFollowing ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                    {isFollowing ? "Stop Following" : "Start Following"}
                  </Button>
                  <Button variant="outline" className="flex items-center gap-2">
                    <Refresh className="h-4 w-4" />
                    Reset Tracking
                  </Button>
                </div>
              </CardContent>
            </Card>
            
            {/* Control panel */}
            <div className="flex flex-col gap-6">
              {/* Manual controls */}
              <Card>
                <CardHeader>
                  <CardTitle>Manual Control</CardTitle>
                  <CardDescription>Override autonomous following</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-3 gap-2 mb-4">
                    <div className="col-start-2">
                      <Button variant="outline" className="w-full" aria-label="Forward">
                        <ChevronUp className="h-5 w-5" />
                      </Button>
                    </div>
                    <div className="col-start-1">
                      <Button variant="outline" className="w-full" aria-label="Left">
                        <ChevronLeft className="h-5 w-5" />
                      </Button>
                    </div>
                    <div className="col-start-2">
                      <Button variant="outline" className="w-full" aria-label="Backward">
                        <ChevronDown className="h-5 w-5" />
                      </Button>
                    </div>
                    <div className="col-start-3">
                      <Button variant="outline" className="w-full" aria-label="Right">
                        <ChevronRight className="h-5 w-5" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              {/* Settings */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="h-5 w-5" />
                    Settings
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="speed">Speed (%)</Label>
                      <span className="text-sm font-medium">{speed}%</span>
                    </div>
                    <Slider
                      id="speed"
                      min={0}
                      max={100}
                      step={1}
                      value={speed}
                      onValueChange={setSpeed}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="distance">Follow Distance (cm)</Label>
                      <span className="text-sm font-medium">{distance} cm</span>
                    </div>
                    <Slider
                      id="distance"
                      min={50}
                      max={200}
                      step={5}
                      value={distance}
                      onValueChange={setDistance}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between space-x-2">
                    <Label htmlFor="obstacle-avoidance">Obstacle Avoidance</Label>
                    <Switch id="obstacle-avoidance" defaultChecked />
                  </div>
                  
                  <div className="flex items-center justify-between space-x-2">
                    <Label htmlFor="audio-alerts">Audio Alerts</Label>
                    <Switch id="audio-alerts" defaultChecked />
                  </div>
                </CardContent>
              </Card>
              
              {/* Status */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertCircle className="h-5 w-5" />
                    System Status
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Battery Level</span>
                      <span className="text-sm font-medium">87%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-1 text-sm">
                        <Thermometer className="h-3 w-3" />
                        CPU Temperature
                      </span>
                      <span className="text-sm font-medium">42°C</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Signal Strength</span>
                      <span className="text-sm font-medium">Good</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </>
  );
};

export default Control;
