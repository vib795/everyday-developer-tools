// Hand-written types kept in sync with backend/app/schemas/*.

export type DiffTag = "equal" | "replace" | "delete" | "insert";

export interface DiffHunk {
  tag: DiffTag;
  left: string[];
  right: string[];
  left_start: number;
  right_start: number;
}

export interface JsonValidateResponse {
  valid: boolean;
  message: string;
  formatted_json?: string | null;
  error_details?: string | null;
}

export interface JsonSchemaResponse {
  schema: Record<string, unknown>;
}

export interface JsonSampleResponse {
  sample: unknown;
}

export interface SimpleOutput {
  output: string;
}

export interface RegexCheckResponse {
  match: boolean | null;
  message: string;
}

export interface RegexGenerateResponse {
  pattern: string;
}

export interface DiffResponse {
  hunks: DiffHunk[];
}

export interface CounterResponse {
  count: number;
  output: string;
}

export interface ColumnExtractorResponse {
  columns: string[];
}

export interface CleanTextResponse {
  cleaned: string;
}

export interface TextStats {
  num_chars: number;
  num_chars_no_space: number;
  num_lines: number;
  num_words: number;
  num_sentences: number;
  num_unique_words: number;
  percent_unique_words: number;
  length_shortest_word: number;
  length_longest_word: number;
  avg_word_length: number;
}

export interface RandomNumberResponse {
  value: number;
}
export interface RandomStringResponse {
  value: string;
}
export interface ShuffleResponse {
  value: string;
}

export interface Base64Response {
  output: string;
}

export interface JwtResponse {
  decoded?: Record<string, unknown> | null;
  error?: string | null;
}

export interface TimeConvertResponse {
  output: Record<string, string | string[]>;
}

export interface CronResponse {
  expression: string;
}

export interface FakeRecord {
  [k: string]: unknown;
}
export interface FakePreviewResponse {
  records: FakeRecord[];
}
