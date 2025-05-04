'use client'; // Necesario por dangerouslySetInnerHTML y posibles scripts del widget

import { useEffect, useRef } from 'react';

interface SocialPostEmbedProps {
  /** El código HTML completo proporcionado por LinkedIn o X para incrustar. */
  embedHtml: string;
  /** Clases CSS adicionales para el contenedor del widget. */
  className?: string;
}

/**
 * Componente para renderizar de forma segura widgets incrustados de redes sociales (LinkedIn, X).
 * Utiliza dangerouslySetInnerHTML y maneja la posible ejecución de scripts.
 */
export function SocialPostEmbed({ embedHtml, className }: SocialPostEmbedProps) {
  const embedContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = embedContainerRef.current;
    if (!container) return;

    // Limpiar contenido previo (si acaso)
    container.innerHTML = '';

    // Crear un fragmento para añadir el HTML
    const fragment = document.createRange().createContextualFragment(embedHtml);

    // Buscar scripts dentro del fragmento
    const scripts = Array.from(fragment.querySelectorAll('script'));

    // Intenta encontrar el iframe DENTRO del fragmento antes de añadirlo
    const iframeElement = fragment.querySelector('iframe');

    // Añadir el contenido (sin scripts inicialmente)
    container.appendChild(fragment);

    // --- NUEVA LÓGICA PARA FORZAR ANCHO DEL IFRAME ---
    // Busca el iframe AHORA que está en el DOM del contenedor
    const iframeInContainer = container.querySelector('iframe');
    if (iframeInContainer) {
        iframeInContainer.style.width = '100%';
        iframeInContainer.style.maxWidth = '100%'; // Añadir max-width
        iframeInContainer.removeAttribute('width'); // Eliminar atributo width fijo
        // Podríamos intentar ajustar la altura también, pero es más arriesgado
        // iframeInContainer.style.height = 'auto'; // Podría romper el layout interno del embed
        // iframeInContainer.removeAttribute('height');
    }
    // --- FIN NUEVA LÓGICA ---

    // Ejecutar los scripts encontrados
    scripts.forEach(oldScript => {
      const newScript = document.createElement('script');
      // Copiar atributos importantes (src, async, etc.)
      Array.from(oldScript.attributes).forEach(attr => {
        newScript.setAttribute(attr.name, attr.value);
      });
      // Copiar contenido si es un script inline
      if (oldScript.textContent) {
        newScript.textContent = oldScript.textContent;
      }
      // Reemplazar el script original por uno nuevo para que se ejecute
      // O simplemente añadirlo al final del contenedor si el original ya está
      document.body.appendChild(newScript); // Añadir al body puede ser más robusto
                                             // O container.appendChild(newScript);
      // oldScript.parentNode?.replaceChild(newScript, oldScript);
    });

    // Limpieza al desmontar (opcional pero buena práctica)
    return () => {
      // Eliminar scripts añadidos al body si es posible rastrearlos
      // O simplemente vaciar el contenedor
      if(container) container.innerHTML = '';
    };

  }, [embedHtml]); // Re-ejecutar si el código embed cambia

  // Añadir w-full, flex, justify-center para centrar el contenido (iframe)
  return <div ref={embedContainerRef} className={`w-full flex justify-center ${className || ''}`} />;
} 