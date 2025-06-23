// ivanintech/frontend/src/app/blog/page.tsx
// --- COMPONENTE BlogPage ---
'use client';

import { useState, useMemo, useEffect } from 'react';
import { Button } from "@/components/ui/button";
// Quitar datos de LinkedIn si vamos a reemplazarlos o complementarlos
// import { getProcessedLinkedInPosts, type ProcessedLinkedInPost } from '@/lib/linkedin-posts-data';
// import { SocialPostEmbed } from '@/components/content/SocialPostEmbed';
// Nuevas importaciones para Blog tradicional
import { useAuth } from '@/context/AuthContext';
import { PlusCircle } from 'lucide-react';
import apiClient from '@/lib/api-client'; // Cambiado
// import { es } from 'date-fns/locale'; // ELIMINADO

// CLIENT TYPES (Importar desde la nueva ubicación centralizada)
import type { BlogPost, BlogPostCreate, BlogPostUpdate } from '@/types'; // ELIMINADO NewsItem
import { AddBlogPostModal } from '@/components/admin/AddBlogPostModal'; // <--- IMPORTAR EL MODAL
import { toast } from 'sonner'; // Para notificaciones
import { ArticleCard } from '@/components/blog/ArticleCard'; // Importar el componente refactorizado
import { Switch } from "@/components/ui/switch"; // Importar Switch
import { Label } from "@/components/ui/label"; // Importar Label

// Importar componentes de diálogo para editar y borrar
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";

export default function BlogPage() {
  const { user, token } = useAuth(); // Para verificar si es superusuario y para el token
  
  // Estado para Blog Posts tradicionales
  const [blogPostsData, setBlogPostsData] = useState<BlogPost[]>([]);
  const [isLoadingBlogPosts, setIsLoadingBlogPosts] = useState(true);
  const [blogError, setBlogError] = useState<string | null>(null);
  const [selectedTag, setSelectedTag] = useState<string | null>(null); // Para filtrar por tag

  // Estado para el toggle de posts no publicados (solo para superuser)
  const [showNonPublished, setShowNonPublished] = useState(false);

  // Estado para los modales
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingPost, setEditingPost] = useState<BlogPost | null>(null);
  const [deletingPost, setDeletingPost] = useState<BlogPost | null>(null);

  // Función para cargar Blog Posts desde el backend
  const loadBlogPosts = async () => {
    setIsLoadingBlogPosts(true);
    setBlogError(null);
    try {
      const data = await apiClient<{ items: BlogPost[] }>('/blog/?limit=100&status=all'); // Cargar todos para el admin
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
    let posts = blogPostsData;

    // 1. Filtrar por estado de publicación
    // Si no es superusuario o si es superusuario pero no quiere ver los no publicados
    if (!user?.is_superuser || (user?.is_superuser && !showNonPublished)) {
      posts = posts.filter(post => post.status === 'published');
    }
    // Si es superusuario y showNonPublished es true, se muestran todos, así que no se aplica filtro de estado.

    // 2. Filtrar por tag seleccionado
    if (selectedTag) {
      posts = posts.filter(post => post.tags && post.tags.split(',').map(t => t.trim()).includes(selectedTag));
    }
    
    // 3. Ordenar por fecha
    return posts.sort((a, b) => new Date(b.published_date).getTime() - new Date(a.published_date).getTime());
  }, [blogPostsData, selectedTag, user, showNonPublished]);

  const handleConfirmModal = async (postData: BlogPostCreate | BlogPostUpdate) => {
    if (!token) {
      toast.error("You are not authenticated.");
      return;
    }

    const isEditing = !!editingPost;
    const endpoint = isEditing ? `/blog/${editingPost.id}` : '/blog/';
    const method = isEditing ? 'PUT' : 'POST';
    const successMessage = isEditing ? "Blog post updated successfully!" : "Blog post created successfully!";

    try {
      await apiClient<BlogPost>(endpoint, { method, token, body: postData });
      toast.success(successMessage);
      loadBlogPosts();
      setShowAddModal(false);
      setEditingPost(null);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      toast.error(`Error: ${errorMessage}`);
    }
  };

  const handleDeletePost = async () => {
    if (!deletingPost || !token) {
      toast.error("No post selected for deletion or you are not authenticated.");
      return;
    }
    try {
      await apiClient<BlogPost>(`/blog/${deletingPost.id}`, { method: 'DELETE', token });
      toast.success("Blog post deleted successfully!");
      setDeletingPost(null);
      loadBlogPosts();
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      toast.error(`Error deleting blog post: ${errorMessage}`);
    }
  };

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold text-primary">Blog</h1>
        {user?.is_superuser && (
          <Button onClick={() => setShowAddModal(true)} variant="outline">
            <PlusCircle className="mr-2 h-4 w-4" /> Add Post
          </Button>
        )}
      </div>

      {/* Controles para Superuser */}
      {user?.is_superuser && (
        <div className="flex items-center space-x-2 mb-4 p-4 bg-secondary rounded-lg">
          <Switch
            id="show-non-published"
            checked={showNonPublished}
            onCheckedChange={setShowNonPublished}
          />
          <Label htmlFor="show-non-published">Mostrar posts no publicados</Label>
        </div>
      )}

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

      {/* --- MODALES --- */}
      {user?.is_superuser && (
        <>
          <AddBlogPostModal
            isOpen={showAddModal || !!editingPost}
            onClose={() => { setShowAddModal(false); setEditingPost(null); }}
            onConfirm={handleConfirmModal}
            postToEdit={editingPost}
            isEditing={!!editingPost}
          />

          {/* Modal de Confirmación de Borrado */}
          <Dialog open={!!deletingPost} onOpenChange={() => setDeletingPost(null)}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Are you sure you want to delete this post?</DialogTitle>
                <DialogDescription>
                  This action cannot be undone. This will permanently delete the blog post titled: <strong>{deletingPost?.title}</strong>.
                </DialogDescription>
              </DialogHeader>
              <DialogFooter>
                <Button variant="outline" onClick={() => setDeletingPost(null)}>Cancel</Button>
                <Button variant="destructive" onClick={handleDeletePost}>Delete</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </>
      )}

      {/* Sección de Blog Posts */}
      {isLoadingBlogPosts && <p className="text-center py-10">Loading posts...</p>}
      {!isLoadingBlogPosts && blogError && <p className="text-destructive text-center">{blogError}</p>}
      {!isLoadingBlogPosts && !blogError && filteredBlogPosts.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 items-start">
          {(() => {
              let linkedInPostOrder = 0; // Contador para el ciclo de los posts de LinkedIn
              return filteredBlogPosts.map((post) => {
                let cardSpanClass = "md:col-span-1 lg:col-span-1"; // Tamaño por defecto para posts manuales

                if (post.linkedin_post_url) {
                  const orderInCycle = linkedInPostOrder % 5; // Ciclo de 5: 3, 2, 1, 2, 1
                  if (orderInCycle === 0) {
                      cardSpanClass = "md:col-span-2 lg:col-span-3"; // El primero ocupa el ancho completo
                  } else if (orderInCycle === 1 || orderInCycle === 3) {
                      cardSpanClass = "md:col-span-1 lg:col-span-2"; // El 2º y 4º ocupan 2/3
                  }
                  // El 3º y 5º se quedan con el tamaño por defecto (1/3)
                  linkedInPostOrder++;
                }

                return (
                  <ArticleCard 
                    key={post.id}
                    post={post}
                    onEdit={setEditingPost}
                    onDelete={setDeletingPost}
                    className={cardSpanClass}
                  />
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
