"use client"; // Marcar como Client Component debido al onError en Image

import { cn } from "@/lib/utils";
import type { NewsItemRead } from "@/types";
import { StarRating } from "@/components/ui/StarRating";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Globe, User, ExternalLink, Pencil, Trash2 } from 'lucide-react';
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";
import SocialShareButtons from './SocialShareButtons';

// Helper para formatear la fecha
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return isNaN(date.getTime())
    ? "No date"
    : date.toLocaleDateString('en-US', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
      });
};

// Restaurar la función para tamaño dinámico
const getCardSizeClasses = (rating: number | null | undefined): string => {
  if (rating && rating > 4.5) return 'md:col-span-2 md:row-span-2';
  if (rating && rating > 3.8) return 'md:col-span-2';
  return 'md:col-span-1';
};

interface NewsCardProps {
  item: NewsItemRead;
  className?: string;
  onEdit: (item: NewsItemRead) => void;
  onDelete: (item: NewsItemRead) => void;
}

export function NewsCard({ item, className, onEdit, onDelete }: NewsCardProps) {
  const { user } = useAuth();
  const sizeClasses = getCardSizeClasses(item.relevance_rating);

  // Ocultar tarjetas con imagen placeholder
  if (item.imageUrl && item.imageUrl.includes('default-news.jpg')) return null;

  const finalClassName = cn(
    'group relative flex h-full min-h-[350px] flex-col overflow-hidden rounded-lg border bg-card text-card-foreground shadow-sm transition-transform duration-300 ease-in-out hover:-translate-y-1',
    sizeClasses,
    className // Permite sobreescribir desde la home
  );

  // Fecha robusta (solo publishedAt, según el tipo NewsItemRead)
  const publishedDate = item.publishedAt || "";

  return (
    <div className={finalClassName}>
      <a href={item.url} target="_blank" rel="noopener noreferrer" className="absolute inset-0 z-10">
        <span className="sr-only">View news</span>
      </a>

      {/* Botones de Admin y Compartir */}
      <div className="absolute top-2 right-2 z-30 flex items-center gap-2">
        <div onClick={(e) => { e.preventDefault(); e.stopPropagation(); }}>
          <SocialShareButtons
            url={item.url}
            title={item.title}
            description={item.description || ''}
          />
        </div>
        {user?.is_superuser && (
          <>
            <Button
              variant="outline"
              size="icon"
              className="h-8 w-8 bg-black/50 text-white hover:bg-black/70 hover:text-white"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onEdit(item);
              }}
            >
              <Pencil className="h-4 w-4" />
            </Button>
            <Button
              variant="destructive"
              size="icon"
              className="h-8 w-8"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onDelete(item);
              }}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </>
        )}
      </div>


      {/* Imagen de fondo */}
      {item.imageUrl && !item.imageUrl.includes('default-news.jpg') ? (
        <div className="absolute inset-0">
          <img
            src={item.imageUrl}
            alt={item.title}
            className="object-cover w-full h-full transition-transform duration-500 group-hover:scale-105"
            style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}
            loading="lazy"
            decoding="async"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent"></div>
        </div>
      ) : (
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-gray-800 to-gray-700">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-gray-500 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a4 4 0 004 4h10a4 4 0 004-4V7M16 3v4M8 3v4m-5 4h18" /></svg>
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
                  <AvatarImage src={item.submitted_by.avatar_url || ''} alt={item.submitted_by.full_name || 'User'} />
                  <AvatarFallback><User className="h-3 w-3" /></AvatarFallback>
                </Avatar>
                <span className="font-semibold drop-shadow-sm">By {item.submitted_by.full_name || 'Community'}</span>
                <ExternalLink className="h-3 w-3 opacity-70 group-hover:opacity-100" />
              </a>
            ) : (
              <div className="relative z-30 flex items-center space-x-2 text-xs text-gray-300">
                <Avatar className="h-5 w-5">
                  <AvatarImage src={item.submitted_by.avatar_url || ''} alt={item.submitted_by.full_name || 'User'} />
                  <AvatarFallback><User className="h-3 w-3" /></AvatarFallback>
                </Avatar>
                <span className="font-semibold drop-shadow-sm">By {item.submitted_by.full_name || 'Community'}</span>
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
          <StarRating rating={item.relevance_rating ?? 0} />
        </div>
      </div>
      
      {/* Footer */}
      <div className="relative z-20 flex items-center justify-between border-t border-white/10 bg-black/30 p-3 text-xs text-gray-300 backdrop-blur-sm">
        <div className="flex items-center space-x-2">
          <Globe className="h-4 w-4" />
          <span className="truncate">{item.sourceName || (item.url && new URL(item.url).hostname.replace('www.', ''))}</span>
        </div>
        {publishedDate && formatDate(publishedDate) !== "No date" && (
          <span>{formatDate(publishedDate)}</span>
        )}
      </div>
    </div>
  );
}
