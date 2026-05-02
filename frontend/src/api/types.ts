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

// Codec & hash

export interface UuidGenerateResponse {
  values: string[];
}

export interface UuidInspectResponse {
  valid: boolean;
  version?: number | null;
  variant?: string | null;
  is_nil?: boolean | null;
  hex?: string | null;
  urn?: string | null;
  timestamp_iso?: string | null;
  error?: string | null;
}

export interface HashResponse {
  digests: Record<string, string>;
}

export interface HmacResponse {
  digest: string;
}

export interface UrlCodecResponse {
  output: string;
}

export interface QueryParamPair {
  key: string;
  value: string;
}

export interface QueryStringResponse {
  params: QueryParamPair[];
  base?: string | null;
}

export interface CaseConvertResponse {
  output: string;
}

export interface JwtSignResponse {
  token?: string | null;
  error?: string | null;
}

// Format converters

export interface FormatConvertResponse {
  output: string;
  error?: string | null;
}

export interface JsonPathResponse {
  matches: unknown[];
  error?: string | null;
}

export interface CurlConvertResponse {
  outputs: Record<string, string>;
  error?: string | null;
}

// Calculators & previews

export interface CronNextRunsResponse {
  runs: string[];
  error?: string | null;
}

export interface ColorConvertResponse {
  hex: string;
  rgb: string;
  hsl: string;
  oklch?: string | null;
  error?: string | null;
}

export interface ContrastResponse {
  ratio: number;
  aa_normal: boolean;
  aa_large: boolean;
  aaa_normal: boolean;
  aaa_large: boolean;
  error?: string | null;
}

export interface ChmodResponse {
  numeric: string;
  symbolic: string;
  error?: string | null;
}

export interface CidrResponse {
  network: string;
  netmask: string;
  broadcast: string | null;
  first_host: string | null;
  last_host: string | null;
  num_hosts: number;
  prefix: number;
  version: number;
  error?: string | null;
}

export interface MarkdownPreviewResponse {
  html: string;
}

// Reference & misc

export interface HttpStatus {
  code: number;
  name: string;
  description: string;
}
export interface HttpStatusListResponse {
  statuses: HttpStatus[];
}

export interface MimeType {
  type: string;
  extensions: string[];
  description: string;
}
export interface MimeTypeListResponse {
  mime_types: MimeType[];
}

export interface LoremResponse {
  text: string;
}

export interface QrCodeResponse {
  svg: string;
  error?: string | null;
}
