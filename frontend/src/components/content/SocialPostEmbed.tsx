'use client';

import React from 'react';

interface SocialPostEmbedProps {
  /** El código HTML completo proporcionado por LinkedIn o X para incrustar. */
  embedHtml: string;
  /** Clases CSS adicionales para el contenedor del widget. */
  className?: string;
}

/**
 * Componente para renderizar de forma segura widgets incrustados de redes sociales (LinkedIn, X).
 * Utiliza dangerouslySetInnerHTML para renderizar el HTML del post.
 * NOTA: La visibilidad y el tamaño del iframe se controlan vía CSS global.
 */
export function SocialPostEmbed({ embedHtml, className }: SocialPostEmbedProps) {
  // El contenedor 'social-embed-container' será el objetivo de nuestro CSS global.
  return (
    <div
      className={`social-embed-container ${className || ''}`}
      dangerouslySetInnerHTML={{ __html: embedHtml }}
    />
  );
} 