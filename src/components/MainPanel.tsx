import { Sparkles, Send } from "lucide-react";
import { useState } from "react";

const examplePrompts = [
  "4-wheel robot with LiDAR",
  "Drone with camera",
  "Robot with SLAM navigation",
  "Arm manipulator with gripper",
];

interface MainPanelProps {
  onGenerate: (prompt: string) => void;
  isGenerating: boolean;
}

const MainPanel = ({ onGenerate, isGenerating }: MainPanelProps) => {
  const [prompt, setPrompt] = useState("");

  const handleGenerate = () => {
    if (prompt.trim()) {
      onGenerate(prompt.trim());
    }
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 gradient-mesh min-h-0">
      <div className="w-full max-w-2xl space-y-6 animate-fade-in">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-medium mb-2">
            <Sparkles className="w-3 h-3" />
            AI-Powered Generation
          </div>
          <h2 className="text-2xl font-bold text-foreground">
            Describe your robot
          </h2>
          <p className="text-sm text-muted-foreground">
            Tell us what you want to build and we'll handle the rest.
          </p>
        </div>

        {/* Input */}
        <div className="glass-panel-strong p-1 neon-border animate-pulse-neon">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Create a 4-wheel robot with LiDAR and camera in a custom map..."
            rows={4}
            className="w-full bg-transparent px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground resize-none focus:outline-none scrollbar-thin"
            onKeyDown={(e) => {
              if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleGenerate();
            }}
          />
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={!prompt.trim() || isGenerating}
          className="w-full py-3 rounded-xl bg-primary text-primary-foreground font-semibold text-sm flex items-center justify-center gap-2 hover:opacity-90 neon-glow transition-all duration-300 disabled:opacity-40 disabled:cursor-not-allowed active:scale-[0.98]"
        >
          {isGenerating ? (
            <>
              <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              Generate & Launch
            </>
          )}
        </button>

        {/* Example Chips */}
        <div className="flex flex-wrap gap-2 justify-center">
          {examplePrompts.map((p) => (
            <button
              key={p}
              onClick={() => setPrompt(p)}
              className="chip"
            >
              {p}
            </button>
          ))}
        </div>

        <p className="text-center text-xs text-muted-foreground/60">
          Press <kbd className="px-1.5 py-0.5 rounded bg-secondary border border-glass-border text-muted-foreground text-[10px]">⌘</kbd> + <kbd className="px-1.5 py-0.5 rounded bg-secondary border border-glass-border text-muted-foreground text-[10px]">Enter</kbd> to generate
        </p>
      </div>
    </div>
  );
};

export default MainPanel;
