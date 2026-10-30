import {
  ArrowDownAZ,
  ArrowUpAZ,
  ChevronLeft,
  ChevronRight,
  Download,
  Loader2,
  Search,
  Trash2,
  Volume2,
  X,
} from "lucide-react";

import type { TtsAudio } from "@/apis/type";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";

interface AudioDisplayPanelProps {
  audios: TtsAudio[];
  totalElements: number;
  totalPages: number;
  page: number;
  size: number;
  search: string;
  sortBy: string;
  sortDir: "asc" | "desc";
  selectedIds: string[];
  playingFileName?: string | null;
  isLoading?: boolean;
  isDeleting?: boolean;
  onSearchChange: (value: string) => void;
  onPageChange: (page: number) => void;
  onSizeChange: (size: number) => void;
  onSortByChange: (sortBy: string) => void;
  onSortDirToggle: () => void;
  onToggleSelectAll: (checked: boolean) => void;
  onToggleSelectRow: (id: string, checked: boolean) => void;
  onListen: (fileName: string) => void;
  onDownload: (fileName: string) => void;
  onDeleteIds: (ids: string[]) => void;
}

const SORT_FIELDS = [
  { value: "text", label: "Text" },
  { value: "vn_meaning", label: "Vietnamese Meaning" },
  { value: "voice", label: "Voice" },
];

const PAGE_SIZES = [10, 20, 50];

const AudioDisplayPanel = ({
  audios,
  totalElements,
  totalPages,
  page,
  size,
  search,
  sortBy,
  sortDir,
  selectedIds,
  playingFileName = null,
  isLoading = false,
  isDeleting = false,
  onSearchChange,
  onPageChange,
  onSizeChange,
  onSortByChange,
  onSortDirToggle,
  onToggleSelectAll,
  onToggleSelectRow,
  onListen,
  onDownload,
  onDeleteIds,
}: AudioDisplayPanelProps) => {
  const allCurrentSelected =
    audios.length > 0 && audios.every((item) => selectedIds.includes(item.id));

  const currentSortLabel =
    SORT_FIELDS.find((f) => f.value === sortBy)?.label ?? sortBy;

  return (
    <Card className="row-span-2 flex h-full min-h-0 flex-col gap-3 rounded-xl border border-slate-200/80 bg-card p-4 shadow-xs dark:border-border">
      {/* Header & Controls */}
      <div className="flex shrink-0 flex-wrap items-center justify-between gap-2.5">
        <div className="flex flex-1 items-center gap-2">
          {/* Search Box */}
          <div className="relative w-full max-w-sm">
            <Search className="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-slate-400" />
            <Input
              value={search}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="Search text..."
              className="h-8 pr-8 pl-8 text-xs sm:text-sm"
            />
            {search && (
              <button
                type="button"
                onClick={() => onSearchChange("")}
                aria-label="Clear search"
                className="absolute top-1/2 right-2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              >
                <X className="size-3.5" />
              </button>
            )}
          </div>

          {/* Sort By */}
          <div className="flex items-center gap-1.5">
            <Select
              value={sortBy}
              onValueChange={(value) => {
                if (value) onSortByChange(value);
              }}
            >
              <SelectTrigger className="h-8 w-[150px] text-xs">
                <SelectValue>{currentSortLabel}</SelectValue>
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  {SORT_FIELDS.map((field) => (
                    <SelectItem key={field.value} value={field.value}>
                      {field.label}
                    </SelectItem>
                  ))}
                </SelectGroup>
              </SelectContent>
            </Select>

            <Button
              type="button"
              variant="outline"
              size="icon-sm"
              onClick={onSortDirToggle}
              title={`Sort direction: ${sortDir.toUpperCase()}`}
              className="size-8"
            >
              {sortDir === "asc" ? (
                <ArrowUpAZ className="size-4" />
              ) : (
                <ArrowDownAZ className="size-4" />
              )}
            </Button>
          </div>
        </div>

        {/* Bulk Delete Action */}
        <div className="flex items-center gap-2">
          {selectedIds.length > 0 && (
            <Button
              type="button"
              variant="destructive"
              size="sm"
              disabled={isDeleting}
              onClick={() => onDeleteIds(selectedIds)}
              className="h-8 gap-1.5 text-xs"
            >
              {isDeleting ? (
                <Loader2 className="size-3.5 animate-spin" />
              ) : (
                <Trash2 className="size-3.5" />
              )}
              <span>Delete ({selectedIds.length})</span>
            </Button>
          )}
        </div>
      </div>

      {/* Table Area */}
      <div className="min-h-0 flex-1 overflow-hidden rounded-lg border border-slate-200/80 dark:border-border">
        <ScrollArea className="h-full w-full">
          <Table>
            <TableHeader className="sticky top-0 z-10 bg-slate-50/95 backdrop-blur-xs dark:bg-muted/80">
              <TableRow>
                <TableHead className="w-10 px-3">
                  <Checkbox
                    checked={allCurrentSelected}
                    onCheckedChange={(checked) =>
                      onToggleSelectAll(Boolean(checked))
                    }
                    aria-label="Select all rows"
                  />
                </TableHead>
                <TableHead className="min-w-[240px]">Text</TableHead>
                <TableHead className="min-w-[200px]">
                  Vietnamese Meaning
                </TableHead>
                <TableHead className="w-[180px]">Voice</TableHead>
                <TableHead className="w-[80px] text-center">Listen</TableHead>
                <TableHead className="w-[90px] text-center">Download</TableHead>
                <TableHead className="w-[80px] text-right pr-4">
                  Action
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={7} className="h-44 text-center">
                    <div className="flex items-center justify-center gap-2 text-xs text-slate-500">
                      <Loader2 className="size-4 animate-spin text-[#4338ca]" />
                      <span>Loading generated audios...</span>
                    </div>
                  </TableCell>
                </TableRow>
              ) : audios.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="h-44 text-center">
                    <div className="flex flex-col items-center justify-center text-center">
                      <p className="text-xs font-medium text-slate-600 sm:text-sm dark:text-slate-300">
                        No audio files found
                      </p>
                      <p className="mt-1 text-xs text-slate-400">
                        Generated audio files will be shown and available here
                      </p>
                    </div>
                  </TableCell>
                </TableRow>
              ) : (
                audios.map((item) => {
                  const isSelected = selectedIds.includes(item.id);
                  const isPending = !item.fileName;
                  const isPlaying =
                    Boolean(item.fileName) && playingFileName === item.fileName;
                  return (
                    <TableRow
                      key={item.id}
                      data-state={isSelected ? "selected" : undefined}
                    >
                      <TableCell className="px-3">
                        <Checkbox
                          checked={isSelected}
                          onCheckedChange={(checked) =>
                            onToggleSelectRow(item.id, Boolean(checked))
                          }
                          aria-label={`Select row ${item.text}`}
                        />
                      </TableCell>
                      <TableCell className="max-w-[340px] truncate font-medium text-slate-800 dark:text-slate-100">
                        <span title={item.text}>{item.text}</span>
                      </TableCell>
                      <TableCell className="max-w-[300px] truncate text-slate-600 dark:text-slate-300">
                        {item.vnMeaning ? (
                          <span title={item.vnMeaning}>{item.vnMeaning}</span>
                        ) : isPending ? (
                          <span className="inline-flex items-center gap-1.5 text-xs italic text-slate-400">
                            <Loader2 className="size-3 animate-spin text-[#4338ca]" />
                            Translating...
                          </span>
                        ) : (
                          <span>—</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary" className="font-normal">
                          {item.voice}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-center">
                        {isPending ? (
                          <span
                            className="inline-flex size-7 items-center justify-center"
                            title="Generating audio in background..."
                          >
                            <Loader2 className="size-4 animate-spin text-[#4338ca]" />
                          </span>
                        ) : (
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon-sm"
                            onClick={() => {
                              if (item.fileName) {
                                onListen(item.fileName);
                              }
                            }}
                            aria-label={`Listen to ${item.text}`}
                            title={isPlaying ? "Stop audio" : "Listen audio"}
                            className={cn(
                              "size-7 transition-colors",
                              isPlaying
                                ? "bg-indigo-50 text-[#4338ca] hover:bg-indigo-100 dark:bg-indigo-950/50 dark:text-indigo-400"
                                : "text-slate-600 hover:bg-indigo-50 hover:text-[#4338ca] dark:text-slate-300 dark:hover:bg-indigo-950/40 dark:hover:text-indigo-400"
                            )}
                          >
                            <Volume2
                              className={cn(
                                "size-4",
                                isPlaying && "animate-pulse"
                              )}
                            />
                          </Button>
                        )}
                      </TableCell>
                      <TableCell className="text-center">
                        {isPending ? (
                          <span
                            className="inline-flex size-7 items-center justify-center"
                            title="Generating audio in background..."
                          >
                            <Loader2 className="size-4 animate-spin text-slate-400" />
                          </span>
                        ) : (
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon-sm"
                            onClick={() => {
                              if (item.fileName) {
                                onDownload(item.fileName);
                              }
                            }}
                            aria-label={`Download ${item.text}`}
                            title="Download MP3"
                            className="size-7 text-slate-600 hover:bg-indigo-50 hover:text-[#4338ca] dark:text-slate-300 dark:hover:bg-indigo-950/40 dark:hover:text-indigo-400"
                          >
                            <Download className="size-4" />
                          </Button>
                        )}
                      </TableCell>
                      <TableCell className="pr-4 text-right">
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon-sm"
                          disabled={isDeleting}
                          onClick={() => onDeleteIds([item.id])}
                          aria-label={`Delete ${item.text}`}
                          className="size-7 text-slate-500 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950/40 dark:hover:text-red-400"
                        >
                          <Trash2 className="size-3.5" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </ScrollArea>
      </div>

      {/* Pagination Footer */}
      <div className="flex shrink-0 flex-wrap items-center justify-between gap-2 text-xs text-slate-600 dark:text-slate-400">
        <div className="flex items-center gap-2">
          <span>Total: {totalElements} record(s)</span>
          <span className="text-slate-300 dark:text-slate-700">|</span>
          <div className="flex items-center gap-1.5">
            <span>Rows:</span>
            <Select
              value={String(size)}
              onValueChange={(value) => {
                if (value) onSizeChange(Number(value));
              }}
            >
              <SelectTrigger className="h-7 w-[68px] px-2 text-xs">
                <SelectValue>{size}</SelectValue>
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  {PAGE_SIZES.map((s) => (
                    <SelectItem key={s} value={String(s)}>
                      {s}
                    </SelectItem>
                  ))}
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span>
            Page {totalPages === 0 ? 0 : page + 1} of {totalPages}
          </span>
          <div className="flex items-center gap-1">
            <Button
              type="button"
              variant="outline"
              size="icon-sm"
              disabled={page <= 0 || isLoading}
              onClick={() => onPageChange(page - 1)}
              className="size-7"
            >
              <ChevronLeft className="size-3.5" />
            </Button>
            <Button
              type="button"
              variant="outline"
              size="icon-sm"
              disabled={page + 1 >= totalPages || isLoading}
              onClick={() => onPageChange(page + 1)}
              className="size-7"
            >
              <ChevronRight className="size-3.5" />
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default AudioDisplayPanel;
