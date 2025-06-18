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
// import { es } from 'date-fns/locale'; // ELIMINADO

// CLIENT TYPES (Importar desde la nueva ubicación centralizada)
import type { BlogPost, BlogPostCreate } from '@/types'; // ELIMINADO NewsItem
import { AddBlogPostModal } from '@/components/admin/AddBlogPostModal'; // <--- IMPORTAR EL MODAL
import { toast } from 'sonner'; // Para notificaciones

// Definir el tipo para la respuesta de la API
interface BlogPostsApiResponse {
  items: BlogPost[];
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
      const response = await fetch(`${API_V1_URL}/blog/?limit=100&status=published`); 
      if (!response.ok) {
        throw new Error(`API Error ${response.status}: ${await response.text()}`);
      }
      const data: BlogPostsApiResponse = await response.json();
      setBlogPostsData(data.items);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      console.error("[BlogPage] Error fetching blog posts:", errorMessage);
      setBlogError("Could not load blog posts.");
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
      toast.error("You are not authenticated.");
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
        toast.error(`Error creating blog post: ${errorData.detail || 'Unknown error'}`);
        return;
      }
      toast.success("Blog post created successfully!");
      loadBlogPosts();
      handleCloseAddBlogPostModal();
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      toast.error(`Error creating blog post: ${errorMessage}`);
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
            Published: {new Date(post.published_date).toLocaleDateString()}
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
              {(() => {
                const url = post.linkedin_post_url;
                if (url.includes('<iframe')) {
                  // Si ya es un iframe completo, lo renderiza directamente.
                  return <SocialPostEmbed embedHtml={url} className="w-full" />;
                } else if (url.startsWith('https://www.linkedin.com/embed')) {
                  // Si es una URL de embed, construye el iframe.
                  const iframeHtml = `<iframe src="${url}" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>`;
                  return <SocialPostEmbed embedHtml={iframeHtml} className="w-full" />;
                } else {
                  // Si es cualquier otra URL, muestra un enlace.
                  return (
                    <a href={url} target="_blank" rel="noopener noreferrer" className="text-sm text-blue-500 hover:underline">
                      View on LinkedIn
                    </a>
                  );
                }
              })()}
            </div>
          )}
          
          <div className="mt-auto pt-3"> {/* Empujar tags y link al final */}
            {post.tags && (
              <div className="mb-3">
                {post.tags.split(',').map((tag: string) => tag.trim()).filter((tag: string) => tag).map((tag: string) => (
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
              Read more →
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
            <PlusCircle className="mr-2 h-4 w-4" /> Add Post
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
            All
            </Button>
          {uniqueTags.map((tag: string) => (
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

      {/* Sección de Blog Posts */}
      {isLoadingBlogPosts && <p className="text-center py-10">Loading posts...</p>}
      {!isLoadingBlogPosts && blogError && <p className="text-destructive text-center">{blogError}</p>}
      {!isLoadingBlogPosts && !blogError && filteredBlogPosts.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 items-start">
          {(() => {
              let linkedInPostOrder = 0; // Contador para el orden de los posts de LinkedIn
              return filteredBlogPosts.map((post) => {
                let cardSpanClass = "lg:col-span-1"; // Por defecto es 1
                if (post.linkedin_post_url) {
                  const orderInCycle = linkedInPostOrder % 5; // Ciclo de 5: 3, 2, 1, 2, 1
                  if (orderInCycle === 0) cardSpanClass = "lg:col-span-3"; // El primero de cada 5 ocupa 3
                  else if (orderInCycle === 1 || orderInCycle === 3) cardSpanClass = "lg:col-span-2"; // El segundo y cuarto ocupan 2
                  // else cardSpanClass queda como lg:col-span-1 (el tercero y quinto)
                  linkedInPostOrder++;
                } else {
                  // Los posts manuales (sin LinkedIn) siempre ocupan 1 columna
                  cardSpanClass = "lg:col-span-1";
                }
                return (
                  <div key={post.id} className={`w-full ${cardSpanClass}`}>
                    <BlogCard post={post} />
                  </div>
                );
              });
            })()}
        </div>
      )}
      {!isLoadingBlogPosts && !blogError && filteredBlogPosts.length === 0 && (
        <p className="text-center text-muted-foreground">No blog posts found matching your criteria.</p>
      )}

      {/* Separador opcional */}
      {/* <hr className="my-16 border-gray-200 dark:border-gray-700" /> */}

    </div>
  );
} 
