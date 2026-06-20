/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0c1118",
        panel: "#141b26",
        panel2: "#1b2532",
        line: "#27323f",
        brand: "#2f9e6e",
        brand2: "#5b8cff",
        amber: "#e0a64b",
        muted: "#8a97a6",
        text: "#e8edf2",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "Segoe UI", "Arial", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      maxWidth: { content: "1160px" },
    },
  },
  plugins: [],
};
