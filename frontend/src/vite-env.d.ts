/// <reference types="vite/client" />
/// <reference types="react" />
/// <reference types="react-dom" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_QRZ_LOOKUP_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
