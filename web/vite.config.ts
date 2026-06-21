import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { viteSingleFile } from "vite-plugin-singlefile";

// Single self-contained index.html: `sda graph view` injects data into it for an
// offline artifact; `sda graph serve` serves it alongside the read-only API.
export default defineConfig({
  plugins: [react(), tailwindcss(), viteSingleFile()],
});
