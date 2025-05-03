
import { 
  Accordion, 
  AccordionContent, 
  AccordionItem, 
  AccordionTrigger 
} from "@/components/ui/accordion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function MathModel() {
  const models = [
    {
      id: "yolo",
      title: "YOLO Bounding Box",
      formula: "B = (x, y, w, h)",
      description: "Larger box = closer distance to person"
    },
    {
      id: "pid",
      title: "PID Controller",
      formula: "Error: e(t) = d_desired − d_current\nu(t) = K_p · e(t) + K_i ∫e(t)dt + K_d · de(t)/dt",
      description: "Ensures smooth speed adjustments"
    },
    {
      id: "kalman",
      title: "Kalman Filter",
      formula: "X_t = A · X_t−1 + B · U_t + W_t",
      description: "Stabilizes tracking by filtering noise"
    },
    {
      id: "admm",
      title: "ADMM Optimization",
      formula: "Minimize f(x) + g(z)\nsubject to Ax + Bz = c",
      description: "Smoothens motion and reduces jerk"
    }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Mathematical Model & Algorithms</CardTitle>
        <CardDescription>The mathematics behind precise tracking</CardDescription>
      </CardHeader>
      <CardContent>
        <Accordion type="single" collapsible className="w-full">
          {models.map((model) => (
            <AccordionItem key={model.id} value={model.id}>
              <AccordionTrigger className="text-left font-medium">
                {model.title}
              </AccordionTrigger>
              <AccordionContent>
                <div className="p-4 bg-muted/50 rounded-md mb-2">
                  <pre className="formula text-sm whitespace-pre-line">{model.formula}</pre>
                </div>
                <p className="text-sm text-muted-foreground">{model.description}</p>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </CardContent>
    </Card>
  );
}
