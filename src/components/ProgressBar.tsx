import { Check } from "lucide-react";

const steps = ["Input", "Generate", "Build", "Launch", "Debug", "Running"];

interface ProgressBarProps {
  currentStep: number; // 0-5
}

const ProgressBar = ({ currentStep }: ProgressBarProps) => {
  return (
    <div className="glass-panel-strong border-t border-glass-border rounded-none px-6 py-3">
      <div className="flex items-center justify-between max-w-3xl mx-auto">
        {steps.map((step, i) => {
          const isCompleted = i < currentStep;
          const isActive = i === currentStep;

          return (
            <div key={step} className="flex items-center">
              <div className="flex flex-col items-center gap-1">
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-500
                    ${isCompleted ? "bg-success text-success-foreground shadow-[0_0_10px_hsl(var(--success)/0.4)]" : ""}
                    ${isActive ? "bg-primary text-primary-foreground neon-glow animate-pulse-neon" : ""}
                    ${!isCompleted && !isActive ? "bg-secondary/50 text-muted-foreground border border-glass-border" : ""}
                  `}
                >
                  {isCompleted ? <Check className="w-3.5 h-3.5" /> : i + 1}
                </div>
                <span className={`text-[10px] font-medium transition-colors duration-300 ${isActive ? "text-primary" : isCompleted ? "text-success" : "text-muted-foreground/50"}`}>
                  {step}
                </span>
              </div>
              {i < steps.length - 1 && (
                <div className={`w-10 h-px mx-1 transition-colors duration-500 ${i < currentStep ? "bg-success" : "bg-glass-border"}`} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ProgressBar;
