/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0A0D12",
        panel: "#12161D",
        panel2: "#171C25",
        line: "#232938",
        line2: "#2B3242",
        mute: "#7B8496",
        mute2: "#5B6472",
        text: "#E8EAEF",
        accent: "#2DD4A8",
        accent2: "#F2545B",
        warn: "#E8B339",
      },
      fontFamily: {
        mono: ["JetBrains Mono", "IBM Plex Mono", "ui-monospace", "monospace"],
        sans: ["Inter", "ui-sans-serif", "system-ui"],
      },
      fontSize: {
        "2xs": ["0.6875rem", { lineHeight: "1rem" }],
      },
    },
  },
  plugins: [],
};