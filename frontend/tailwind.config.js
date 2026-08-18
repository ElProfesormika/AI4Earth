/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#07090b",
          900: "#0c1116",
          800: "#121920",
          700: "#1a232c",
          600: "#24303a",
        },
        ember: {
          400: "#ffb347",
          500: "#f08c2e",
          600: "#e85d25",
        },
        moss: {
          400: "#7ddea0",
          500: "#3dcc7a",
        },
        mist: {
          100: "#e8efe8",
          400: "#8a9aa3",
          500: "#6b7c86",
        },
      },
      fontFamily: {
        display: ["Syne", "sans-serif"],
        sans: ["Figtree", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "monospace"],
      },
      boxShadow: {
        glow: "0 0 40px rgba(232, 93, 37, 0.18)",
        panel: "0 24px 60px rgba(0,0,0,0.45)",
      },
    },
  },
  plugins: [],
};
