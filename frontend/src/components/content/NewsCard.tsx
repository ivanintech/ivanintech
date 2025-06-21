"use client"; // Marcar como Client Component debido al onError en Image

import Link from "next/link";
import { cn } from "@/lib/utils";
import type { NewsItemRead } from "@/types";
import { StarRating } from "@/components/ui/StarRating";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

// Helper para formatear la fecha
const dateFormatter = new Intl.DateTimeFormat("es-ES", {
  year: "numeric",
  month: "long",
  day: "numeric",
});

// Helper para determinar las clases de tamaño de la tarjeta según el nivel de promoción
const getCardSizeClasses = (level: number | undefined): string => {
  switch (level) {
    case 2: // Nivel "Muy Importante"
      return "md:col-span-2 lg:col-span-3";
    case 1: // Nivel "Importante"
      return "md:col-span-2";
    default: // Nivel "Normal"
      return "md:col-span-1";
  }
};

interface NewsCardProps {
  item: NewsItemRead;
  className?: string;
}

export function NewsCard({ item, className }: NewsCardProps) {
  const formattedDate = item.publishedAt
    ? dateFormatter.format(new Date(item.publishedAt))
    : "Fecha no disponible";

  const sizeClasses = getCardSizeClasses(item.promotion_level);

  const finalClassName = cn(
    "border border-border rounded-lg overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 bg-card dark:bg-card group flex flex-col hover:scale-[1.02]",
    sizeClasses,
    className
  );

  return (
    <div className={finalClassName}>
      <Link
        href={item.url}
        target="_blank"
        rel="noopener noreferrer"
        className="block"
      >
        <div className="relative aspect-video bg-muted flex items-center justify-center text-muted-foreground overflow-hidden">
          {item.imageUrl ? (
            <img
              src={item.imageUrl}
              alt={`Imagen de la noticia: ${item.title}`}
              className="absolute top-0 left-0 w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
              loading="lazy"
            />
          ) : (
            <span className="text-xs">(Imagen no disponible)</span>
          )}
        </div>
      </Link>

      <div className="p-4 md:p-5 flex flex-col flex-grow">
        <h3 className="font-semibold mb-1 group-hover:text-primary transition-colors text-lg">
          <a href={item.url} target="_blank" rel="noopener noreferrer">
            {item.title}
          </a>
        </h3>

        <p className="text-xs text-muted-foreground mb-3">
          {item.sourceName || "Fuente desconocida"} • {formattedDate}
        </p>

        {item.description && (
          <p className="text-sm text-muted-foreground mb-4 line-clamp-3">
            {item.description}
          </p>
        )}

        {item.relevance_rating && item.relevance_rating >= 2.5 && (
          <StarRating rating={item.relevance_rating} className="mb-4" />
        )}

        <div className="mt-auto flex justify-between items-center pt-3 border-t">
          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-primary group-hover:underline"
          >
            Leer artículo →
          </a>
          {item.submitted_by && (
            <div className="flex items-center space-x-2">
              <span className="text-xs text-muted-foreground italic">por:</span>
              <a
                href={item.submitted_by.website_url || "#"}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-1.5 group/user"
              >
                <Avatar className="h-5 w-5">
                  <AvatarImage
                    src={item.submitted_by.avatar_url || undefined}
                    alt={item.submitted_by.full_name || "Avatar"}
                  />
                  <AvatarFallback>
                    {(item.submitted_by.full_name || "U").charAt(0)}
                  </AvatarFallback>
                </Avatar>
                <span className="text-xs font-medium text-muted-foreground group-hover/user:underline">
                  {item.submitted_by.full_name || "Usuario"}
                </span>
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
