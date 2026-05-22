/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f4f8',
          100: '#dbe3f0',
          200: '#bccce3',
          300: '#90acd1',
          400: '#6488bd',
          500: '#4368a5',
          600: '#345187',
          700: '#2c426f',
          800: '#27395d',
          900: '#233250',
          950: '#141d30',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
