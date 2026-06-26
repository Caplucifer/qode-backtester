/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0B0E14",
        panel: "#11151F",
        panel2: "#161B27",
        line: "#232938",
        mute: "#6B7385",
        text: "#E6E9F0",
        accent: "#3FE0A5",
        accent2: "#FF6B5E",
        warn: "#E0B23F",
      },
      fontFamily: {
        mono: ["IBM Plex Mono", "ui-monospace", "monospace"],
        sans: ["Inter", "ui-sans-serif", "system-ui"],
      },
    },
  },
  plugins: [],
};
