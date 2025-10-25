/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'space': {
          900: '#0f1419',
          800: '#1a1f2e',
          700: '#252b3a',
          600: '#303746',
        },
        'accent': {
          cyan: '#00d9ff',
          green: '#4ade80',
          yellow: '#facc15',
          red: '#ef4444',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}


