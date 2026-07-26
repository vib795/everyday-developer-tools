import { Navigate, Route, Routes } from "react-router";

import { Layout } from "./components/Layout";
import { Home } from "./pages/home/Home";
import { Validator } from "./pages/json/Validator";
import { SchemaGenerator } from "./pages/json/SchemaGenerator";
import { SampleGenerator } from "./pages/json/SampleGenerator";
import { Converter } from "./pages/json/Converter";
import { Parser } from "./pages/json/Parser";
import { RegexChecker } from "./pages/regex/Checker";
import { RegexGenerator } from "./pages/regex/Generator";
import { DiffViewer } from "./pages/string/DiffViewer";
import { Counter } from "./pages/string/Counter";
import { ColumnExtractor } from "./pages/string/ColumnExtractor";
import { CleanText } from "./pages/string/CleanText";
import { TextStatistics } from "./pages/string/TextStatistics";
import { RandomNumber } from "./pages/string/RandomNumber";
import { RandomString } from "./pages/string/RandomString";
import { ShuffleLetters } from "./pages/string/ShuffleLetters";
import { Base64Page } from "./pages/encoding/Base64Page";
import { JwtViewer } from "./pages/encoding/JwtViewer";
import { UuidGenerator } from "./pages/codec/UuidGenerator";
import { HashTool } from "./pages/codec/HashTool";
import { UrlCodec } from "./pages/codec/UrlCodec";
import { CaseConverter } from "./pages/codec/CaseConverter";
import { JwtSigner } from "./pages/codec/JwtSigner";
import { FormatConverter } from "./pages/convert/FormatConverter";
import { JsonPath } from "./pages/convert/JsonPath";
import { CurlConverter } from "./pages/convert/CurlConverter";
import { CronNext } from "./pages/calc/CronNext";
import { Color } from "./pages/calc/Color";
import { Chmod } from "./pages/calc/Chmod";
import { Cidr } from "./pages/calc/Cidr";
import { MarkdownPreview } from "./pages/calc/MarkdownPreview";
import { HttpStatuses } from "./pages/misc/HttpStatuses";
import { MimeTypes } from "./pages/misc/MimeTypes";
import { Lorem } from "./pages/misc/Lorem";
import { QrCode } from "./pages/misc/QrCode";
import { TimeConverter } from "./pages/time/TimeConverter";
import { CronScheduler } from "./pages/time/CronScheduler";
import { MarkdownPdf } from "./pages/document/MarkdownPdf";
import { FakeData } from "./pages/fakeData/FakeData";

export function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/home" element={<Navigate to="/" replace />} />

        <Route path="/json-tools/json-validator" element={<Validator />} />
        <Route path="/json-tools/json-schema-generator" element={<SchemaGenerator />} />
        <Route path="/json-tools/json-sample-generator" element={<SampleGenerator />} />
        <Route path="/json-tools/json-converter" element={<Converter />} />
        <Route path="/json-tools/json-parser" element={<Parser />} />

        <Route path="/regex-tools/regex-checker" element={<RegexChecker />} />
        <Route path="/regex-tools/regex-generator" element={<RegexGenerator />} />

        <Route path="/string-tools/diff-viewer" element={<DiffViewer />} />
        <Route path="/string-tools/counter" element={<Counter />} />
        <Route path="/string-tools/column-extractor" element={<ColumnExtractor />} />
        <Route path="/string-tools/clean-text" element={<CleanText />} />
        <Route path="/string-tools/text-statistics" element={<TextStatistics />} />
        <Route path="/string-tools/random-number-generator" element={<RandomNumber />} />
        <Route path="/string-tools/random-string-generator" element={<RandomString />} />
        <Route path="/string-tools/shuffle-letters" element={<ShuffleLetters />} />

        <Route path="/base64" element={<Base64Page />} />
        <Route path="/jwt-viewer" element={<JwtViewer />} />
        <Route path="/jwt_viewer" element={<Navigate to="/jwt-viewer" replace />} />
        <Route path="/codec/uuid" element={<UuidGenerator />} />
        <Route path="/codec/hash" element={<HashTool />} />
        <Route path="/codec/url" element={<UrlCodec />} />
        <Route path="/codec/case" element={<CaseConverter />} />
        <Route path="/codec/jwt-signer" element={<JwtSigner />} />
        <Route path="/convert/format" element={<FormatConverter />} />
        <Route path="/convert/jsonpath" element={<JsonPath />} />
        <Route path="/convert/curl" element={<CurlConverter />} />
        <Route path="/calc/cron-next" element={<CronNext />} />
        <Route path="/calc/color" element={<Color />} />
        <Route path="/calc/chmod" element={<Chmod />} />
        <Route path="/calc/cidr" element={<Cidr />} />
        <Route path="/calc/markdown-preview" element={<MarkdownPreview />} />
        <Route path="/ref/http-statuses" element={<HttpStatuses />} />
        <Route path="/ref/mime-types" element={<MimeTypes />} />
        <Route path="/misc/lorem" element={<Lorem />} />
        <Route path="/misc/qr" element={<QrCode />} />

        <Route path="/time-converter" element={<TimeConverter />} />
        <Route path="/cron-scheduler" element={<CronScheduler />} />
        <Route path="/schedule_cron" element={<Navigate to="/cron-scheduler" replace />} />

        <Route path="/markdown-pdf-converter" element={<MarkdownPdf />} />

        <Route path="/fake-data-generator" element={<FakeData />} />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}
