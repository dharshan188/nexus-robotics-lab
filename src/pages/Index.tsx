import { useState, useCallback } from "react";
import { toast } from "sonner";
import Navbar from "@/components/Navbar";
import SetupSidebar from "@/components/SetupSidebar";
import MainPanel from "@/components/MainPanel";
import OutputPanel, { type LogEntry } from "@/components/OutputPanel";
import ProgressBar from "@/components/ProgressBar";

const simulatedLogs: { message: string; type: LogEntry["type"]; step: number }[] = [
  { message: "Initializing workspace...", type: "info", step: 1 },
  { message: "Parsing robot description...", type: "info", step: 1 },
  { message: "Robot model generated successfully", type: "success", step: 1 },
  { message: "Generating URDF model...", type: "info", step: 2 },
  { message: "Building ROS2 workspace...", type: "info", step: 2 },
  { message: "Compiling packages (3/3)...", type: "info", step: 2 },
  { message: "Build completed with 0 errors", type: "success", step: 2 },
  { message: "Launching Gazebo Ignition...", type: "info", step: 3 },
  { message: "Loading world: custom_map.sdf", type: "info", step: 3 },
  { message: "Spawning robot entity...", type: "info", step: 3 },
  { message: "Simulation running at 1000Hz", type: "success", step: 3 },
  { message: "Running auto-debug analysis...", type: "info", step: 4 },
  { message: "Minor: TF tree has 2ms latency", type: "warning", step: 4 },
  { message: "All systems nominal", type: "success", step: 4 },
  { message: "Robot is operational ✓", type: "success", step: 5 },
];

const Index = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [systemStatus, setSystemStatus] = useState<"connected" | "running" | "error">("connected");
  const [buildStatus, setBuildStatus] = useState<"idle" | "running" | "success" | "error">("idle");
  const [simStatus, setSimStatus] = useState<"idle" | "running" | "success" | "error">("idle");
  const [debugStatus, setDebugStatus] = useState<"idle" | "running" | "success" | "error">("idle");

  const addLog = useCallback((message: string, type: LogEntry["type"]) => {
    const now = new Date();
    const timestamp = `${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}:${now.getSeconds().toString().padStart(2, "0")}`;
    setLogs((prev) => [...prev, { id: Date.now() + Math.random(), message, type, timestamp }]);
  }, []);

  const handleGenerate = useCallback(async (prompt: string) => {
    setIsGenerating(true);
    setLogs([]);
    setCurrentStep(0);
    setSystemStatus("running");
    setBuildStatus("idle");
    setSimStatus("idle");
    setDebugStatus("idle");

    toast("Generation started", { description: `Processing: "${prompt}"` });

    let prevStep = -1;
    for (let i = 0; i < simulatedLogs.length; i++) {
      const log = simulatedLogs[i];
      await new Promise((r) => setTimeout(r, 400 + Math.random() * 600));

      if (log.step !== prevStep) {
        setCurrentStep(log.step);
        prevStep = log.step;
        if (log.step === 2) setBuildStatus("running");
        if (log.step === 3) { setBuildStatus("success"); setSimStatus("running"); }
        if (log.step === 4) { setSimStatus("success"); setDebugStatus("running"); }
        if (log.step === 5) { setDebugStatus("success"); }
      }

      addLog(log.message, log.type);
    }

    setIsGenerating(false);
    setSystemStatus("connected");
    toast.success("Robot launched successfully!");
  }, [addLog]);

  const handleInitialize = () => {
    toast("Workspace initialized", { description: "Configuration saved successfully." });
  };

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden">
      <Navbar status={systemStatus} />
      <div className="flex flex-1 min-h-0">
        <SetupSidebar
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
          onInitialize={handleInitialize}
        />
        <MainPanel onGenerate={handleGenerate} isGenerating={isGenerating} />
        <OutputPanel logs={logs} buildStatus={buildStatus} simStatus={simStatus} debugStatus={debugStatus} />
      </div>
      <ProgressBar currentStep={currentStep} />
    </div>
  );
};

export default Index;
