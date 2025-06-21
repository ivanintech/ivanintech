"use client"; // Marcar como Client Component debido al onError en Image

import { cn } from "@/lib/utils";
import type { NewsItemRead } from "@/types";
import { StarRating } from "@/components/ui/StarRating";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Globe, User, ExternalLink } from 'lucide-react';
import { Badge } from "@/components/ui/badge";

// Helper para formatear la fecha
const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('es-ES', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });
};

// Helper para determinar las clases de tamaño de la tarjeta según el nivel de promoción
const getCardSizeClasses = (rating: number | null | undefined): string => {
  if (rating && rating > 3.8) {
    return 'md:col-span-2 md:row-span-2';
  }
  if (rating && rating > 3.0) {
    return 'md:col-span-2';
  }
  return 'md:col-span-1';
};

interface NewsCardProps {
  item: NewsItemRead;
  className?: string;
}

export function NewsCard({ item, className }: NewsCardProps) {
  const sizeClasses = getCardSizeClasses(item.relevance_rating);

  const finalClassName = cn(
    'group relative flex h-full min-h-[350px] flex-col overflow-hidden rounded-lg border bg-card text-card-foreground shadow-sm transition-transform duration-300 ease-in-out hover:-translate-y-1',
    sizeClasses,
    className
  );

  return (
    <div className={finalClassName}>
      <a href={item.url} target="_blank" rel="noopener noreferrer" className="absolute inset-0 z-10">
        <span className="sr-only">Ver noticia</span>
      </a>

      {/* Imagen de fondo */}
      {item.imageUrl && (
        <div className="absolute inset-0">
          <img
            src={item.imageUrl}
            alt={item.title}
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent"></div>
        </div>
      )}

      {/* Contenido */}
      <div className="relative z-20 flex flex-1 flex-col justify-end p-4 text-white">
        <div className="flex-1"></div> {/* Espaciador para empujar contenido hacia abajo */}
        
        {/* Bloque del autor de la comunidad */}
        {item.is_community && item.submitted_by && (
          <div className="mb-2">
            {item.submitted_by.website_url ? (
              <a
                href={item.submitted_by.website_url}
                target="_blank"
                rel="noopener noreferrer"
                className="relative z-30 flex items-center space-x-2 text-xs text-gray-300 transition-colors hover:text-white"
                onClick={(e) => {
                  e.stopPropagation(); // Evita que el enlace principal de la tarjeta se active
                }}
              >
                <Avatar className="h-5 w-5 border-2 border-transparent group-hover:border-primary-foreground/50">
                  <AvatarImage src={item.submitted_by.avatar_url || ''} alt={item.submitted_by.full_name || 'Usuario'} />
                  <AvatarFallback><User className="h-3 w-3" /></AvatarFallback>
                </Avatar>
                <span className="font-semibold drop-shadow-sm">Por {item.submitted_by.full_name || 'Comunidad'}</span>
                <ExternalLink className="h-3 w-3 opacity-70 group-hover:opacity-100" />
              </a>
            ) : (
              <div className="relative z-30 flex items-center space-x-2 text-xs text-gray-300">
                <Avatar className="h-5 w-5">
                  <AvatarImage src={item.submitted_by.avatar_url || ''} alt={item.submitted_by.full_name || 'Usuario'} />
                  <AvatarFallback><User className="h-3 w-3" /></AvatarFallback>
                </Avatar>
                <span className="font-semibold drop-shadow-sm">Por {item.submitted_by.full_name || 'Comunidad'}</span>
              </div>
            )}
          </div>
        )}

        <h3 className="text-lg font-bold leading-tight drop-shadow-md">
          <a href={item.url} target="_blank" rel="noopener noreferrer" className="relative z-20">
            {item.title}
          </a>
        </h3>
        {item.description && (
          <p className="mt-2 text-sm text-gray-200 line-clamp-3 opacity-0 transition-opacity duration-300 group-hover:opacity-100 drop-shadow-sm">
            {item.description}
          </p>
        )}

        {/* Sectores (Tags) */}
        {item.sectors && (
          <div className="mt-3 flex flex-wrap gap-2">
            {(typeof item.sectors === 'string' ? JSON.parse(item.sectors) : item.sectors).slice(0, 4).map((sector: string, index: number) => (
              <Badge key={index} variant="secondary" className="text-xs backdrop-blur-sm">
                {sector}
              </Badge>
            ))}
          </div>
        )}

        <div className="mt-4 flex items-center justify-between">
          {item.relevance_rating && <StarRating rating={item.relevance_rating} />}
        </div>
      </div>
      
      {/* Footer */}
      <div className="relative z-20 flex items-center justify-between border-t border-white/10 bg-black/30 p-3 text-xs text-gray-300 backdrop-blur-sm">
        <div className="flex items-center space-x-2">
          <Globe className="h-4 w-4" />
          <span className="truncate">{item.sourceName || (item.url && new URL(item.url).hostname.replace('www.', ''))}</span>
        </div>
        <span>{formatDate(item.publishedAt)}</span>
      </div>
    </div>
  );
}
