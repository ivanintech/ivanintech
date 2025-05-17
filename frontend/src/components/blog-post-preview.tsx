import Link from 'next/link';
import Image from 'next/image';
// import type { BlogPost } from '@/lib/types'; // Comentado o eliminado
import type { HomePageBlogPost } from '@/lib/linkedin-posts-data';

// Tipo más flexible para el post
// Usaremos directamente el tipo BlogPost de @/lib/types y HomePageBlogPost para claridad
// y el componente decidirá cómo manejarlo.
export type PreviewPostType = import('@/lib/types').BlogPost | HomePageBlogPost;

interface BlogPostPreviewProps {
  post: PreviewPostType;
  isLinkedInEmbed?: boolean;
  linkedInUrl?: string; 
  embedCode?: string;
}

export function BlogPostPreview({ post, isLinkedInEmbed, linkedInUrl, embedCode }: BlogPostPreviewProps) {
  let displayDate = 'Fecha inválida';
  // El campo de fecha es 'published_date' en ambos tipos que nos interesan.
  // En BlogPost (de API) puede ser string o Date. En HomePageBlogPost es string (ISO).
  const dateValue = post.published_date;

  if (dateValue) {
    try {
      const dateToFormat = new Date(dateValue);
      if (!isNaN(dateToFormat.getTime())) {
        displayDate = dateToFormat.toLocaleDateString('es-ES', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
        });
      }
    } catch (e) {
      console.error("Error formateando fecha en BlogPostPreview:", post.title, dateValue, e);
    }
  }

  const linkProps = isLinkedInEmbed && linkedInUrl
    ? { href: linkedInUrl, target: "_blank" as const, rel: "noopener noreferrer" }
    : { href: `/blog/${post.slug}` }; // slug existe en ambos tipos

  // image_url es opcional en ambos casos o puede ser null.
  const imageUrl = 'image_url' in post ? post.image_url : null;
  
  // Lógica mejorada para excerptText para asegurar que sea string
  const excerptValue = ('excerpt' in post && typeof post.excerpt === 'string' && post.excerpt) 
    ? post.excerpt 
    : (('description' in post && typeof post.description === 'string' && post.description) ? post.description : undefined);
  const excerptText: string = excerptValue || '';

  return (
    <div
      className="block border border-border rounded-lg overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 bg-muted/50 dark:bg-muted/10 group flex flex-col hover:scale-[1.03] h-full"
    >
      {isLinkedInEmbed && embedCode ? (
        <div 
          className="aspect-video bg-muted overflow-hidden w-full linkedin-embed-container"
          dangerouslySetInnerHTML={{ __html: embedCode }}
        />
      ) : (
        <Link {...linkProps} className="block aspect-video bg-muted flex items-center justify-center text-muted-foreground overflow-hidden">
          {imageUrl ? (
          <Image 
                src={imageUrl}
              alt={`Imagen del post ${post.title}`}
              width={400} 
              height={225}
              className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
        ) : (
          <span className="text-xs">(Imagen Destacada)</span>
        )}
        </Link>
      )}
      <div className="p-5 flex flex-col flex-grow">
        <p className="text-xs text-muted-foreground mb-2">
          {displayDate}
        </p>
        <Link {...linkProps}>
          <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors cursor-pointer">{post.title}</h3> 
        </Link>
        <p className="text-sm text-muted-foreground mb-4 flex-grow">{excerptText}</p>
        <Link
          {...linkProps}
          className="mt-auto text-sm font-medium text-primary group-hover:underline cursor-pointer"
        >
          Leer más →
        </Link>
      </div>
    </div>
  );
} 