import Image from 'next/image';
import { notFound } from 'next/navigation'; // Para manejar posts no encontrados
// import { blogPostsData } from '@/lib/blog-data'; // Ya no se usa
import type { BlogPost } from '@/types';
import apiClient from '@/lib/api-client'; // Importar el nuevo cliente de API

interface ApiError extends Error {
  response?: {
    status: number;
  };
}

// Función para obtener los datos del post basado en el slug desde la API
async function getPostData(slug: string): Promise<BlogPost | undefined> {
  try {
    const post = await apiClient<BlogPost>(`/content/blog/${slug}`);
    return post;
  } catch (error) {
    const apiError = error as ApiError;
    // Si el cliente de API devuelve un error con status 404, el post no existe
    if (apiError.response && apiError.response.status === 404) {
      return undefined;
    }
    // Para otros errores, lanzamos una excepción para que la maneje error.tsx
    console.error(`Detailed error in getPostData for slug ${slug}:`, error);
    throw new Error(`Could not load post '${slug}'.`); 
  }
}

// Definir el tipo para las props de la página
type BlogPostPageProps = {
  params: {
    slug: string;
  };
};

// Opcional: Generar metadatos dinámicos para SEO
export async function generateMetadata({ params }: BlogPostPageProps) {
  try {
    // Necesitamos manejar el error aquí también o la build podría fallar
    const post = await getPostData(params.slug);
    if (!post) {
      return { title: 'Post not found' };
    }
    // Usar el inicio del contenido como descripción si existe, o un fallback
    const description = post.content 
      ? post.content.substring(0, 155) + '...' 
      : 'Read the full post on Iván In Tech.';
    return {
      title: `${post.title} | Iván In Tech Blog`,
      description: description, 
    };
  } catch (error) {
     console.error("Error generating metadata for post:", params.slug, error);
     // Devolver título genérico en caso de error al generar metadatos
     return { title: 'Error loading post | Iván In Tech Blog' };
  }
}

// Componente de la página del post
export default async function BlogPostPage({ params }: BlogPostPageProps) {
  // Si getPostData lanza error (que no sea 404), se mostrará error.tsx
  const post = await getPostData(params.slug);

  // Si el post no se encuentra (getPostData devolvió undefined por 404)
  if (!post) {
    notFound();
  }

  // Usar el contenido del post directamente. Asumimos que viene como HTML o Markdown procesable.
  // Si es Markdown, necesitarías una librería para renderizarlo de forma segura.
  const postContentHtml = post.content || '<p class="mt-4 italic text-foreground/60">(Content not available)</p>';

  return (
    <article className="container mx-auto px-4 py-16 max-w-3xl">
      {/* Imagen destacada (opcional) */}
      {post.image_url && (
        <div className="mb-8">
          <Image
            src={post.image_url}
            alt={`Featured image for ${post.title}`}
            width={768} // Ancho más grande para la página del post
            height={400}
            className="w-full h-auto rounded-lg object-cover shadow-md"
            priority // Cargar con prioridad si es la imagen principal
          />
        </div>
      )}
      
      {/* Encabezado del Post */}
      <h1 className="text-3xl md:text-4xl font-bold mb-4 text-primary">{post.title}</h1>
      <p className="text-foreground/60 mb-8">
        Published on {new Date(post.published_date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
      </p>

      {/* Contenido del Post */}
      <div 
        className="prose prose-lg max-w-none text-foreground prose-p:text-foreground/90 prose-a:text-primary hover:prose-a:text-primary/80 prose-strong:text-foreground prose-headings:text-foreground prose-blockquote:border-primary prose-blockquote:text-foreground/80 dark:prose-invert dark:prose-a:text-primary dark:hover:prose-a:text-primary/80"
        dangerouslySetInnerHTML={{ __html: postContentHtml }} // ¡CUIDADO! Asegúrate que el HTML es seguro.
      />

      {/* LinkedIn Post Embed */}
      {post.linkedin_post_url && (
        <div className="mt-12">
          <h2 className="text-2xl font-bold mb-4 text-foreground">LinkedIn Post</h2>
          <iframe 
            src={post.linkedin_post_url}
            height="500" // Puedes ajustar la altura
            width="100%"
            frameBorder="0" 
            allowFullScreen
            title="Embedded LinkedIn Post"
            className="w-full rounded-lg shadow-md"
          ></iframe>
        </div>
      )}

      {/* TODO: Añadir navegación (post anterior/siguiente), comentarios, etc. */}
    </article>
  );
}

// Opcional pero recomendado: Generar rutas estáticas en build time si los posts no cambian a menudo
// export async function generateStaticParams() {
//   return blogPostsData.map((post) => ({
//     slug: post.slug,
//   }));
// }

// Ya no necesitamos generar rutas estáticas de esta forma si los posts son dinámicos
// o si queremos que siempre se obtengan frescos del servidor.
// Si quisiéramos pre-renderizar algunos slugs populares, podríamos obtenerlos de la API aquí.
/*
export async function generateStaticParams() {
  // Ejemplo: obtener slugs de la API (necesitaríamos un endpoint para esto)
  // const res = await fetch(`${API_V1_URL}/content/blog-slugs`);
  // const slugs = await res.json();
  // return slugs.map((slug: string) => ({ slug }));

  // O si aún usamos los datos mock (temporalmente):
  // return blogPostsData.map((post) => ({
  //   slug: post.slug,
  // }));
  return []; // Deshabilitar SSG por ahora
}
*/ 