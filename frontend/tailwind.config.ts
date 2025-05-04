import type { Config } from 'tailwindcss';
import defaultTheme from 'tailwindcss/defaultTheme'; // Importar el tema por defecto completo

// Helper para convertir variables CSS a formato Tailwind
function hsl(variableName: string) {
  return `hsl(var(${variableName}) / <alpha-value>)`; // Usar HSL es más flexible con opacidad
}

const config: Config = {
  darkMode: 'class', // Habilitar dark mode basado en clase
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        // Usar la fuente del tema por defecto
        sans: ['var(--font-inter)', ...defaultTheme.fontFamily.sans],
      },
      colors: {
        // Mantener colores base
        background: hsl('--background'),
        foreground: hsl('--foreground'),
        primary: {
          DEFAULT: hsl('--primary'),
          foreground: hsl('--primary-foreground'),
        },
        accent: {
          DEFAULT: hsl('--accent'),
          foreground: hsl('--accent-foreground'),
        },
        muted: {
          DEFAULT: hsl('--muted'),
          foreground: hsl('--muted-foreground'),
        },
        // Añadir borderColor
        borderColor: {
          DEFAULT: hsl('--border'), // Usar la variable CSS como color de borde por defecto
          primary: hsl('--primary'), // Opcional: borde primario
          // ... otros colores de borde si son necesarios
        },
        // Añadir más colores si es necesario (muted, destructive, etc.)
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic':
          'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'), // Añadir el plugin de tipografía
  ],
};
export default config; 