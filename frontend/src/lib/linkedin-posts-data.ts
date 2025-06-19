import type { BlogPost, HomePageBlogPost } from '@/types';

/**
 * Extrae el URN de una URL de LinkedIn.
 * El URN es necesario para generar el código de inserción (embed).
 * Maneja diferentes formatos de URL de posts de actividad y de "share".
 * @param url - La URL del post de LinkedIn.
 * @returns El URN extraído o null si no se encuentra.
 */
function extractUrnFromLinkedInUrl(url: string): string | null {
  if (!url) return null;
  // Expresión regular mejorada para capturar 'urn:li:xxxx:numeros'
  // donde xxxx puede ser activity, share, ugcPost, etc.
  const urnMatch = url.match(/(urn:li:\w+:\d+)/);
  if (urnMatch && urnMatch[1]) {
    return urnMatch[1];
  }

  // Fallback para formatos no reconocidos que puedan tener el ID
  const genericIdMatch = url.match(/activity-([0-9]+)/) || url.match(/\/posts\/([0-9]+)/);
  if (genericIdMatch && genericIdMatch[1]) {
      return `urn:li:activity:${genericIdMatch[1]}`;
  }

  console.warn(`Could not extract URN from LinkedIn URL: ${url}`);
  return null;
}


/**
 * Adapta un objeto BlogPost (venido de la API) a un objeto HomePageBlogPost,
 * que es el formato que espera el componente de la página de inicio.
 * @param post - El objeto BlogPost.
 * @returns Un objeto HomePageBlogPost si la adaptación es exitosa, o null si no lo es (p.ej. no es un post de LinkedIn).
 */
export function adaptLinkedInPostForHomePage(post: BlogPost): HomePageBlogPost | null {
  if (!post.linkedin_post_url) {
    return null;
  }

  const urn = extractUrnFromLinkedInUrl(post.linkedin_post_url);

  // Si no se puede extraer el URN, no podemos mostrar el embed.
  // Podríamos decidir mostrarlo sin embed, pero por ahora lo omitimos.
  if (!urn) {
    return null;
  }

  return {
    id: post.id,
    slug: post.slug,
    title: post.title,
    excerpt: post.excerpt || `Actividad reciente en LinkedIn. Clica para ver más.`,
    published_date: post.published_date,
    linkedInUrl: post.linkedin_post_url,
    // Construimos el embedCode para que no tenga bordes y se adapte al 100%
    embedCode: `<iframe src="https://www.linkedin.com/embed/feed/update/${urn}" height="100%" width="100%" frameborder="0" allowfullscreen="" title="Publicación integrada" style="min-height: 400px; border: none;"></iframe>`,
  };
} 