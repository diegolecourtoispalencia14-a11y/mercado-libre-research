export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        flamante: {
          flame: "#F65058",
          "flame-hover": "#E03E46",
          "flame-light": "rgba(246, 80, 88, 0.12)",
          dark: "#090A0F",
          card: "#12141D",
          "card-hover": "#181B26",
          border: "rgba(255, 255, 255, 0.08)",
          "border-hover": "rgba(255, 255, 255, 0.18)",
          mint: "#10B981",
          amber: "#F59E0B",
          cyan: "#06B6D4",
        },
      },
      fontFamily: {
        sans: ["Plus Jakarta Sans", "system-ui", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      boxShadow: {
        glow: "0 0 25px rgba(246, 80, 88, 0.25)",
        "glow-sm": "0 0 15px rgba(246, 80, 88, 0.18)",
        "glow-mint": "0 0 20px rgba(16, 185, 129, 0.2)",
      },
    },
  },
  plugins: [],
}


