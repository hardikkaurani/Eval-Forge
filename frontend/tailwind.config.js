/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        editorial: {
          canvas: '#F6F4EE',
          pearl: '#DDE4E1',
          mist: '#B0C2C6',
          slate: '#7E939C',
          steel: '#4C5F6B',
          charcoal: '#2E3A44',
          accent: '#0284c7',
          'accent-hover': '#0369a1',
          'accent-glow': '#38bdf8',
          'dark-canvas': '#182026',
          'dark-surface': '#202a32',
          'dark-border': '#2e3a44',
        },
        chrome: {
          bg: '#182026',
          panel: '#202a32',
          border: '#2e3a44',
          text: '#F6F4EE',
          muted: '#7E939C',
          hover: '#2a3742',
          selected: '#344452',
        },
        workbench: {
          bg: '#F6F4EE',
          card: '#FFFFFF',
          border: '#DDE4E1',
          text: '#2E3A44',
          muted: '#4C5F6B',
        },
        brand: {
          terracotta: '#0284c7',
          'terracotta-hover': '#0369a1',
          sky: '#38bdf8',
          indigo: '#2e3a44',
        },
        well: {
          bg: '#12181d',
          border: '#2e3a44',
        },
      },
      fontFamily: {
        sans: ['"Source Sans 3"', '"Source Sans Pro"', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'],
        serif: ['"Source Sans 3"', '"Source Sans Pro"', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'],
        mono: ['"Source Code Pro"', '"JetBrains Mono"', 'monospace'],
        display: ['"Source Sans 3"', '"Source Sans Pro"', '-apple-system', 'sans-serif'],
        brand: ['"Source Sans 3"', '"Source Sans Pro"', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '0.375rem',
        sm: '0.25rem',
        md: '0.375rem',
        lg: '0.5rem',
        xl: '0.75rem',
        full: '9999px',
      },
      boxShadow: {
        subtle: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        chrome: '0 4px 12px 0 rgba(0, 0, 0, 0.3)',
      },
    },
  },
  plugins: [],
};
