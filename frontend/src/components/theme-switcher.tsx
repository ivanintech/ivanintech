'use client'

import * as React from 'react'
import { useTheme } from 'next-themes'

// Iconos simples (podrían reemplazarse por una librería de iconos)
const SunIcon = () => <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5"><path d="M12 2.25a.75.75 0 0 1 .75.75v2.25a.75.75 0 0 1-1.5 0V3a.75.75 0 0 1 .75-.75ZM7.5 12a4.5 4.5 0 1 1 9 0 4.5 4.5 0 0 1-9 0ZM18.899 6.101a.75.75 0 0 0-1.06-1.06l-1.591 1.59a.75.75 0 1 0 1.06 1.061l1.591-1.59ZM21.75 12a.75.75 0 0 1-.75.75h-2.25a.75.75 0 0 1 0-1.5h2.25a.75.75 0 0 1 .75.75ZM17.838 17.838a.75.75 0 0 0-1.06-1.06l-1.59 1.59a.75.75 0 1 0 1.06 1.06l1.59-1.59ZM12 18a.75.75 0 0 1 .75.75V21a.75.75 0 0 1-1.5 0v-2.25A.75.75 0 0 1 12 18ZM7.758 17.838a.75.75 0 0 0-1.06 1.06l-1.59-1.591a.75.75 0 0 0-1.061 1.06l1.59 1.591a.75.75 0 0 0 1.061-1.06l1.59-1.59ZM6 12a.75.75 0 0 1-.75.75H3a.75.75 0 0 1 0-1.5h2.25A.75.75 0 0 1 6 12ZM6.101 5.04a.75.75 0 0 0-1.061 1.06l1.591 1.591a.75.75 0 0 0 1.06-1.061L6.101 5.04Z" /></svg>
const MoonIcon = () => <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5"><path fillRule="evenodd" d="M9.528 1.718a.75.75 0 0 1 .162.819A8.97 8.97 0 0 0 9 6a9 9 0 0 0 9 9 8.97 8.97 0 0 0 3.463-.69.75.75 0 0 1 .981.98 10.503 10.503 0 0 1-9.694 6.46c-5.799 0-10.5-4.7-10.5-10.5 0-3.51 1.713-6.622 4.43-8.566a.75.75 0 0 1 .818.162Z" clipRule="evenodd" /></svg>

export function ThemeSwitcher() {
  const [mounted, setMounted] = React.useState(false)
  const { theme, setTheme } = useTheme()

  // Evita hydration mismatch asegurando que el componente se renderice igual en servidor y cliente inicialmente
  React.useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    // Renderizar un placeholder o nada hasta que el cliente esté montado
    return <div className="w-9 h-9"></div> // Placeholder del mismo tamaño que el botón
  }

  return (
    <button
      aria-label="Toggle Dark Mode"
      type="button"
      className="p-2 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
    >
      {theme === 'dark' ? <SunIcon /> : <MoonIcon />}
    </button>
  )
} 