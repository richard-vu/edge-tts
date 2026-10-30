import { Loader2, Play } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import {
  MAX_TEXT_LENGTH,
  SPEED_OPTIONS,
  SPEED_RATE_MAP,
  type SpeedOption,
} from "./types";

interface AudioGeneratorPanelProps {
  text: string;
  speed: SpeedOption;
  isGenerating?: boolean;
  onTextChange: (text: string) => void;
  onSpeedChange: (speed: SpeedOption) => void;
  onGenerate?: () => void;
}

const AudioGeneratorPanel = ({
  text,
  speed,
  isGenerating = false,
  onTextChange,
  onSpeedChange,
  onGenerate,
}: AudioGeneratorPanelProps) => {
  return (
    <Card className="row-span-1 flex h-full min-h-0 flex-col gap-2.5 rounded-xl border border-slate-200/80 bg-card p-3.5 shadow-xs dark:border-border">
      <Textarea
        value={text}
        maxLength={MAX_TEXT_LENGTH}
        onChange={(e) => onTextChange(e.target.value)}
        placeholder="Enter your text here..."
        className="min-h-0 w-full flex-1 resize-none rounded-md border-slate-200 bg-background p-3 text-sm leading-relaxed text-slate-700 focus-visible:border-[#4338ca] focus-visible:ring-1 focus-visible:ring-[#4338ca]/30 dark:border-input dark:text-slate-200"
      />

      {/* Character Counter & Speed Bar */}
      <div className="flex shrink-0 flex-wrap items-center justify-between gap-3">
        <span
          className={cn(
            "text-xs",
            text.length >= MAX_TEXT_LENGTH
              ? "font-medium text-red-500"
              : "text-slate-400 dark:text-slate-500"
          )}
        >
          {text.length} / {MAX_TEXT_LENGTH}
        </span>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-600 sm:text-sm dark:text-slate-400">
            Speed:
          </span>
          <div className="inline-flex items-center overflow-hidden rounded-md border border-slate-200 dark:border-input">
            {SPEED_OPTIONS.map((option) => {
              const isActive = speed === option;
              return (
                <button
                  key={option}
                  type="button"
                  title={`Rate: ${SPEED_RATE_MAP[option]}`}
                  onClick={() => onSpeedChange(option)}
                  className={cn(
                    "h-7 border-r border-slate-200 px-2.5 text-xs transition-colors last:border-r-0 dark:border-input",
                    isActive
                      ? "bg-[#1976d2] font-medium text-white"
                      : "bg-background text-slate-600 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-muted"
                  )}
                >
                  {option}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Generate Audio Button */}
      <Button
        type="button"
        onClick={onGenerate}
        disabled={
          isGenerating || !text.trim() || text.length > MAX_TEXT_LENGTH
        }
        className="h-9 w-full shrink-0 gap-2 rounded-md bg-[#4338ca] text-sm font-normal text-white hover:bg-[#3730a3]"
      >
        {isGenerating ? (
          <>
            <Loader2 className="size-4 animate-spin" />
            <span>Generating Audio...</span>
          </>
        ) : (
          <>
            <span>Generate Audio</span>
            <span className="flex size-4 items-center justify-center rounded-full bg-white text-[#4338ca]">
              <Play className="ml-0.5 size-2.5 fill-current" />
            </span>
          </>
        )}
      </Button>
    </Card>
  );
};

export default AudioGeneratorPanel;

