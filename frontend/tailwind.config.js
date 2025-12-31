/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        'hister-purple': '#8B5CF6',
        'hister-pink': '#EC4899',
        'hister-dark': '#1F2937',
      }
    },
  },
  plugins: [],
}
