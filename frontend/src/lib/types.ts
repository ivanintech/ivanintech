// src/lib/types.ts

// Interfaz para la estructura de datos de un proyecto
export interface Project {
  id: string;
  title: string;
  description?: string | null;
  imageUrl?: string | null;
  videoUrl?: string | null;
  githubUrl?: string | null;
  liveUrl?: string | null;
  technologies: string[];
}

// Interfaz para la estructura de datos de un post del blog
export interface BlogPost {
  id: number;
  title: string;
  slug: string;
  content: string;
  tags?: string | null;
  image_url?: string | null;
  linkedin_post_url?: string | null;
  status: string;
  author_id: number;
  published_date: string;
  last_modified_date?: string | null;
}

// Interfaz para un elemento de noticias (Alineada con API Backend)
export interface NewsItem {
  id: number | string;
  title: string;
  url: string;
  sourceName: string;
  description: string;
  publishedAt: string;
  imageUrl?: string | null;
  relevance_score?: number | null;
  time_category?: string | null;
  sectors?: any | null;
  sourceId?: string | null;
} 