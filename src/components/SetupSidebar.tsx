import { ChevronDown, Zap, PanelLeftClose, PanelLeft } from "lucide-react";
import { useState } from "react";
import { Switch } from "@/components/ui/switch";

interface SetupSidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  onInitialize: () => void;
}

const SetupSidebar = ({ collapsed, onToggle, onInitialize }: SetupSidebarProps) => {
  const [rosVersion, setRosVersion] = useState("ros2");
  const [simEngine, setSimEngine] = useState("gazebo-ignition");
  const [autoDebug, setAutoDebug] = useState(true);
  const [enableLogs, setEnableLogs] = useState(true);

  if (collapsed) {
    return (
      <div className="w-12 glass-panel-strong border-r border-glass-border rounded-none flex flex-col items-center pt-4 shrink-0">
        <button onClick={onToggle} className="w-8 h-8 rounded-lg bg-secondary/50 border border-glass-border flex items-center justify-center text-muted-foreground hover:text-primary hover:border-primary/40 transition-all duration-300">
          <PanelLeft className="w-4 h-4" />
        </button>
      </div>
    );
  }

  return (
    <aside className="w-72 glass-panel-strong border-r border-glass-border rounded-none flex flex-col shrink-0 animate-fade-in">
      <div className="flex items-center justify-between p-4 border-b border-glass-border">
        <h2 className="text-sm font-semibold text-foreground tracking-wide uppercase">Setup Configuration</h2>
        <button onClick={onToggle} className="w-7 h-7 rounded-md bg-secondary/50 border border-glass-border flex items-center justify-center text-muted-foreground hover:text-primary transition-all duration-300">
          <PanelLeftClose className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="flex-1 p-4 space-y-5 overflow-y-auto scrollbar-thin">
        {/* ROS Version */}
        <div className="space-y-2">
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">ROS Version</label>
          <div className="relative">
            <select
              value={rosVersion}
              onChange={(e) => setRosVersion(e.target.value)}
              className="w-full appearance-none bg-secondary/50 border border-glass-border rounded-lg px-3 py-2.5 text-sm text-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all duration-300 cursor-pointer"
            >
              <option value="ros1">ROS1</option>
              <option value="ros2">ROS2</option>
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
          </div>
        </div>

        {/* Simulation Engine */}
        <div className="space-y-2">
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Simulation Engine</label>
          <div className="relative">
            <select
              value={simEngine}
              onChange={(e) => setSimEngine(e.target.value)}
              className="w-full appearance-none bg-secondary/50 border border-glass-border rounded-lg px-3 py-2.5 text-sm text-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 transition-all duration-300 cursor-pointer"
            >
              <option value="gazebo-classic">Gazebo Classic</option>
              <option value="gazebo-ignition">Gazebo Ignition</option>
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
          </div>
        </div>

        {/* Toggles */}
        <div className="space-y-4 pt-2">
          <div className="flex items-center justify-between">
            <label className="text-sm text-secondary-foreground">Enable Auto-Debug</label>
            <Switch checked={autoDebug} onCheckedChange={setAutoDebug} />
          </div>
          <div className="flex items-center justify-between">
            <label className="text-sm text-secondary-foreground">Enable Logs</label>
            <Switch checked={enableLogs} onCheckedChange={setEnableLogs} />
          </div>
        </div>

        {/* Initialize Button */}
        <button
          onClick={onInitialize}
          className="w-full mt-4 py-2.5 rounded-lg bg-primary/15 border border-primary/30 text-primary text-sm font-medium flex items-center justify-center gap-2 hover:bg-primary/25 hover:border-primary/50 hover:neon-glow transition-all duration-300 active:scale-[0.98]"
        >
          <Zap className="w-4 h-4" />
          Initialize Workspace
        </button>
      </div>
    </aside>
  );
};

export default SetupSidebar;
