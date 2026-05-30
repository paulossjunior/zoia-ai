import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{vue,ts}'],
  theme: {
    extend: {
      colors: {
        ink: '#18202f',
        panel: '#f7f8fa',
        line: '#d8dde5',
        success: '#198754',
        warning: '#b7791f',
        danger: '#c2413a'
      },
      boxShadow: {
        subtle: '0 1px 2px rgb(16 24 40 / 0.08)'
      }
    }
  },
  plugins: []
} satisfies Config
