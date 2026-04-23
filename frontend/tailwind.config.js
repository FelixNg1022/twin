/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        imessage: {
          blue: "#007aff",
          grey: "#e5e5ea",
        },
      },
      fontFamily: {
        sf: [
          "-apple-system",
          "SF Pro Display",
          "SF Pro Text",
          "system-ui",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};
