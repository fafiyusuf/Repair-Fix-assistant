/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f9f871',
          100: '#F9F871',
          200: '#C0D360',
          300: '#8CAD51',
          400: '#5F8841',
          500: '#386331',
          600: '#174020',
          700: '#123319',
          800: '#0d2612',
          900: '#08190c',
        },
        // ChatGPT-style dark sidebar
        sidebar: {
          DEFAULT: '#171717',
          hover: '#212121',
          border: '#2f2f2f',
        },
        chat: {
          bg: '#212121',
          user: '#2f2f2f',
          assistant: '#171717',
        }
      },
    },
  },
  plugins: [],
}
