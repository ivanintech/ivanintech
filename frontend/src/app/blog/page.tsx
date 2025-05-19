// ivanintech/frontend/src/app/blog/page.tsx
// --- COMPONENTE BlogPage ---
'use client';

import { useState, useMemo, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
// Quitar datos de LinkedIn si vamos a reemplazarlos o complementarlos
// import { getProcessedLinkedInPosts, type ProcessedLinkedInPost } from '@/lib/linkedin-posts-data';
import { SocialPostEmbed } from '@/components/content/SocialPostEmbed';
import Link from 'next/link';

// Nuevas importaciones para Blog tradicional
import { useAuth } from '@/context/AuthContext';
import { PlusCircle } from 'lucide-react';
import { API_V1_URL } from '@/lib/api-client'; // Para la URL base de la API
import type { BlogPost, BlogPostCreate } from '@/lib/types'; // Tipos para blog
import { AddBlogPostModal } from '@/components/admin/AddBlogPostModal'; // <--- IMPORTAR EL MODAL
import { toast } from 'sonner'; // Para notificaciones

// Mantener funciones de fecha si son necesarias para agrupar los nuevos blog posts
function getStartOfDay(date: Date): Date {
  const start = new Date(date);
  start.setHours(0, 0, 0, 0);
  return start;
}
function getStartOfWeek(date: Date): Date {
  const start = getStartOfDay(date);
  const day = start.getDay();
  const diff = start.getDate() - day + (day === 0 ? -6 : 1);
  return new Date(start.setDate(diff));
}
function getStartOfMonth(date: Date): Date {
  const start = new Date(date);
  start.setDate(1);
  start.setHours(0, 0, 0, 0);
  return start;
}

export default function BlogPage() {
  const { user, token } = useAuth(); // Para verificar si es superusuario y para el token
  
  // Estado para Blog Posts tradicionales
  const [blogPostsData, setBlogPostsData] = useState<BlogPost[]>([]);
  const [isLoadingBlogPosts, setIsLoadingBlogPosts] = useState(true);
  const [blogError, setBlogError] = useState<string | null>(null);
  const [showAddBlogPostModal, setShowAddBlogPostModal] = useState(false);
  const [selectedTag, setSelectedTag] = useState<string | null>(null); // Para filtrar por tag

  // Función para cargar Blog Posts desde el backend
  const loadBlogPosts = async () => {
    setIsLoadingBlogPosts(true);
    setBlogError(null);
    try {
      // Asumiendo que el router de blog está en /api/v1/blog/
      const response = await fetch(`${API_V1_URL}/blog/`); 
      if (!response.ok) {
        throw new Error(`API Error ${response.status}: ${await response.text()}`);
      }
      const data: BlogPost[] = await response.json();
      setBlogPostsData(data);
    } catch (err: any) {
      console.error("[BlogPage] Error fetching blog posts:", err);
      setBlogError("No se pudieron cargar las entradas del blog.");
      setBlogPostsData([]);
    } finally {
      setIsLoadingBlogPosts(false);
    }
  };

  useEffect(() => {
    loadBlogPosts(); // Cargar posts al montar
  }, []);

  // Lógica para agrupar BlogPosts (similar a la de noticias o LinkedIn)
  // const groupedBlogPosts = useMemo(() => {
  //   const now = new Date();
  //   const todayStart = getStartOfDay(now);
  //   // ... (lógica de agrupación similar a la de NoticiasPage si se necesita) ...
  //   // Por ahora, devolveremos todos para simplificar
  //   return {
  //     all: blogPostsData.sort((a, b) => new Date(b.published_date).getTime() - new Date(a.published_date).getTime()),
  //   };
  // }, [blogPostsData]);

  // Derivar tags únicos para los filtros
  const uniqueTags = useMemo(() => {
    const allTags = new Set<string>();
    blogPostsData.forEach(post => {
      if (post.tags) {
        post.tags.split(',').forEach(tag => allTags.add(tag.trim()));
      }
    });
    return Array.from(allTags).sort();
  }, [blogPostsData]);

  // Filtrar posts por tag seleccionado
  const filteredBlogPosts = useMemo(() => {
    if (!selectedTag) {
      return blogPostsData.sort((a, b) => new Date(b.published_date).getTime() - new Date(a.published_date).getTime());
    }
    return blogPostsData
      .filter(post => post.tags && post.tags.split(',').map(t => t.trim()).includes(selectedTag))
      .sort((a, b) => new Date(b.published_date).getTime() - new Date(a.published_date).getTime());
  }, [blogPostsData, selectedTag]);

  const handleOpenAddBlogPostModal = () => {
    setShowAddBlogPostModal(true);
  };

  const handleCloseAddBlogPostModal = () => {
    setShowAddBlogPostModal(false);
  };

  const handleConfirmAddBlogPost = async (postData: BlogPostCreate) => {
    if (!token) {
      toast.error("No estás autenticado.");
      return;
    }
    console.log("Datos de la nueva entrada de blog a enviar:", postData);
    try {
      const response = await fetch(`${API_V1_URL}/blog/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(postData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        toast.error(`Error al crear entrada de blog: ${errorData.detail || 'Error desconocido'}`);
        return;
      }
      toast.success("¡Entrada de blog creada con éxito!");
      loadBlogPosts(); // Recargar posts
      handleCloseAddBlogPostModal(); // Cerrar modal
    } catch (err: any) {
      toast.error(`Error al crear entrada de blog: ${err.message || 'Error de red'}`);
    }
  };

  // Renderizado de una tarjeta de Blog Post (ejemplo simple)
  function BlogCard({ post }: { post: BlogPost }) {
    return (
      <div className="bg-card border border-border rounded-lg overflow-hidden shadow-lg flex flex-col h-full">
        {post.image_url && (
          <img 
            src={post.image_url} 
            alt={post.title} 
            className="w-full h-48 object-cover" // Altura fija para la imagen
          />
        )}
        <div className="p-4 flex flex-col flex-grow">
          <h3 className="text-xl font-semibold mb-2">{post.title}</h3>
          <p className="text-xs text-muted-foreground mb-2">
            Publicado: {new Date(post.published_date).toLocaleDateString()}
          </p>
          
          {post.excerpt && <p className="text-sm mb-3 text-muted-foreground flex-grow">{post.excerpt}</p>}
          
          {/* Mostrar contenido completo si no hay extracto, o una parte del contenido */}
          {!post.excerpt && post.content && (
             // Usar dangerouslySetInnerHTML con precaución. Asumir que el contenido es seguro o sanearlo.
             // O usar un renderer de Markdown si el contenido es Markdown.
            <div 
              className="text-sm mb-3 prose dark:prose-invert max-w-none flex-grow" 
              dangerouslySetInnerHTML={{ __html: post.content.length > 200 ? post.content.substring(0, 200) + '...' : post.content }} 
            />
          )}

          {post.linkedin_post_url && (
            <div className="my-3">
              {/* Asumiendo que SocialPostEmbed puede tomar una URL o que linkedin_post_url es un embed code */}
              {/* Si es solo una URL, podríamos necesitar un componente diferente o simplemente un enlace */}
              {post.linkedin_post_url.startsWith('<iframe') || post.linkedin_post_url.startsWith('<script') ? (
                <SocialPostEmbed embedHtml={post.linkedin_post_url} className="w-full" />
              ) : (
                <a href={post.linkedin_post_url} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-500 hover:underline">
                  Ver en LinkedIn
                </a>
              )}
            </div>
          )}
          
          <div className="mt-auto pt-3"> {/* Empujar tags y link al final */}
            {post.tags && (
              <div className="mb-3">
                {post.tags.split(',').map(tag => tag.trim()).filter(tag => tag).map(tag => (
                  <Badge 
                    key={tag} 
                    variant="secondary" 
                    className="mr-1 mb-1 cursor-pointer hover:bg-primary/20"
                    onClick={() => setSelectedTag(tag)}
                  >
                    {tag}
                  </Badge>
                ))}
              </div>
            )}
            <Link href={`/blog/${post.slug}`} className="text-primary hover:underline text-sm font-medium">
              Leer más →
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold text-primary">Blog</h1>
        {user?.is_superuser && (
          <Button onClick={handleOpenAddBlogPostModal} variant="outline">
            <PlusCircle className="mr-2 h-4 w-4" /> Añadir Entrada
          </Button>
        )}
      </div>

      {/* Filtros de Tags */}
      {uniqueTags.length > 0 && (
        <div className="mb-8 flex flex-wrap gap-2 items-center">
          <Button 
            variant={selectedTag === null ? "default" : "outline"}
            onClick={() => setSelectedTag(null)}
            size="sm"
          >
            Todos
          </Button>
          {uniqueTags.map(tag => (
            <Button 
              key={tag} 
              variant={selectedTag === tag ? "default" : "outline"}
              onClick={() => setSelectedTag(tag)}
              size="sm"
            >
              {tag}
            </Button>
          ))}
        </div>
      )}

      {/* Modal para añadir entrada */}
      {user?.is_superuser && (
        <AddBlogPostModal
          isOpen={showAddBlogPostModal}
          onClose={handleCloseAddBlogPostModal}
          onAddPost={handleConfirmAddBlogPost} 
        />
      )}

      {isLoadingBlogPosts && <p className="text-center">Cargando entradas del blog...</p>}
      {blogError && <p className="text-center text-destructive">{blogError}</p>}
      
      {!isLoadingBlogPosts && !blogError && filteredBlogPosts.length === 0 && (
        <p className="text-center text-muted-foreground mt-12">
          {selectedTag ? `No hay entradas de blog para el tag "${selectedTag}".` : "No hay entradas de blog para mostrar."}
        </p>
      )}

      {/* Sección de Blog Posts */}
      {filteredBlogPosts.length > 0 && (
        <section className="mb-16">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 items-start">
            {filteredBlogPosts.map((post) => (
              <BlogCard key={post.id} post={post} />
            ))}
          </div>
        </section>
      )}

      {/* Aquí podrías mantener la sección de posts de LinkedIn si quieres que coexistan */}
      {/* <h2 className="text-3xl font-bold text-center my-12 text-secondary">Actividad Reciente en LinkedIn</h2> */}
      {/* ... (código para mostrar posts de LinkedIn) ... */}
    </div>
  );
} 
