
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ThemeToggle";

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur">
      <div className="container flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
        </Link>
        
        <div className="flex items-center gap-4">
          <ThemeToggle />
          <Button asChild>
            <Link to="/control">Go to Control Panel</Link>
          </Button>
        </div>
      </div>
    </header>
  );
}
