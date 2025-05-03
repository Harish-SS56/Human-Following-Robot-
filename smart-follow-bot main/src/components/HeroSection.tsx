
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

export function HeroSection() {
  return (
    <section className="relative overflow-hidden">
      <div className="tech-pattern absolute inset-0 opacity-50 dark:opacity-30"></div>
      <div className="hero-gradient absolute inset-0 opacity-30 dark:opacity-40"></div>
      
      <div className="container relative z-10 py-24 md:py-32 flex flex-col items-center text-center">
        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-robot-blue to-robot-teal dark:from-primary dark:to-secondary">
          Human Following Robot
        </h1>
        
        <p className="text-xl md:text-2xl max-w-2xl text-muted-foreground mb-10">
          Smart Tracking. Smooth Navigation. Real-Time Control.
        </p>
        
        <div className="float max-w-xs md:max-w-sm mb-10">
  <img 
    src="/images/robot.jpg" 
    alt="Abstract robot illustration" 
    className="w-full h-auto"
  />
</div>

        
        <Button asChild size="lg" className="group">
  <a href="http://127.0.0.1:5000/" className="flex items-center gap-2" target="_blank" rel="noopener noreferrer">
    Go to Control Panel
    <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
  </a>
</Button>

      </div>
    </section>
  );
}
