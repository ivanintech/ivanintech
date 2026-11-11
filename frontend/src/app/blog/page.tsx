// ivanintech/frontend/src/app/blog/page.tsx
// Server Component: trae los posts en el servidor para que lleguen
// renderizados al HTML (SEO + sin parpadeo). El filtrado interactivo sigue
// en BlogClient.
import type { Metadata } from "next";
import BlogClient from "./BlogClient";
import { API_V1_URL } from "@/lib/api-client";
import type { BlogPost } from "@/types";

// La lista debe renderizarse en servidor en cada petición (o casi): si se
// prerenderiza en build, y en build el backend no responde, queda cacheada
// VACÍA durante el revalidate y el blog sale sin posts en el HTML.
export const dynamic = "force-dynamic";
export const revalidate = 0;

export const metadata: Metadata = {
  title: "Blog | Iván In Tech",
  description:
    "Artículos y publicaciones de Iván Castro sobre inteligencia artificial, desarrollo web, datos y tecnología.",
  alternates: { canonical: "https://ivanintech.com/blog" },
  openGraph: {
    title: "Blog | Iván In Tech",
    description:
      "Artículos y publicaciones de Iván Castro sobre inteligencia artificial, desarrollo web, datos y tecnología.",
    url: "https://ivanintech.com/blog",
    siteName: "Iván In Tech",
    type: "website",
    locale: "es_ES",
  },
  twitter: {
    card: "summary_large_image",
    title: "Blog | Iván In Tech",
    description:
      "Artículos y publicaciones sobre inteligencia artificial, desarrollo web, datos y tecnología.",
  },
};

interface BlogPostsApiResponse {
  items: BlogPost[];
}

/**
 * Carga los posts en el servidor. Degrada a [] en vez de lanzar: un backend
 * dormido (free tier) no debe tumbar la página; BlogClient los pedirá entonces
 * desde el navegador.
 */
async function getBlogPosts(): Promise<BlogPost[]> {
  // El free tier de Render tarda ~50 s en despertar el backend. Con un timeout
  // corto el fetch aborta, la página se renderiza sin posts y el blog queda
  // vacío para los buscadores. 70 s cubre el cold start con margen.
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 70000);
  try {
    const res = await fetch(`${API_V1_URL}/blog/?limit=100&status_filter=published`, {
      cache: "no-store",
      signal: controller.signal,
    });
    if (!res.ok) {
      console.error(`[blog] API respondió ${res.status}`);
      return [];
    }
    const data: BlogPostsApiResponse = await res.json();
    return data.items ?? [];
  } catch (error) {
    console.error("[blog] getBlogPosts degradado:", (error as Error)?.message);
    return [];
  } finally {
    clearTimeout(timeoutId);
  }
}

export default async function BlogPage() {
  const posts = await getBlogPosts();

  // JSON-LD para que los buscadores entiendan que es un listado de artículos.
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Blog",
    name: "Blog de Iván In Tech",
    url: "https://ivanintech.com/blog",
    author: {
      "@type": "Person",
      name: "Iván Castro",
      url: "https://ivanintech.com/sobre-mi",
    },
    blogPost: posts.slice(0, 20).map((p) => ({
      "@type": "BlogPosting",
      headline: p.title,
      datePublished: p.published_date,
      url: `https://ivanintech.com/blog/${p.slug}`,
      ...(p.excerpt ? { description: p.excerpt } : {}),
      ...(p.image_url ? { image: p.image_url } : {}),
    })),
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <BlogClient initialPosts={posts} />
    </>
  );
}
