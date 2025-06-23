'use client';

import type { BlogPost } from '@/types';
import { BlogPostPreview } from '@/components/blog/BlogPostPreview';
import { SocialPostEmbed } from '@/components/blog/SocialPostEmbed';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { ArrowRight, Pencil, Trash2 } from 'lucide-react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { format } from "date-fns";
import { es } from "date-fns/locale";

interface ArticleCardProps {
  post: BlogPost;
  onEdit: (post: BlogPost) => void;
  onDelete: (post: BlogPost) => void;
  className?: string;
}

/**
 * Extrae el URN de una URL de LinkedIn.
 * El URN es necesario para generar el código de inserción (embed).
 */
function extractUrnFromLinkedInUrl(url: string): string | null {
    if (!url) return null;
    const urnMatch = url.match(/(urn:li:\w+:\d+)/);
    if (urnMatch && urnMatch[1]) {
      return urnMatch[1];
    }
    const genericIdMatch = url.match(/activity-([0-9]+)/) || url.match(/\/posts\/([0-9]+)/);
    if (genericIdMatch && genericIdMatch[1]) {
        return `urn:li:activity:${genericIdMatch[1]}`;
    }
    console.warn(`Could not extract URN from LinkedIn URL: ${url}`);
    return null;
}

/**
 * Construye el código de inserción (embed) para un post de LinkedIn.
 */
function getLinkedInEmbedCode(url: string): string | null {
    // Solo intentar si es una URL de LinkedIn
    if (!url || !url.includes('linkedin.com')) {
        return null;
    }
    const urn = extractUrnFromLinkedInUrl(url);
    if (!urn) return null;
    return `<iframe src="https://www.linkedin.com/embed/feed/update/${urn}" height="100%" width="100%" frameborder="0" allowfullscreen="" title="Publicación integrada" style="min-height: 500px; border: none;"></iframe>`;
}

export function ArticleCard({ post, onEdit, onDelete, className }: ArticleCardProps) {
  const { user } = useAuth();
  const embedCode = post.linkedin_post_url ? getLinkedInEmbedCode(post.linkedin_post_url) : null;

  if (embedCode) {
    let formattedDate = "Fecha no disponible";
    try {
      formattedDate = format(new Date(post.published_date), "d 'de' MMMM 'de' yyyy", { locale: es });
    } catch {
      console.error("Invalid date for post:", post.title, post.published_date);
    }
    
    return (
        <Card className={`flex flex-col h-full overflow-hidden transition-shadow duration-300 ease-in-out hover:shadow-lg min-h-[550px] ${className}`}>
            <CardHeader>
                <CardTitle className="text-xl font-bold leading-tight">
                    <Link
                        href={`/blog/${post.slug}`}
                        className="hover:text-primary transition-colors duration-200"
                        legacyBehavior>
                        {post.title}
                    </Link>
                </CardTitle>
                <p className="text-sm text-muted-foreground pt-1">{formattedDate}</p>
            </CardHeader>
            <CardContent className="flex-grow p-0 relative">
                <div className="h-full">
                    <SocialPostEmbed embedHtml={embedCode} />
                </div>
            </CardContent>
            <CardFooter className="flex flex-col items-start mt-auto pt-4 border-t">
                <div className="flex justify-between w-full items-center">
                    <div className="flex flex-wrap gap-1">
                        {post.tags && post.tags.split(',').map((tag: string) => (
                        <Badge key={tag.trim()} variant="secondary">{tag.trim()}</Badge>
                        ))}
                    </div>
                    <Link
                        href={`/blog/${post.slug}`}
                        className="flex items-center text-sm font-semibold text-primary hover:underline shrink-0"
                        legacyBehavior>
                        Leer más
                        <ArrowRight className="w-4 h-4 ml-1" />
                    </Link>
                </div>
                {user?.is_superuser && (
                  <div className="flex gap-2 mt-4 self-end w-full justify-end">
                      <Button variant="outline" size="sm" onClick={() => onEdit(post)}>
                          <Pencil className="w-4 h-4 mr-1" />
                          Editar
                      </Button>
                      <Button variant="destructive" size="sm" onClick={() => onDelete(post)}>
                          <Trash2 className="w-4 h-4 mr-1" />
                          Eliminar
                      </Button>
                  </div>
                )}
            </CardFooter>
        </Card>
    );
  }

  return (
    <BlogPostPreview 
      post={post}
      onEdit={onEdit}
      onDelete={onDelete}
      className={className}
    />
  );
} 