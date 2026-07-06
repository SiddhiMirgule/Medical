"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  BarChart3,
  BookOpen,
  FlaskConical,
  Home,
  Menu,
  MessageSquare,
  Settings,
  X,
  Shield,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/lib/store";
import { ThemeToggle } from "@/components/ThemeToggle";

const navItems = [
  { href: "/", label: "Home", icon: Home },
  { href: "/ask", label: "Ask Question", icon: MessageSquare },
  { href: "/sources", label: "Sources", icon: BookOpen },
];

const adminItems = [
  { href: "/evaluation", label: "Evaluation", icon: Activity },
  { href: "/benchmark", label: "Benchmark", icon: BarChart3 },
  { href: "/admin", label: "Admin", icon: Settings },
];

export function Header() {
  const pathname = usePathname();
  const { sidebarOpen, toggleSidebar, setSidebarOpen } = useAppStore();

  return (
    <header className="sticky top-0 z-50 border-b border-border/40 bg-background/80 backdrop-blur-xl">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" className="lg:hidden" onClick={toggleSidebar}>
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-medical-blue to-medical-teal">
              <Shield className="h-4 w-4 text-white" />
            </div>
            <span className="text-lg font-bold">
              Med<span className="text-medical-teal">Verify</span> AI
            </span>
          </Link>
        </div>

        <nav className="hidden items-center gap-1 lg:flex">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent",
                pathname === item.href ? "text-medical-teal" : "text-muted-foreground"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          ))}
          <div className="mx-2 h-4 w-px bg-border" />
          {adminItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent",
                pathname === item.href ? "text-medical-teal" : "text-muted-foreground"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <ThemeToggle />
          <Button variant="medical" size="sm" asChild className="hidden sm:flex">
            <Link href="/ask">
              <FlaskConical className="h-4 w-4" />
              Ask Question
            </Link>
          </Button>
        </div>
      </div>

      {sidebarOpen && (
        <div className="border-t border-border lg:hidden">
          <nav className="container mx-auto space-y-1 px-4 py-4">
            {[...navItems, ...adminItems].map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setSidebarOpen(false)}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-colors hover:bg-accent",
                  pathname === item.href ? "bg-accent text-medical-teal" : "text-muted-foreground"
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}

export function Footer() {
  return (
    <footer className="border-t border-border/40 bg-muted/20">
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
          <p className="text-sm text-muted-foreground">
            MedVerify AI — Evidence-Grounded Medical Question Answering
          </p>
          <p className="text-xs text-muted-foreground">
            For research and educational purposes only. Not medical advice.
          </p>
        </div>
      </div>
    </footer>
  );
}
