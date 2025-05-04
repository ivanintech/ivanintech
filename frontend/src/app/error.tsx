'use client' // Los archivos error.tsx deben ser Client Components

import { useEffect } from 'react'
import { Button } from '@/components/ui/button' // Reutilizar el botón

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string } // El error incluye un digest en producción para correlación
  reset: () => void // Función para intentar re-renderizar el segmento
}) {
  useEffect(() => {
    // Opcional: Registrar el error en un servicio de reporting
    console.error('[Global Error Boundary]:', error)
  }, [error])

  return (
    <div className="container mx-auto px-4 py-16 min-h-[calc(100vh-200px)] flex flex-col items-center justify-center text-center">
      <h2 className="text-2xl font-semibold text-destructive mb-4">¡Ups! Algo salió mal</h2>
      <p className="text-muted-foreground mb-6">
        Ocurrió un error al intentar cargar esta sección.
      </p>
      {/* Opcional: Mostrar detalles del error en desarrollo */}
      {process.env.NODE_ENV === 'development' && (
        <details className="mb-6 text-sm text-muted-foreground/70 bg-muted/50 p-3 rounded border w-full max-w-md">
          <summary>Detalles del error (dev)</summary>
          <pre className="mt-2 text-left whitespace-pre-wrap break-words">
            {error?.message}
            {error?.stack ? `\nStack:\n${error.stack}` : ''}
          </pre>
        </details>
      )}
      <Button
        onClick={() => reset()} // Intentar recuperar re-renderizando
        variant="outline"
      >
        Intentar de nuevo
      </Button>
    </div>
  )
} 