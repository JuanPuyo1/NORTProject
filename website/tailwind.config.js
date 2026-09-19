/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./core/templates/**/*.html",
    "./blog/templates/**/*.html",
    "./collaborate/templates/**/*.html",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        nort: {
          accent: "#7c3aed",
        },
      },
      maxWidth: {
        content: "1120px",
      },
    },
  },
  plugins: [require("@tailwindcss/typography"), require("daisyui")],
  daisyui: {
    themes: [
      {
        nort: {
          primary: "#0a0a0a",
          "primary-content": "#fafafa",
          secondary: "#f4f4f5",
          accent: "#7c3aed",
          neutral: "#0a0a0a",
          "base-100": "#ffffff",
          "base-200": "#f4f4f5",
          "base-300": "#e4e4e7",
          "base-content": "#0a0a0a",
        },
      },
    ],
  },
};
