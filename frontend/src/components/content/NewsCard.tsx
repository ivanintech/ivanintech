"use client"; // Marcar como Client Component debido al onError en Image

import Link from 'next/link';
import Image from 'next/image';
import type { NewsItem } from '@/lib/types'; // Usar el tipo correcto
import { cn } from '@/lib/utils'; // Para combinar clases condicionalmente

// Formateador de fecha (reutilizable)
const dateFormatter = new Intl.DateTimeFormat('es-ES', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
});

interface NewsCardProps {
  item: NewsItem; // Usar el tipo correcto NewsItem
  className?: string; // Para permitir estilos adicionales (ej. para la tarjeta destacada)
  isFeatured?: boolean; // Indicador opcional para estilos especiales
}

export function NewsCard({ item, className, isFeatured = false }: NewsCardProps) {
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

  return (
    <Link 
      href={item.url || '#'} // <-- CORREGIDO: usar url
      target="_blank" // Abrir en nueva pestaña
      rel="noopener noreferrer" // Seguridad y SEO
      className={cn(
        "block border border-border rounded-lg overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 bg-card dark:bg-card group flex flex-col hover:scale-[1.02]", // Usar bg-card, ajustar hover:scale
        isFeatured ? "md:flex-row" : "flex-col", // Layout horizontal en desktop si es destacada
        className // Aplicar clases adicionales
      )}
    >
      {/* Imagen o Placeholder */}
      <div className={cn(
        "relative aspect-video bg-muted flex items-center justify-center text-muted-foreground overflow-hidden",
        isFeatured ? "md:w-1/3 md:aspect-auto" : "w-full" // Ancho diferente si es destacada en desktop
      )}>
        {item.imageUrl ? ( // <-- CORREGIDO: usar imageUrl
          <Image 
              src={item.imageUrl} // <-- CORREGIDO: usar imageUrl
              alt={`Imagen de la noticia: ${item.title}`}
              fill // Usar fill para que la imagen cubra el div contenedor
              sizes={isFeatured ? "(max-width: 768px) 100vw, 33vw" : "100vw"} // Tamaños para optimización
              className="object-cover transition-transform duration-300 group-hover:scale-105"
              onError={(e) => { 
                 // Ocultar la imagen si falla la carga
                 (e.target as HTMLImageElement).style.display = 'none'; 
                 // Opcional: Mostrar un placeholder dentro del div padre
                 const parentDiv = (e.target as HTMLImageElement).parentElement;
                 if (parentDiv) {
                   const placeholder = parentDiv.querySelector('.image-placeholder');
                   if (placeholder) (placeholder as HTMLElement).style.display = 'flex';
                 }
              }}
          />
        ) : (
          // Placeholder explícito si no hay imagen
          <span className="text-xs image-placeholder">(Imagen no disponible)</span> 
        )}
         {/* Placeholder oculto para mostrar si la imagen falla (alternativa a onError directo) */} 
         {/* <span className="absolute inset-0 hidden items-center justify-center text-xs image-placeholder">(Error al cargar imagen)</span> */} 
      </div>
      
      {/* Contenido */}
      <div className={cn(
        "p-4 md:p-5 flex flex-col flex-grow", // Ajustar padding
        isFeatured ? "md:w-2/3" : "w-full" // Ancho diferente si es destacada en desktop
      )}>
        <h3 className={cn(
          "font-semibold mb-2 group-hover:text-primary transition-colors",
          isFeatured ? "text-xl md:text-2xl" : "text-lg" // Tamaño de título diferente
        )}>
          {item.title}
        </h3>
        {/* Fuente y Fecha */}
        <p className="text-xs text-muted-foreground mb-3">
          {item.sourceName || 'Fuente desconocida'} • {formattedDate} {/* <-- CORREGIDO: usar sourceName */}
        </p>
        {/* Descripción (opcional) */}
        {item.description && ( 
          <p className={cn(
            "text-sm text-muted-foreground mb-4",
            isFeatured ? "line-clamp-4" : "line-clamp-3" // Limitar líneas de descripción
          )}>
            {item.description}
          </p>
        )}
        {/* Enlace Leer Artículo */}
        <span className="mt-auto text-sm font-medium text-primary group-hover:underline">
          Leer artículo →
        </span>
      </div>
    </Link>
  );
} 