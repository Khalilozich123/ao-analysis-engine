/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0a0a0b",
        surface: "#141416",
        elevated: "#1b1b1f",
        border: "#26262b",
        text: { DEFAULT: "#f4f4f5", muted: "#9a9aa4", dim: "#6b6b74" },
        accent: "#7c83ff",
        // Verdict semantics (text tone).
        strong: "#4ade80",   // Fort intérêt
        qualify: "#fbbf24",  // À qualifier
        weak: "#fb923c",     // Faible intérêt
        reject: "#f87171",   // Non pertinent
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
      },
      borderRadius: { card: "14px" },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(6px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        shimmer: { "100%": { transform: "translateX(100%)" } },
      },
      animation: {
        "fade-up": "fade-up 220ms cubic-bezier(0.22, 1, 0.36, 1)",
      },
    },
  },
  plugins: [],
};
