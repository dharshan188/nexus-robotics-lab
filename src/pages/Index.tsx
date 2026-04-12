import { useState, useCallback } from "react";
import { toast } from "sonner";
import Navbar from "@/components/Navbar";
import SetupSidebar from "@/components/SetupSidebar";
import MainPanel from "@/components/MainPanel";
import OutputPanel, { type LogEntry } from "@/components/OutputPanel";
import ProgressBar from "@/components/ProgressBar";

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
    addLog("Sending generation request to backend...", "info");
    console.log("Sending:", prompt);

    try {
      setCurrentStep(1);
      setBuildStatus("running");

      const response = await fetch("http://127.0.0.1:8000/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt }),
      });

      const data = await response.json();
      console.log("Response:", data);

      if (!response.ok) {
        throw new Error(data?.detail || "Failed to generate robot");
      }

      setCurrentStep(5);
      setBuildStatus("success");
      setSimStatus("success");
      setDebugStatus("success");
      setSystemStatus("connected");
      addLog("Gazebo launched", "success");
      toast.success("Gazebo launched");
    } catch (error) {
      console.error("API error:", error);
      const message = error instanceof Error ? error.message : "Unexpected API error";
      setBuildStatus("error");
      setSimStatus("error");
      setDebugStatus("error");
      setSystemStatus("error");
      addLog(message, "error");
      toast.error(message);
    } finally {
      setIsGenerating(false);
    }
  }, [addLog]);

  const handleInitialize = () => {
    toast("Workspace initialized", { description: "Configuration saved successfully." });
  };

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden">
      <Navbar status={systemStatus} />
      <div className="flex flex-1 min-h-0 flex-col xl:flex-row">
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
