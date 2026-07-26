/// <reference types="vite/client" />

// TypeScript 7 requires an explicit declaration for side-effect CSS imports
// like `import "./styles.css"`.
declare module "*.css";
