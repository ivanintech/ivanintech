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
export interface NewsItemRead {
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