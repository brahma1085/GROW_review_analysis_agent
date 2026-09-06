/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: "#00d09c",
        "primary-dark": "#00a87e",
        "on-primary": "#ffffff",
        "brand-dark": "#090d16",
        "card-dark": "#131b2e",
        "card-dark-subtle": "#1a243b",
        "border-dark": "#1e293b",
        "border-dark-light": "#334155",
        error: "#eb5757",
        "error-light": "#fef2f2",
        warning: "#f5a814",
        secondary: "#3247e2",
      },
      fontFamily: {
        body: ["Inter", "sans-serif"],
        heading: ["Plus Jakarta Sans", "sans-serif"],
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/container-queries')
  ],
}
