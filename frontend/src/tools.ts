export interface ToolLink {
  path: string;
  label: string;
  description?: string;
}

export interface ToolGroup {
  label: string;
  items: ToolLink[];
}

export const TOOL_GROUPS: ToolGroup[] = [
  {
    label: "JSON",
    items: [
      { path: "/json-tools/json-validator", label: "JSON Validator", description: "Validate JSON, optionally against a schema." },
      { path: "/json-tools/json-schema-generator", label: "Schema Generator", description: "Generate a JSON Schema from a sample." },
      { path: "/json-tools/json-sample-generator", label: "Sample Generator", description: "Generate sample data from a schema." },
      { path: "/json-tools/json-converter", label: "String ⇄ JSON Converter", description: "Convert between JSON and an escaped string." },
      { path: "/json-tools/json-parser", label: "JSON Parser", description: "Beautify / pretty-print JSON." },
    ],
  },
  {
    label: "RegEx",
    items: [
      { path: "/regex-tools/regex-checker", label: "Regex Checker", description: "Test a regex against a string (ReDoS-safe)." },
      { path: "/regex-tools/regex-generator", label: "Regex Generator", description: "Suggest a regex pattern for an input." },
    ],
  },
  {
    label: "String",
    items: [
      { path: "/string-tools/diff-viewer", label: "Diff Viewer", description: "Side-by-side text diff." },
      { path: "/string-tools/counter", label: "Char/Word Counter", description: "Count characters, words, or custom tokens." },
      { path: "/string-tools/column-extractor", label: "Column Extractor", description: "Pull a column out of delimited text." },
      { path: "/string-tools/clean-text", label: "Clean Text", description: "Collapse whitespace and capitalize sentences." },
      { path: "/string-tools/text-statistics", label: "Text Statistics", description: "Counts and word-length stats." },
      { path: "/string-tools/random-number-generator", label: "Random Number", description: "Random integer in a range." },
      { path: "/string-tools/random-string-generator", label: "Random String", description: "Generate a random string." },
      { path: "/string-tools/shuffle-letters", label: "Shuffle Letters", description: "Randomize the order of letters." },
    ],
  },
  {
    label: "Encoding",
    items: [
      { path: "/base64", label: "Base64", description: "Encode / decode Base64." },
      { path: "/jwt-viewer", label: "JWT Viewer", description: "Decode an HS256 JWT." },
    ],
  },
  {
    label: "Time",
    items: [
      { path: "/time-converter", label: "Time Converter", description: "ISO / epoch / Postgres timestamp converter." },
      { path: "/cron-scheduler", label: "CRON Scheduler", description: "Build a cron expression visually." },
    ],
  },
  {
    label: "Document",
    items: [
      { path: "/markdown-pdf-converter", label: "Markdown ⇄ PDF", description: "Convert between Markdown and PDF." },
    ],
  },
  {
    label: "Fake Data",
    items: [
      { path: "/fake-data-generator", label: "Fake Data", description: "Generate sample datasets in JSON or CSV." },
    ],
  },
];
