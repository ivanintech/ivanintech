export interface HttpUrlString extends String {}

export interface BlogPost {
  id: string; // o number, según tu backend
  slug: string;
  title: string;
  content: string;
  author_id?: string | null;
  published_at?: string | null; // ISO date string
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
  image_url?: string | null;
  tags?: string | null; // o string[] si el backend devuelve un array
  is_published: boolean;
  is_featured?: boolean | null;
  linkedin_post_url?: string | null;
  // Si tienes datos del autor embebidos:
  // author?: { id: string; full_name?: string | null; email: string; } | null;
}

export interface User {
  id: string;
  email: string;
  full_name?: string | null;
  is_active: boolean;
  is_superuser: boolean;
  profile_picture_url?: string | null;
  linkedin_url?: string | null;
  github_username?: string | null;
  role?: string | null;
  created_at: string;
  updated_at: string;
}

// Otros tipos que puedas necesitar...

export interface ResourceLinkBase {
  url: string; // Changed from HttpUrlString for consistency with new structure
  title?: string | null;
  description?: string | null;
  personal_note?: string | null;
  ai_generated_summary?: string | null;
  ai_relevance_score?: number | null;
  ai_tags?: string[] | null;
  resource_type?: string | null;
  thumbnail_url?: string | null; // Changed from HttpUrlString
  user_id?: string | null;
  rating?: number | null;
  is_ivan_recommended?: boolean;
  ai_generated_description?: string | null;
  tags?: string | null;
}

export interface ResourceLinkCreate extends ResourceLinkBase {}

export interface ResourceLinkUpdate extends Partial<ResourceLinkBase> {}

export interface ResourceLinkRead extends ResourceLinkBase {
  id: string;
  created_at: string;
  updated_at: string;
  submitted_by_user?: User | null;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface Message {
  message: string;
}