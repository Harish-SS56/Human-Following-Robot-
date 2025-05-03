
import { HeroSection } from "@/components/HeroSection";
import { Header } from "@/components/Header";
import { FeatureCard } from "@/components/FeatureCard";
import { HardwareStack } from "@/components/HardwareStack";
import { Methodology } from "@/components/Methodology";
import { MathModel } from "@/components/MathModel";
import { 
  UserCheck, 
  Hand, 
  Gauge, 
  MonitorCheck, 
  AlertTriangle, 
  Scan 
} from "lucide-react";

const Index = () => {
  const features = [
    {
      title: "Autonomous Human Tracking",
      description: "Identifies and follows a specific person with precision and reliability.",
      icon: UserCheck
    },
    {
      title: "Gesture-Based Control",
      description: "Switch between follow/stop modes with simple hand gestures.",
      icon: Hand
    },
    {
      title: "Adaptive Speed Control",
      description: "Uses PID controller to maintain a stable distance from the target.",
      icon: Gauge
    },
    {
      title: "Remote Monitoring",
      description: "Live video feed and control capabilities from any web browser.",
      icon: MonitorCheck
    },
    {
      title: "Rerouting",
      description: "Alerts and rerouting using onboard  for safety.",
      icon: AlertTriangle
    },
    {
      title: "Tracking Recovery",
      description: "360° scan plus voice alerts when tracking is lost.",
      icon: Scan
    }
  ];

  return (
    <>
      <Header />
      <main className="flex flex-col gap-16 pb-16">
        <HeroSection />
        
        <section id="features" className="container">
          <h2 className="text-3xl font-bold tracking-tight mb-8 text-center">
            Advanced Features
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <FeatureCard 
                key={index} 
                title={feature.title} 
                description={feature.description} 
                icon={feature.icon} 
              />
            ))}
          </div>
        </section>
        
        <section id="hardware" className="container">
          <HardwareStack />
        </section>
        
        <section id="methodology" className="container">
          <Methodology />
        </section>
        
        <section id="math-model" className="container">
          <MathModel />
        </section>
      </main>
    </>
  );
};

export default Index;
