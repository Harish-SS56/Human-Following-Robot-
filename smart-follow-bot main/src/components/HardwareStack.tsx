
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Cpu, Camera, Chrome, Palette, Hand, Server, Cog, Battery } from "lucide-react";

interface StackItemProps {
  title: string;
  description: string;
  icon: React.ReactNode;
}

function StackItem({ title, description, icon }: StackItemProps) {
  return (
    <div className="flex gap-3 items-start">
      <div className="p-2 rounded-md bg-primary/10 shrink-0">
        {icon}
      </div>
      <div>
        <h3 className="font-medium">{title}</h3>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
    </div>
  );
}

export function HardwareStack() {
  const stackItems = [
    {
      title: "Raspberry Pi 5",
      description: "AI model processing",
      icon: <Cpu className="h-5 w-5 text-primary" />
    },
    {
      title: "OpenCV",
      description: "Vision system",
      icon: <Camera className="h-5 w-5 text-primary" />
    },
    {
      title: "YOLOv8",
      description: "Person detection",
      icon: <Chrome className="h-5 w-5 text-primary" />
    },
    {
      title: "HSV Color Filtering",
      description: "Precise color-based tracking",
      icon: <Palette className="h-5 w-5 text-primary" />
    },
    {
      title: "MediaPipe",
      description: "Hand gesture detection",
      icon: <Hand className="h-5 w-5 text-primary" />
    },
    {
      title: "Flask + WebSockets",
      description: "Web interface and video streaming",
      icon: <Server className="h-5 w-5 text-primary" />
    },
    {
      title: "L298N + DC Motors",
      description: "Motor control",
      icon: <Cog className="h-5 w-5 text-primary" />
    },
    {
      title: "12V Li-ion Battery",
      description: "Power supply",
      icon: <Battery className="h-5 w-5 text-primary" />
    }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Hardware & Software Stack</CardTitle>
        <CardDescription>The technology powering our robot</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {stackItems.map((item, index) => (
            <StackItem
              key={index}
              title={item.title}
              description={item.description}
              icon={item.icon}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
