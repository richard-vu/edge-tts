import type { TtsVoice } from "@/apis/type";

export type Gender = "Male" | "Female";
export type SpeedOption = "0.5x" | "1x" | "1.5x";

export interface LocaleOption {
  locale: string;
  label: string;
}

export interface VoiceOption {
  id: string;
  label: string;
  locale: string;
  gender: Gender;
}

export const DEFAULT_LOCALE = "en-US";
export const DEFAULT_VOICE_ID = "en-US-AndrewNeural";
export const MAX_TEXT_LENGTH = 5000;

export const SPEED_OPTIONS: SpeedOption[] = ["0.5x", "1x", "1.5x"];

export const SPEED_RATE_MAP: Record<SpeedOption, string> = {
  "0.5x": "-50%",
  "1x": "+0%",
  "1.5x": "+50%",
};

export const DEFAULT_TEXT =
  "Hello teachers, welcome to the lecture!";

const languageDisplayNames =
  typeof Intl !== "undefined" && "DisplayNames" in Intl
    ? new Intl.DisplayNames(["en"], { type: "language" })
    : null;

export function formatLocaleLabel(locale: string): string {
  try {
    const display = languageDisplayNames?.of(locale);
    if (display && display.toLowerCase() !== locale.toLowerCase()) {
      return `${display} (${locale})`;
    }
  } catch {
    // Ignore invalid locale tag formatting errors
  }
  return locale;
}

export function mapTtsVoiceToOption(voice: TtsVoice): VoiceOption {
  const gender: Gender = voice.Gender === "Female" ? "Female" : "Male";
  // Transform "Microsoft Andrew Online (Natural) - English (United States)" -> "English (United States) - Andrew"
  let label = voice.ShortName;
  if (voice.FriendlyName) {
    const cleaned = voice.FriendlyName.replace(/^Microsoft\s+/i, "").replace(
      /\s+Online\s*\(Natural\)\s*/i,
      " "
    );
    const parts = cleaned.split(" - ");
    if (parts.length === 2) {
      label = `${parts[1].trim()} - ${parts[0].trim()}`;
    } else {
      label = cleaned.trim();
    }
  }

  return {
    id: voice.ShortName,
    label,
    locale: voice.Locale,
    gender,
  };
}
