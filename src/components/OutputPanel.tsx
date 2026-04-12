import { Terminal, CheckCircle2, AlertTriangle, XCircle, Activity } from "lucide-react";
import { useEffect, useRef } from "react";

export interface LogEntry {
  id: number;
  message: string;
  type: "info" | "success" | "warning" | "error";
  timestamp: string;
}

interface StatusCardProps {
  label: string;
  status: "idle" | "running" | "success" | "error";
}

const StatusCard = ({ label, status }: StatusCardProps) => {
  const config = {
    idle: { icon: Activity, color: "text-muted-foreground", bg: "bg-secondary/30", border: "border-glass-border" },
    running: { icon: Activity, color: "text-warning", bg: "bg-warning/5", border: "border-warning/30" },
    success: { icon: CheckCircle2, color: "text-success", bg: "bg-success/5", border: "border-success/30" },
    error: { icon: XCircle, color: "text-destructive", bg: "bg-destructive/5", border: "border-destructive/30" },
  }[status];

  return (
    <div className={`${config.bg} border ${config.border} rounded-lg px-3 py-2 flex items-center gap-2 transition-all duration-500`}>
      <config.icon className={`w-3.5 h-3.5 ${config.color} ${status === "running" ? "animate-spin" : ""}`} />
      <div>
        <p className="text-[10px] text-muted-foreground uppercase tracking-wider">{label}</p>
        <p className={`text-xs font-medium capitalize ${config.color}`}>{status}</p>
      </div>
    </div>
  );
};

interface OutputPanelProps {
  logs: LogEntry[];
  buildStatus: "idle" | "running" | "success" | "error";
  simStatus: "idle" | "running" | "success" | "error";
  debugStatus: "idle" | "running" | "success" | "error";
}

const logColors = {
  info: "text-muted-foreground",
  success: "text-success",
  warning: "text-warning",
  error: "text-destructive",
};

const logPrefixes = {
  info: "INFO",
  success: " OK ",
  warning: "WARN",
  error: " ERR",
};

const OutputPanel = ({ logs, buildStatus, simStatus, debugStatus }: OutputPanelProps) => {
  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div className="w-full xl:w-80 h-64 xl:h-auto glass-panel-strong border-t xl:border-t-0 xl:border-l border-glass-border rounded-none flex flex-col shrink-0">
      {/* Header */}
      <div className="flex items-center gap-2 p-4 border-b border-glass-border">
        <Terminal className="w-4 h-4 text-primary" />
        <h2 className="text-sm font-semibold text-foreground">Live Output</h2>
        <div className="ml-auto flex gap-1">
          <div className="w-2.5 h-2.5 rounded-full bg-destructive/60" />
          <div className="w-2.5 h-2.5 rounded-full bg-warning/60" />
          <div className="w-2.5 h-2.5 rounded-full bg-success/60" />
        </div>
      </div>

      {/* Status Cards */}
      <div className="p-3 grid grid-cols-3 gap-2 border-b border-glass-border">
        <StatusCard label="Build" status={buildStatus} />
        <StatusCard label="Sim" status={simStatus} />
        <StatusCard label="Debug" status={debugStatus} />
      </div>

      {/* Terminal Logs */}
      <div className="flex-1 p-3 overflow-y-auto scrollbar-thin min-h-0">
        {logs.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-xs text-muted-foreground/50 font-mono">Awaiting commands...</p>
          </div>
        ) : (
          <div className="space-y-0.5">
            {logs.map((log) => (
              <div key={log.id} className="terminal-text flex gap-2 animate-fade-in">
                <span className="text-muted-foreground/40 text-[10px] mt-0.5 shrink-0">{log.timestamp}</span>
                <span className={`text-[10px] font-semibold shrink-0 ${logColors[log.type]}`}>[{logPrefixes[log.type]}]</span>
                <span className={logColors[log.type]}>{log.message}</span>
              </div>
            ))}
            <div ref={logsEndRef} />
            <span className="terminal-text text-primary animate-blink">▋</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default OutputPanel;
