import Link from 'next/link';
import Image from 'next/image';
import type { BlogPost } from '@/lib/types';

export function BlogPostPreview({ post }: { post: BlogPost }) {
  return (
    <Link 
      href={`/blog/${post.slug}`} 
      className="block border border-border rounded-lg overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 bg-muted/50 dark:bg-muted/10 group flex flex-col hover:scale-[1.03]"
    >
      {/* Imagen o Placeholder */}
      <div className="aspect-video bg-muted flex items-center justify-center text-muted-foreground overflow-hidden">
        {post.imageUrl ? (
          <Image 
              src={post.imageUrl}
              alt={`Imagen del post ${post.title}`}
              width={400} 
              height={225}
              className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
        ) : (
          <span className="text-xs">(Imagen Destacada)</span>
        )}
      </div>
      {/* Contenido */}
      <div className="p-5 flex flex-col flex-grow">
        <p className="text-xs text-muted-foreground mb-2">
          {new Date(post.date).toLocaleDateString('es-ES', { year: 'numeric', month: 'long', day: 'numeric' })}
        </p>
        <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">{post.title}</h3> {/* text-lg y font-semibold */}
        <p className="text-sm text-muted-foreground mb-4 flex-grow">{post.excerpt}</p>
        <span className="mt-auto text-sm font-medium text-primary group-hover:underline">
          Leer más →
        </span>
      </div>
    </Link>
  );
} 