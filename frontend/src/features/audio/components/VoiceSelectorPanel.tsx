import { Loader2 } from "lucide-react";

import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import type { LocaleOption, VoiceOption } from "./types";

interface VoiceSelectorPanelProps {
  selectedLocale: string;
  selectedVoiceId: string;
  locales: LocaleOption[];
  voices: VoiceOption[];
  isLoadingLocales?: boolean;
  isLoadingVoices?: boolean;
  onLocaleChange: (locale: string | null) => void;
  onVoiceSelect: (voiceId: string) => void;
}

const VoiceSelectorPanel = ({
  selectedLocale,
  selectedVoiceId,
  locales,
  voices,
  isLoadingLocales = false,
  isLoadingVoices = false,
  onLocaleChange,
  onVoiceSelect,
}: VoiceSelectorPanelProps) => {
  const selectedLocaleLabel =
    locales.find((item) => item.locale === selectedLocale)?.label ?? selectedLocale;

  return (
    <Card className="flex h-full min-h-0 flex-col gap-3.5 rounded-xl border border-slate-200/80 bg-card p-4 shadow-xs lg:col-span-4 xl:col-span-3 dark:border-border">
      {/* Language / Locale Select */}
      <div className="flex shrink-0 flex-col gap-1.5">
        <Label className="text-xs font-normal text-slate-600 dark:text-slate-400">
          Language
        </Label>
        <Select
          value={selectedLocale}
          onValueChange={onLocaleChange}
          disabled={isLoadingLocales}
        >
          <SelectTrigger className="h-10 w-full rounded-md border-slate-200 bg-background px-3 text-sm text-slate-800 dark:border-input dark:text-slate-100">
            <SelectValue>{selectedLocaleLabel}</SelectValue>
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              {locales.map((item) => (
                <SelectItem key={item.locale} value={item.locale}>
                  {item.label}
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>

      {/* Voice List */}
      <div className="flex min-h-0 flex-1 flex-col gap-1.5">
        <Label className="shrink-0 text-xs font-normal text-slate-600 dark:text-slate-400">
          Voice ({voices.length})
        </Label>
        <ScrollArea className="min-h-0 flex-1 pr-2.5">
          {isLoadingVoices ? (
            <div className="flex h-40 items-center justify-center gap-2 text-xs text-slate-500">
              <Loader2 className="size-4 animate-spin text-[#4338ca]" />
              <span>Loading voices...</span>
            </div>
          ) : voices.length === 0 ? (
            <div className="flex h-40 items-center justify-center text-xs text-slate-500">
              No voices found for {selectedLocale}
            </div>
          ) : (
            <div className="flex flex-col gap-2 pb-1">
              {voices.map((voice) => {
                const isSelected = voice.id === selectedVoiceId;
                return (
                  <button
                    key={voice.id}
                    type="button"
                    onClick={() => onVoiceSelect(voice.id)}
                    className={cn(
                      "flex w-full cursor-pointer items-center rounded-md border px-3 py-2.5 text-left transition-all outline-none",
                      isSelected
                        ? "border-[#4338ca] bg-indigo-50/40 dark:border-indigo-500 dark:bg-indigo-950/30"
                        : "border-slate-200 bg-background hover:border-slate-300 hover:bg-slate-50/60 dark:border-input dark:hover:bg-muted/40"
                    )}
                  >
                    <div className="flex min-w-0 items-center gap-2">
                      <span
                        className="shrink-0 text-base leading-none font-semibold text-[#4338ca] dark:text-indigo-400"
                        aria-hidden="true"
                      >
                        {voice.gender === "Male" ? "♂" : "♀"}
                      </span>
                      <span
                        className="truncate text-xs text-slate-700 sm:text-[13px] dark:text-slate-200"
                        title={`${voice.label} (${voice.id})`}
                      >
                        {voice.label}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </ScrollArea>
      </div>
    </Card>
  );
};

export default VoiceSelectorPanel;
