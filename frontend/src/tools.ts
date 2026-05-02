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
      { path: "/convert/jsonpath", label: "JSONPath", description: "Evaluate a JSONPath expression." },
    ],
  },
  {
    label: "Convert",
    items: [
      { path: "/convert/format", label: "Format Converter", description: "JSON ⇄ YAML ⇄ TOML ⇄ XML ⇄ CSV." },
      { path: "/convert/curl", label: "cURL Converter", description: "curl → fetch / axios / requests." },
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
      { path: "/codec/url", label: "URL Codec", description: "Encode/decode URLs and parse query strings." },
      { path: "/codec/hash", label: "Hash & HMAC", description: "MD5, SHA-* and HMAC digests." },
      { path: "/jwt-viewer", label: "JWT Viewer", description: "Decode an HS256 JWT." },
      { path: "/codec/jwt-signer", label: "JWT Signer", description: "Sign payloads with HS256/384/512." },
      { path: "/codec/uuid", label: "UUID", description: "Generate and inspect UUIDs (v1/v3/v4/v5/v7)." },
      { path: "/codec/case", label: "Case Converter", description: "camelCase, snake_case, kebab-case, …" },
    ],
  },
  {
    label: "Time",
    items: [
      { path: "/time-converter", label: "Time Converter", description: "ISO / epoch / Postgres timestamp converter." },
      { path: "/cron-scheduler", label: "CRON Scheduler", description: "Build a cron expression visually." },
      { path: "/calc/cron-next", label: "CRON Next Runs", description: "When will this cron expression fire next?" },
    ],
  },
  {
    label: "Calc",
    items: [
      { path: "/calc/color", label: "Color", description: "Hex/RGB/HSL/OKLCH and WCAG contrast." },
      { path: "/calc/chmod", label: "chmod Calculator", description: "Numeric ⇄ symbolic Unix permissions." },
      { path: "/calc/cidr", label: "CIDR Calculator", description: "Subnet, range, and host count." },
    ],
  },
  {
    label: "Document",
    items: [
      { path: "/markdown-pdf-converter", label: "Markdown ⇄ PDF", description: "Convert between Markdown and PDF." },
      { path: "/calc/markdown-preview", label: "Markdown Preview", description: "Live side-by-side preview." },
    ],
  },
  {
    label: "Fake Data",
    items: [
      { path: "/fake-data-generator", label: "Fake Data", description: "Generate sample datasets in JSON or CSV." },
      { path: "/misc/lorem", label: "Lorem Ipsum", description: "Filler text for layouts." },
      { path: "/misc/qr", label: "QR Code", description: "Encode text/URL as an SVG QR code." },
    ],
  },
  {
    label: "Reference",
    items: [
      { path: "/ref/http-statuses", label: "HTTP Statuses", description: "Searchable reference of HTTP status codes." },
      { path: "/ref/mime-types", label: "MIME Types", description: "Common Content-Type / extension reference." },
    ],
  },
];
