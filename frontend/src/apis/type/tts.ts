export interface SupportedLanguage {
  lang: string;
  locales: string[];
}

export interface VoiceTag {
  ContentCategories: string[];
  VoicePersonalities: string[];
}

export interface TtsVoice {
  Name: string;
  ShortName: string;
  Gender: string;
  Locale: string;
  SuggestedCodec: string;
  FriendlyName: string;
  Status: string;
  VoiceTag?: VoiceTag | null;
}

export interface GenerateAudioRequest {
  text: string;
  voice?: string;
  rate?: string;
  volume?: string;
  pitch?: string;
}

export interface TtsAudio {
  id: string;
  text: string;
  vnMeaning?: string | null;
  voice: string;
  rate: string;
  volume: string;
  pitch: string;
  fileName?: string | null;
}

export interface GetTtsAudiosParams {
  search?: string | null;
  page?: number;
  size?: number;
  sortBy?: string;
  sortDir?: "asc" | "desc";
}
