'use client'

import React from 'react'
import useEmblaCarousel from 'embla-carousel-react'
import Autoplay from 'embla-carousel-autoplay' // Opcional para autoplay
import Image from 'next/image'

// Array de imágenes a mostrar (¡asegúrate de que estén optimizadas!)
const images = [
  { src: '/img/ivan-graduated.jpg', alt: 'Iván en su graduación' },
  { src: '/img/ivan-pitching2.jpeg', alt: 'Iván dando una presentación' },
  { src: '/img/ivan-with-robot.webp', alt: 'Iván con un robot' },
    { src: '/img/ivan-on-ship.jpg', alt: 'Iván en un barco' },
    { src: '/img/ivan-on-thailand.jpeg', alt: 'Iván explorando Tailandia' },
    { src: '/img/ivan-on-ship.jpg', alt: 'Iván disfrutando de un chapuzón' },
  // Añade aquí más imágenes (optimizadas) cuando las tengas
  // { src: '/img/ivan-on-thailand-optimized.webp', alt: 'Iván en Tailandia' },
  // { src: '/img/ivan-in-pool-optimized.webp', alt: 'Iván en una piscina' },
];

export function PersonalCarousel() {
  // Usar el plugin Autoplay (opcional)
  const [emblaRef, emblaApi] = useEmblaCarousel({ loop: true }, [Autoplay()])

  return (
    <div className="overflow-hidden rounded-lg border border-border shadow-lg" ref={emblaRef}>
      <div className="flex">
        {images.map((img, index) => (
          // Cada slide ocupa todo el ancho, flex-shrink-0 evita que se encojan
          <div className="relative flex-grow-0 flex-shrink-0 w-full aspect-video bg-muted" key={index}>
            <Image
              src={img.src}
              alt={img.alt}
              layout="fill"
              objectFit="cover"
              className="block"
              // Añadir sizes si es necesario para optimización
            />
          </div>
        ))}
      </div>
      {/* Podríamos añadir botones de navegación o puntos aquí si quisiéramos */}
    </div>
  )
} 