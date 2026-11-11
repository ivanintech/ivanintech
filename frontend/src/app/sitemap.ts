// ivanintech/frontend/src/app/sitemap.ts
// Genera /sitemap.xml con las rutas estáticas + los 41 posts del blog.
// Next lo sirve automáticamente en https://ivanintech.com/sitemap.xml
import type { MetadataRoute } from "next";
import { API_V1_URL } from "@/lib/api-client";
import type { BlogPost } from "@/types";

const BASE_URL = "https://ivanintech.com";

export const revalidate = 3600;

interface BlogPostsApiResponse {
  items: BlogPost[];
}

async function getBlogPosts(): Promise<BlogPost[]> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 70000);
  try {
    const res = await fetch(`${API_V1_URL}/blog/?limit=200&status_filter=published`, {
      cache: "no-store",
      signal: controller.signal,
    });
    if (!res.ok) return [];
    const data: BlogPostsApiResponse = await res.json();
    return data.items ?? [];
  } catch {
    return [];
  } finally {
    clearTimeout(timeoutId);
  }
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const staticRoutes: MetadataRoute.Sitemap = [
    { url: BASE_URL, changeFrequency: "weekly", priority: 1 },
    { url: `${BASE_URL}/portfolio`, changeFrequency: "monthly", priority: 0.9 },
    { url: `${BASE_URL}/sobre-mi`, changeFrequency: "monthly", priority: 0.8 },
    { url: `${BASE_URL}/blog`, changeFrequency: "daily", priority: 0.9 },
    { url: `${BASE_URL}/noticias`, changeFrequency: "daily", priority: 0.7 },
    { url: `${BASE_URL}/recursos`, changeFrequency: "weekly", priority: 0.7 },
    { url: `${BASE_URL}/contacto`, changeFrequency: "yearly", priority: 0.5 },
  ];

  const posts = await getBlogPosts();
  const postRoutes: MetadataRoute.Sitemap = posts.map((p) => ({
    url: `${BASE_URL}/blog/${p.slug}`,
    lastModified: p.published_date ? new Date(p.published_date) : undefined,
    changeFrequency: "monthly" as const,
    priority: 0.6,
  }));

  return [...staticRoutes, ...postRoutes];
}
