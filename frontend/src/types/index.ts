// src/types/index.ts (anteriormente lib/types.ts)

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
  is_featured: boolean;
}

// Interfaz para leer un BlogPost (corresponde a BlogPostRead del backend)
export type BlogPost = {
  id: string; // Cambiado a string para coincidir con el backend
  title: string;
  slug: string;
  content: string;
  excerpt?: string | null; // Añadido para coincidir con BlogPostRead
  tags?: string | null;
  image_url?: string | null;
  linkedin_post_url?: string | null;
  status: string;
  author_id: number;
  published_date: string; // Se espera formato YYYY-MM-DD del backend
  last_modified_date?: string | null; // Se espera formato YYYY-MM-DD del backend
}

// Interfaz para crear un nuevo BlogPost (corresponde a BlogPostCreate del backend)
export interface BlogPostCreate {
  title: string;
  content: string;
  excerpt?: string | null;
  tags?: string | null;
  image_url?: string | null;
  linkedin_post_url?: string | null;
  status?: string; // Opcional, el backend tiene default 'published'
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
  relevance_rating?: number | null; // Calificación de 1 a 5
  sectors?: string[] | null;
  sourceId?: string | null;
}

// Interfaz para crear un nuevo elemento de noticias (para enviar al backend)
export interface NewsItemCreate {
  title: string;
  sourceUrl: string; // Corresponde a 'url' en NewsItem
  summary: string;   // Corresponde a 'description' en NewsItem
  publishedAt: string; // Debe ser un string ISO 8601
  imageUrl?: string | null;
  sectors?: string[]; // Lista de strings para los sectores
  sourceName?: string; // Opcional si el backend lo puede inferir o no es estrictamente necesario al crear
  // Añade otros campos que el backend espere para la creación
}

// Interfaz para ResourceLink (corresponde a ResourceLinkRead del backend)
export interface ResourceLink {
  id: string;
  title: string;
  url: string;
  ai_generated_description?: string | null;
  personal_note?: string | null;
  resource_type?: string | null;
  tags?: string | null;
  thumbnail_url?: string | null;
  created_at: string; // O Date, dependiendo de cómo se parsee
  author_id?: number | null;
  author_name?: string | null;
  is_pinned: boolean;
  is_ivan_recommended?: boolean | null;
  rating?: number | null;
  likes: number;
  dislikes: number;
  is_new?: boolean; // Se calculará en el frontend
}

// Interfaz básica para el Usuario (para el frontend)
export interface UserSession {
  id: number | string; // Podría ser int o string dependiendo de tu backend user ID
  email: string;
  full_name?: string | null;
  is_active: boolean;
  is_superuser: boolean; // o isAdmin, etc.
  token?: string; // <--- AÑADIR TOKEN AQUÍ
} 