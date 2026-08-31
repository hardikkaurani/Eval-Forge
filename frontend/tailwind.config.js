/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        chrome: {
          bg: '#0b1326',
          panel: '#131b2e',
          border: '#3e484f',
          text: '#dae2fd',
          muted: '#bdc8d1',
          hover: '#222a3d',
          selected: '#2d3449',
        },
        workbench: {
          bg: '#fdf8f8',
          card: '#f7f3f2',
          border: '#e5e2e1',
          text: '#1c1b1b',
          muted: '#444748',
        },
        brand: {
          terracotta: '#904c21',
          'terracotta-hover': '#783a0f',
          sky: '#38bdf8',
          indigo: '#3131c0',
        },
        well: {
          bg: '#060e20',
          border: '#2d3449',
        },
      },
      fontFamily: {
        sans: ['Geist', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
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
