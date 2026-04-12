import { Settings, Wifi, Activity } from "lucide-react";
import { useState } from "react";

type SystemStatus = "connected" | "running" | "error";

const statusConfig: Record<SystemStatus, { label: string; dotClass: string; color: string }> = {
  connected: { label: "Connected", dotClass: "status-dot-success", color: "text-success" },
  running: { label: "Running", dotClass: "status-dot-warning", color: "text-warning" },
  error: { label: "Error", dotClass: "status-dot-error", color: "text-destructive" },
};

interface NavbarProps {
  status: SystemStatus;
}

const Navbar = ({ status }: NavbarProps) => {
  const { label, dotClass, color } = statusConfig[status];

  return (
    <nav className="h-14 glass-panel-strong border-b border-glass-border rounded-none flex items-center justify-between px-6 z-50 relative">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-primary/20 border border-primary/30 flex items-center justify-center neon-glow">
          <Activity className="w-4 h-4 text-primary" />
        </div>
        <h1 className="text-base font-semibold tracking-tight">
          <span className="text-primary neon-text">Autonomous</span>{" "}
          <span className="text-foreground">Robotics Copilot</span>
        </h1>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 glass-panel px-3 py-1.5 rounded-full">
          <div className={dotClass} />
          <span className={`text-xs font-medium ${color}`}>{label}</span>
        </div>
        <button className="w-8 h-8 rounded-lg bg-secondary/50 border border-glass-border flex items-center justify-center text-muted-foreground hover:text-primary hover:border-primary/40 transition-all duration-300">
          <Settings className="w-4 h-4" />
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
