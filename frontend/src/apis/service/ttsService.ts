import type {
  ApiResponse,
  GenerateAudioRequest,
  GetTtsAudiosParams,
  PageResponse,
  SupportedLanguage,
  TtsAudio,
  TtsVoice,
} from "../type";

function getRequiredEnv(name: string): string {
  const value = (import.meta.env[name] as string | undefined)?.trim();
  if (!value) {
    throw new Error(`Missing environment variable: ${name} is not configured.`);
  }
  return value;
}

function getBackendUrl(): string {
  return getRequiredEnv("VITE_BACKEND_URL").replace(/\/+$/, "");
}

export async function getTtsAudios(
  params: GetTtsAudiosParams = {}
): Promise<ApiResponse<PageResponse<TtsAudio>>> {
  const backendUrl = getBackendUrl();
  const {
    search = "",
    page = 0,
    size = 20,
    sortBy = "text",
    sortDir = "asc",
  } = params;

  const queryParams = new URLSearchParams({
    page: String(page),
    size: String(size),
    sortBy,
    sortDir,
  });

  if (search !== null && search !== undefined) {
    queryParams.set("search", search);
  }

  const response = await fetch(`${backendUrl}/api/v1/tts?${queryParams.toString()}`, {
    method: "GET",
    headers: {
      accept: "*/*",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch TTS audios: HTTP ${response.status}`);
  }

  return (await response.json()) as ApiResponse<PageResponse<TtsAudio>>;
}

export async function getSupportedLanguages(): Promise<ApiResponse<SupportedLanguage[]>> {
  const backendUrl = getBackendUrl();
  const response = await fetch(`${backendUrl}/api/v1/tts/supported-languages`, {
    method: "GET",
    headers: {
      accept: "*/*",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch supported languages: HTTP ${response.status}`);
  }

  return (await response.json()) as ApiResponse<SupportedLanguage[]>;
}

export async function getVoicesByLang(lang: string = "en-US"): Promise<ApiResponse<TtsVoice[]>> {
  const backendUrl = getBackendUrl();
  const query = new URLSearchParams({ lang }).toString();
  const response = await fetch(`${backendUrl}/api/v1/tts/voices?${query}`, {
    method: "GET",
    headers: {
      accept: "*/*",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch voices for locale '${lang}': HTTP ${response.status}`);
  }

  return (await response.json()) as ApiResponse<TtsVoice[]>;
}

export async function generateAudio(
  payload: GenerateAudioRequest
): Promise<ApiResponse<string>> {
  if (payload.text.length > 5000) {
    throw new Error("Text must not exceed 5000 characters.");
  }

  const backendUrl = getBackendUrl();
  const body = {
    text: payload.text,
    voice: payload.voice?.trim() || getRequiredEnv("VITE_TTS_DEFAULT_VOICE"),
    rate: payload.rate?.trim() || getRequiredEnv("VITE_TTS_DEFAULT_RATE"),
    volume: payload.volume?.trim() || getRequiredEnv("VITE_TTS_DEFAULT_VOLUME"),
    pitch: payload.pitch?.trim() || getRequiredEnv("VITE_TTS_DEFAULT_PITCH"),
  };

  const response = await fetch(`${backendUrl}/api/v1/tts/generate-audio`, {
    method: "POST",
    headers: {
      accept: "*/*",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`Failed to generate audio: HTTP ${response.status}`);
  }

  return (await response.json()) as ApiResponse<string>;
}

export async function deleteTtsAudios(ids: string[]): Promise<ApiResponse<string[]>> {
  const backendUrl = getBackendUrl();
  const response = await fetch(`${backendUrl}/api/v1/tts`, {
    method: "DELETE",
    headers: {
      accept: "*/*",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(ids),
  });

  if (!response.ok) {
    throw new Error(`Failed to delete TTS audios: HTTP ${response.status}`);
  }

  return (await response.json()) as ApiResponse<string[]>;
}

export async function getAudioFile(fileName: string): Promise<Blob> {
  const backendUrl = getBackendUrl();
  const encodedFileName = encodeURIComponent(fileName.trim());
  const response = await fetch(`${backendUrl}/api/v1/tts/audio/${encodedFileName}`, {
    method: "GET",
    headers: {
      accept: "audio/mpeg, */*",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch audio file '${fileName}': HTTP ${response.status}`);
  }

  return await response.blob();
}
