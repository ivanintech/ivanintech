"use client"; // Marcar como Client Component debido al onError en Image

import Link from 'next/link';
import type { NewsItem } from '@/types'; // Usar el tipo correcto
import { cn } from '@/lib/utils'; // Para combinar clases condicionalmente
import { StarRating } from '@/components/ui/StarRating'; // Importar el nuevo componente

// Formateador de fecha (reutilizable)
const dateFormatter = new Intl.DateTimeFormat('es-ES', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
});

interface NewsCardProps {
  item: NewsItem; // Usar el tipo correcto NewsItem
  className?: string; // Mantenemos className para flexibilidad desde el padre
}

// Función para determinar el tamaño de la tarjeta basado en la calificación
const getCardSizeClasses = (rating: number | null | undefined): string => {
  if (rating && rating > 4.5) {
    // Estilo portada: ocupa más espacio en la cuadrícula en pantallas medianas y grandes
    return 'md:col-span-2 md:row-span-2';
  }
  if (rating && rating > 4) {
    // Estilo destacado: ocupa el doble de ancho en pantallas medianas y grandes
    return 'md:col-span-2';
  }
  // Tamaño por defecto
  return 'md:col-span-1';
};

export function NewsCard({ item, className }: NewsCardProps) {
  // Recibimos publishedAt como string
  let publishedDateObject: Date | null = null;
  try {
    // Intentar convertir el string publishedAt
    publishedDateObject = new Date(item.publishedAt);
  } catch (e) {
    console.error("Error converting publishedAt in NewsCard:", item.id, e);
  }

  // Validar fecha antes de formatear
  const formattedDate = publishedDateObject instanceof Date && !isNaN(publishedDateObject.getTime())
                        ? dateFormatter.format(publishedDateObject)
                        : 'Fecha inválida';

  const sizeClasses = getCardSizeClasses(item.relevance_rating);
  // Unimos las clases de tamaño con cualquier otra clase que se pase
  const finalClassName = cn(
    "block border border-border rounded-lg overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 bg-card dark:bg-card group flex flex-col hover:scale-[1.02]",
    sizeClasses, // Aplicamos las clases de tamaño dinámicas
    className
  );

  return (
    <Link 
      href={item.url || '#'} // <-- CORREGIDO: usar url
      target="_blank" // Abrir en nueva pestaña
      rel="noopener noreferrer" // Seguridad y SEO
      className={finalClassName} // Usamos las clases finales
    >
      {/* Imagen o Placeholder */}
      <div className={cn(
        "relative aspect-video bg-muted flex items-center justify-center text-muted-foreground overflow-hidden",
      )}>
        {item.imageUrl ? (
          <img 
              src={item.imageUrl}
              alt={`Imagen de la noticia: ${item.title}`}
              className="absolute top-0 left-0 w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
              loading="lazy"
              onError={(e) => { 
                 (e.target as HTMLImageElement).style.display = 'none'; 
                 const parentDiv = (e.target as HTMLImageElement).parentElement;
                 if (parentDiv) {
                   const placeholder = parentDiv.querySelector('.image-placeholder');
                   if (placeholder) (placeholder as HTMLElement).style.display = 'flex';
                 }
              }}
          />
        ) : (
          <span className="text-xs image-placeholder">(Imagen no disponible)</span> 
        )}
      </div>
      
      {/* Contenido */}
      <div className={cn(
        "p-4 md:p-5 flex flex-col flex-grow", // Ajustar padding
      )}>
        <h3 className={cn(
          "font-semibold mb-1 group-hover:text-primary transition-colors text-lg",
        )}>
          {item.title}
        </h3>
        
        {/* Fuente y Fecha */}
        <p className="text-xs text-muted-foreground mb-3">
          {item.sourceName || 'Fuente desconocida'} • {formattedDate}
        </p>
        {/* Descripción (opcional) */}
        {item.description && ( 
          <p className={cn(
            "text-sm text-muted-foreground mb-4 line-clamp-3",
          )}>
            {item.description}
          </p>
        )}
        
        {/* Rating de Estrellas (con condición) */}
        {item.relevance_rating && item.relevance_rating >= 2.5 && (
          <StarRating rating={item.relevance_rating} className="mb-4" />
        )}

        {/* Enlace Leer Artículo (con mt-auto para empujar al fondo) */}
        <span className="mt-auto text-sm font-medium text-primary group-hover:underline">
          Leer artículo →
        </span>
      </div>
    </Link>
  );
} 