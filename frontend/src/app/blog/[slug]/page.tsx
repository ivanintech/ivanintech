import Image from 'next/image';
import { notFound } from 'next/navigation'; // Para manejar posts no encontrados
// import { blogPostsData } from '@/lib/blog-data'; // Ya no se usa
import type { BlogPost } from '@/types';
import { API_V1_URL } from '@/lib/api-client'; // Importar URL base

// Función para obtener los datos del post basado en el slug desde la API (¡Ahora lanza errores!)
async function getPostData(slug: string): Promise<BlogPost | undefined> {
  let res: Response | undefined;
  try {
    res = await fetch(`${API_V1_URL}/content/blog/${slug}`, {
      next: { revalidate: 3600 } 
    });

    // Si la API devuelve 404, el post no existe (manejado por notFound() en la página)
    if (res.status === 404) {
      return undefined;
    }

    // Para otros errores de respuesta HTTP
    if (!res.ok) {
      throw new Error(`Error ${res.status}: Failed to fetch post '${slug}' (${res.statusText})`);
    }

    return await res.json();

  } catch (error) {
    // Capturar error de red o el error lanzado arriba
    console.error(`Detailed error in getPostData for slug ${slug}:`, error);
    // Si el error ya fue lanzado por !res.ok, podríamos querer mostrar ese mensaje más específico
    // Pero por simplicidad y para el error.tsx, lanzamos uno genérico.
    // Nota: Si el status fue 404, no llegamos aquí porque retornamos undefined antes.
    throw new Error(`Could not load post '${slug}'.`); 
  }
}

// Opcional: Generar metadatos dinámicos para SEO
export async function generateMetadata({ params }: { params: { slug: string } }) {
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
export default async function BlogPostPage({ params }: { params: { slug: string } }) {
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