// src/types/index.ts (anteriormente lib/types.ts)

import { UserPublic } from './api'; // <-- Importar UserPublic
export * from './api'; // Re-exportar todos los tipos de la API

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
  updated_at: string;
}

// Interfaz para leer un BlogPost (corresponde a BlogPostRead del backend)
export interface BlogPostBase {
  title: string;
  content: string;
  excerpt?: string | null;
  tags?: string | null;
  image_url?: string | null;
  linkedin_post_url?: string | null;
  status?: string;
}

// Interfaz para leer un BlogPost (corresponde a BlogPostRead del backend)
export interface BlogPost extends BlogPostBase {
  id: string;
  author_id: number;
  slug: string;
  published_date: string; // O Date, si se transforma en el cliente
  last_modified_date?: string; // O Date
  author: {
    id: number;
    full_name: string | null;
  };
  url: string;
}

// Interfaz para crear un nuevo BlogPost (corresponde a BlogPostCreate del backend)
export type BlogPostCreate = BlogPostBase;

// Interfaz para un elemento de noticias (Alineada con API Backend)
export interface NewsItemRead {
  id: string;
  title: string;
  url: string;
  sourceName?: string;
  imageUrl?: string;
  description?: string;
  publishedAt: string; // O Date, si se convierte
  relevance_rating?: number;
  sectors?: string[];
  is_community?: boolean;
  submitted_by?: UserPublic;
  promotion_level?: number; // 0=normal, 1=destacado, 2=muy destacado
}

// Interfaz para crear un nuevo elemento de noticias (para enviar al backend)
export interface NewsItemSubmit {
  url: string;
}

export interface NewsItemCreate {
  title: string;
  url: string;
  description?: string | null;
  relevance_rating?: number | null;
  sectors?: string[] | null;
  is_community?: boolean;
  submitted_by_user_id?: number | null;
  publishedAt: string; // O Date, dependiendo de cómo lo manejes
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
  star_rating?: number;
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

// Interfaz para adaptar los posts de LinkedIn a lo que espera la Home
export interface HomePageBlogPost {
  id: string;
  slug: string;
  title: string;
  excerpt?: string;
  published_date: string;
  linkedInUrl?: string;
  embedCode?: string;
}

// Para la respuesta de la API de social login
// export interface SocialLoginResponse {
//   // ... existing code ...
// }

export type BlogPostUpdate = Partial<BlogPostCreate>;

// --- News ---
export interface NewsItem {
  id: number;
  title: string;
  url: string;
  sourceName?: string;
  imageUrl?: string;
  description?: string;
  publishedAt: string; // O Date, si se convierte
  relevance_rating?: number;
  sectors?: string[];
  is_community?: boolean;
  submitted_by?: UserPublic;
  promotion_level?: number; // 0=normal, 1=destacado, 2=muy destacado
}

export interface NewsItemUpdate {
  title?: string;
  url?: string;
  description?: string;
  imageUrl?: string;
  sectors?: string[];
  publishedAt?: string;
  sourceName?: string;
  sourceId?: string;
  is_community?: boolean;
  relevance_rating?: number;
  submitted_by_user_id?: number;
}

export interface ResourceVote {
    id: number;
    resource_link_id: string;
    user_id: number;
    vote_type: 'like' | 'dislike';
    created_at: string;
}

// --- Blog Suggestions (New) ---
export interface BlogSuggestion {
  id: string;
  title: string;
  content: string;
  excerpt?: string | null;
  tags?: string | null;
  image_url?: string | null;
  status: 'pending' | 'published' | 'rejected';
  source?: string | null;
  created_at: string;
  processed_at?: string | null;
  published_post_id?: string | null;
} 