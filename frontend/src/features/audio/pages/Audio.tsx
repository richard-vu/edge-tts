import { useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import {
  deleteTtsAudios,
  generateAudio,
  getAudioFile,
  getSupportedLanguages,
  getTtsAudios,
  getVoicesByLang,
} from "@/apis/service/ttsService";
import {
  AudioDisplayPanel,
  AudioGeneratorPanel,
  DEFAULT_LOCALE,
  DEFAULT_TEXT,
  DEFAULT_VOICE_ID,
  formatLocaleLabel,
  type LocaleOption,
  mapTtsVoiceToOption,
  MAX_TEXT_LENGTH,
  SPEED_RATE_MAP,
  type SpeedOption,
  VoiceSelectorPanel,
} from "../components";

const Audio = () => {
  const queryClient = useQueryClient();

  const [selectedLocale, setSelectedLocale] = useState<string>(DEFAULT_LOCALE);
  const [selectedVoiceId, setSelectedVoiceId] = useState<string>(DEFAULT_VOICE_ID);
  const [text, setText] = useState<string>(DEFAULT_TEXT);
  const [speed, setSpeed] = useState<SpeedOption>("1x");

  // Search, sort, pagination & selection state for Audio Display Area
  const [search, setSearch] = useState<string>("");
  const [page, setPage] = useState<number>(0);
  const [size, setSize] = useState<number>(20);
  const [sortBy, setSortBy] = useState<string>("text");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [playingFileName, setPlayingFileName] = useState<string | null>(null);

  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);
  const audioObjectUrlRef = useRef<string | null>(null);

  const stopCurrentAudio = () => {
    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause();
      audioPlayerRef.current.src = "";
      audioPlayerRef.current = null;
    }
    if (audioObjectUrlRef.current) {
      URL.revokeObjectURL(audioObjectUrlRef.current);
      audioObjectUrlRef.current = null;
    }
    setPlayingFileName(null);
  };

  useEffect(() => {
    return () => {
      stopCurrentAudio();
    };
  }, []);

  const { data: languagesResp, isLoading: isLoadingLocales } = useQuery({
    queryKey: ["tts", "supported-languages"],
    queryFn: getSupportedLanguages,
  });

  const { data: voicesResp, isLoading: isLoadingVoices } = useQuery({
    queryKey: ["tts", "voices", selectedLocale],
    queryFn: () => getVoicesByLang(selectedLocale),
    enabled: Boolean(selectedLocale),
  });

  const { data: audiosResp, isLoading: isLoadingAudios } = useQuery({
    queryKey: ["tts", "audios", { search, page, size, sortBy, sortDir }],
    queryFn: () =>
      getTtsAudios({
        search,
        page,
        size,
        sortBy,
        sortDir,
      }),
    refetchInterval: (query) => {
      const items = query.state.data?.data?.content ?? [];
      const hasPendingAudio = items.some((item) => !item.fileName);
      return hasPendingAudio ? 2000 : false;
    },
  });

  const generateAudioMutation = useMutation({
    mutationFn: generateAudio,
    onSuccess: (response) => {
      toast.success(response.message || "Audio generated successfully");
      queryClient.invalidateQueries({ queryKey: ["tts", "audios"] });
    },
    onError: (error) => {
      toast.error(
        error instanceof Error ? error.message : "Failed to generate audio"
      );
    },
  });

  const deleteAudiosMutation = useMutation({
    mutationFn: deleteTtsAudios,
    onSuccess: (response, deletedIds) => {
      toast.success(response.message || "Deleted audio record(s) successfully");
      setSelectedIds((prev) => prev.filter((id) => !deletedIds.includes(id)));
      queryClient.invalidateQueries({ queryKey: ["tts", "audios"] });
    },
    onError: (error) => {
      toast.error(
        error instanceof Error ? error.message : "Failed to delete audio records"
      );
    },
  });

  const localeOptions = useMemo<LocaleOption[]>(() => {
    const groups = languagesResp?.data ?? [];
    const allLocales = groups.flatMap((group) => group.locales);
    if (allLocales.length === 0) {
      return [{ locale: DEFAULT_LOCALE, label: formatLocaleLabel(DEFAULT_LOCALE) }];
    }
    return allLocales.map((locale) => ({
      locale,
      label: formatLocaleLabel(locale),
    }));
  }, [languagesResp]);

  const voiceOptions = useMemo(() => {
    const rawVoices = voicesResp?.data ?? [];
    return rawVoices.map(mapTtsVoiceToOption);
  }, [voicesResp]);

  // Keep selectedVoiceId valid when voiceOptions change for a newly selected locale
  const activeVoiceId = useMemo(() => {
    if (voiceOptions.length === 0) {
      return selectedVoiceId;
    }
    if (voiceOptions.some((v) => v.id === selectedVoiceId)) {
      return selectedVoiceId;
    }
    const defaultMatch = voiceOptions.find((v) => v.id === DEFAULT_VOICE_ID);
    return defaultMatch ? defaultMatch.id : voiceOptions[0].id;
  }, [voiceOptions, selectedVoiceId]);

  const audios = useMemo(
    () => audiosResp?.data?.content ?? [],
    [audiosResp]
  );
  const totalElements = audiosResp?.data?.totalElements ?? 0;
  const totalPages = audiosResp?.data?.totalPages ?? 0;

  const handleLocaleChange = (value: string | null) => {
    if (!value) return;
    setSelectedLocale(value);
  };

  const handleGenerateAudio = () => {
    const trimmedText = text.trim();
    if (!trimmedText) {
      toast.warning("Please enter text to generate audio.");
      return;
    }
    if (trimmedText.length > MAX_TEXT_LENGTH) {
      toast.warning(`Text must not exceed ${MAX_TEXT_LENGTH} characters.`);
      return;
    }

    generateAudioMutation.mutate({
      text: trimmedText,
      voice: activeVoiceId,
      rate: SPEED_RATE_MAP[speed],
    });
  };

  const handleSearchChange = (value: string) => {
    setSearch(value);
    setPage(0);
  };

  const handleSizeChange = (newSize: number) => {
    setSize(newSize);
    setPage(0);
  };

  const handleSortByChange = (newSortBy: string) => {
    setSortBy(newSortBy);
    setPage(0);
  };

  const handleSortDirToggle = () => {
    setSortDir((prev) => (prev === "asc" ? "desc" : "asc"));
    setPage(0);
  };

  const handleToggleSelectAll = (checked: boolean) => {
    const currentPageIds = audios.map((item) => item.id);
    if (checked) {
      setSelectedIds((prev) => Array.from(new Set([...prev, ...currentPageIds])));
    } else {
      setSelectedIds((prev) => prev.filter((id) => !currentPageIds.includes(id)));
    }
  };

  const handleToggleSelectRow = (id: string, checked: boolean) => {
    if (checked) {
      setSelectedIds((prev) => (prev.includes(id) ? prev : [...prev, id]));
    } else {
      setSelectedIds((prev) => prev.filter((item) => item !== id));
    }
  };

  const handleDeleteIds = (ids: string[]) => {
    if (ids.length === 0) return;
    deleteAudiosMutation.mutate(ids);
  };

  const handleListen = async (fileName: string) => {
    if (playingFileName === fileName) {
      stopCurrentAudio();
      return;
    }

    stopCurrentAudio();
    setPlayingFileName(fileName);

    try {
      const blob = await getAudioFile(fileName);
      const objectUrl = URL.createObjectURL(blob);
      audioObjectUrlRef.current = objectUrl;

      const player = new window.Audio(objectUrl);
      audioPlayerRef.current = player;

      player.onended = () => {
        stopCurrentAudio();
      };
      player.onerror = () => {
        stopCurrentAudio();
        toast.error("Failed to play audio file");
      };

      await player.play();
    } catch (error) {
      stopCurrentAudio();
      toast.error(
        error instanceof Error ? error.message : "Failed to load audio file"
      );
    }
  };

  const handleDownload = async (fileName: string) => {
    try {
      const blob = await getAudioFile(fileName);
      const objectUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = objectUrl;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(objectUrl);
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Failed to download audio file"
      );
    }
  };

  return (
    <div className="h-full w-full overflow-hidden bg-gradient-to-r from-pink-50/60 via-slate-50/40 to-pink-50/60 p-4 md:px-6 md:py-5 dark:from-background dark:via-background dark:to-background">
      <div className="grid h-full w-full min-h-0 grid-cols-1 gap-4 lg:grid-cols-12">
        <VoiceSelectorPanel
          selectedLocale={selectedLocale}
          selectedVoiceId={activeVoiceId}
          locales={localeOptions}
          voices={voiceOptions}
          isLoadingLocales={isLoadingLocales}
          isLoadingVoices={isLoadingVoices}
          onLocaleChange={handleLocaleChange}
          onVoiceSelect={setSelectedVoiceId}
        />

        <div className="grid h-full min-h-0 grid-rows-3 gap-4 lg:col-span-8 xl:col-span-9">
          <AudioGeneratorPanel
            text={text}
            speed={speed}
            isGenerating={generateAudioMutation.isPending}
            onTextChange={setText}
            onSpeedChange={setSpeed}
            onGenerate={handleGenerateAudio}
          />
          <AudioDisplayPanel
            audios={audios}
            totalElements={totalElements}
            totalPages={totalPages}
            page={page}
            size={size}
            search={search}
            sortBy={sortBy}
            sortDir={sortDir}
            selectedIds={selectedIds}
            playingFileName={playingFileName}
            isLoading={isLoadingAudios}
            isDeleting={deleteAudiosMutation.isPending}
            onSearchChange={handleSearchChange}
            onPageChange={setPage}
            onSizeChange={handleSizeChange}
            onSortByChange={handleSortByChange}
            onSortDirToggle={handleSortDirToggle}
            onToggleSelectAll={handleToggleSelectAll}
            onToggleSelectRow={handleToggleSelectRow}
            onListen={handleListen}
            onDownload={handleDownload}
            onDeleteIds={handleDeleteIds}
          />
        </div>
      </div>
    </div>
  );
};

export default Audio;
