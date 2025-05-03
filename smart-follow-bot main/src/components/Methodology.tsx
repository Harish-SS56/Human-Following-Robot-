
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Video, EyeIcon, Navigation, HandIcon, Tv, Volume2 } from "lucide-react";

export function Methodology() {
  const steps = [
    {
      title: "Video Capture",
      description: "Live webcam feed",
      icon: <Video className="h-5 w-5 text-white" />
    },
    {
      title: "Detection & Tracking",
      description: "YOLOv8 + HSV filtering",
      icon: <EyeIcon className="h-5 w-5 text-white" />
    },
    {
      title: "Motion Planning",
      description: "PID + ADMM for smooth motion",
      icon: <Navigation className="h-5 w-5 text-white" />
    },
    {
      title: "Gesture Input",
      description: "MediaPipe hand detection",
      icon: <HandIcon className="h-5 w-5 text-white" />
    },
    {
      title: "Live Streaming",
      description: "Flask server for remote access",
      icon: <Tv className="h-5 w-5 text-white" />
    },
    {
      title: "Alerts",
      description: "Speaker triggers for events",
      icon: <Volume2 className="h-5 w-5 text-white" />
    }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>How It Works</CardTitle>
        <CardDescription>From detection to movement in 6 steps</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col md:flex-row gap-4 md:gap-0 justify-between relative">
          {/* Timeline connector */}
          <div className="hidden md:block absolute top-6 left-8 right-8 h-0.5 bg-muted"></div>
          
          {steps.map((step, index) => (
            <div key={index} className="relative flex flex-col items-center text-center max-w-[160px] mx-auto">
              <div className="z-10 flex items-center justify-center w-12 h-12 rounded-full bg-primary mb-2">
                {step.icon}
              </div>
              <h3 className="font-medium text-sm">{step.title}</h3>
              <p className="text-xs text-muted-foreground">{step.description}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
