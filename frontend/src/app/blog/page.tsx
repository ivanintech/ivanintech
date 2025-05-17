// ivanintech/frontend/src/app/blog/page.tsx
// --- COMPONENTE BlogPage ---
'use client';

import { SocialPostEmbed } from '@/components/content/SocialPostEmbed';
import { useState, useMemo } from 'react';
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
// Importar los datos y funciones del nuevo archivo
import { 
  getProcessedLinkedInPosts, 
  type ProcessedLinkedInPost, 
  // rawLinkedInPosts // Ya no necesitamos rawLinkedInPosts directamente aquí
} from '@/lib/linkedin-posts-data';

// --- LISTA DE POSTS A INCRUSTAR --- (ELIMINADO, AHORA EN linkedin-posts-data.ts)
// const postsToEmbed = [ ... ];

// --- FUNCIONES HELPER FECHAS --- (Mantenidas si se usan localmente, o mover si son más genéricas)
function getStartOfDay(date: Date): Date {
  const start = new Date(date);
  start.setHours(0, 0, 0, 0);
  return start;
}
function getStartOfWeek(date: Date): Date { // Lunes como inicio de semana
  const start = getStartOfDay(date);
  const day = start.getDay(); // Domingo = 0, Lunes = 1, ...
  const diff = start.getDate() - day + (day === 0 ? -6 : 1); // Ajustar para Lunes
  return new Date(start.setDate(diff));
}
function getStartOfMonth(date: Date): Date {
  const start = new Date(date);
  start.setDate(1);
  start.setHours(0, 0, 0, 0);
  return start;
}

// Corrección: Type Alias ProcessedPost ya no se necesita aquí si usamos ProcessedLinkedInPost directamente
// type ProcessedPost = (typeof postsToEmbed)[number] & {
//   publishedDateObject: Date | null;
// };

export default function BlogPage() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  // Usar la función importada para obtener y procesar los posts
  const allProcessedPosts = useMemo(() => getProcessedLinkedInPosts(), []);

  const parsedAndFilteredPosts: ProcessedLinkedInPost[] = useMemo(() => {
    let filtered = allProcessedPosts; // Empezar con todos los posts ya procesados

        if (selectedCategory) {
            filtered = filtered.filter(post => post.category === selectedCategory);
        }
    // La ordenación ya se hace en getProcessedLinkedInPosts, así que no es necesaria aquí
    // return filtered.sort((a, b) => (b.publishedDateObject as Date).getTime() - (a.publishedDateObject as Date).getTime());
    return filtered;
  }, [selectedCategory, allProcessedPosts]);

  const groupedPosts = useMemo(() => {
     const now = new Date();
     const yesterdayStart = getStartOfDay(new Date(now.getTime() - 24 * 60 * 60 * 1000));
     const weekStart = getStartOfWeek(now);

     // Asegurarse de que publishedDateObject no sea null antes de comparar
     const ultimos = parsedAndFilteredPosts.filter(p => p.publishedDateObject && p.publishedDateObject >= yesterdayStart);
     const semana = parsedAndFilteredPosts.filter(p => p.publishedDateObject && p.publishedDateObject >= weekStart && p.publishedDateObject < yesterdayStart);
     const anteriores = parsedAndFilteredPosts.filter(p => p.publishedDateObject && p.publishedDateObject < weekStart);

     return { ultimos, semana, anteriores };
  }, [parsedAndFilteredPosts]);

  const availableCategories = useMemo(() => {
    // Obtener categorías de los posts procesados (que ya excluyen los que no tienen embed)
    const categories = new Set(allProcessedPosts.map(p => p.category).filter(Boolean) as string[]); 
    return Array.from(categories).sort();
  }, [allProcessedPosts]);

  // Helper para renderizar una sección de posts
  function renderPostSection(title: string, posts: ProcessedLinkedInPost[], isLatestSection: boolean = false) {
    if (posts.length === 0) return null;

    return (
      <section className="mb-16">
        <h2 className={`text-3xl font-semibold mb-6 ${isLatestSection ? 'text-center md:text-left' : ''}`}>
          {title}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 items-start">
          {posts.map((post, index) => {
            const shouldSpan = (isLatestSection && index === 0 && posts.length > 1) || post.author === 'me';
            const columnSpanClass = shouldSpan ? 'md:col-span-2 lg:col-span-2' : '';

            return (
              <div
                key={post.id}
                className={`bg-card border border-border rounded-lg overflow-hidden shadow-sm flex flex-col ${columnSpanClass}`}
              >
                <div className="p-1 flex-grow">
                  <SocialPostEmbed embedHtml={post.embedCode} />
                </div>
                <div className="p-2 text-right border-t border-border space-x-2">
                   {post.author === 'me' && (
                     <Badge variant="default">Mi Post</Badge>
                   )}
                   {post.author === 'recommended' && (
                      <Badge variant="secondary">Recomendado</Badge>
                   )}
                  <Badge variant="outline">{post.category}</Badge>
                </div>
              </div> 
            );
          })}
        </div> 
      </section> 
    );
  } 


  return (
    <div className="container mx-auto px-4 py-16">
      <h1 className="text-4xl font-bold text-center mb-8 text-primary">
        Actividad Reciente en LinkedIn
      </h1>

      {/* Filtros por Categoría */}
      <div className="flex flex-wrap justify-center gap-2 mb-12">
         <Button
            variant={!selectedCategory ? "default" : "outline"}
            onClick={() => setSelectedCategory(null)}
            size="sm"
            >
            Todos
            </Button>
            {availableCategories.map((category: string) => (
            <Button
                key={category}
                variant={selectedCategory === category ? "default" : "outline"}
                onClick={() => setSelectedCategory(category)}
                size="sm"
            >
                {category}
            </Button>
            ))}
      </div>

      {parsedAndFilteredPosts.length === 0 ? (
         <p className="text-center text-muted-foreground mt-12">
           No hay actividad para mostrar {selectedCategory ? `en la categoría "${selectedCategory}"` : ''}.
        </p>
      ) : (
        <>
          {renderPostSection("Últimos Posts", groupedPosts.ultimos, true)}
          {renderPostSection("Esta Semana", groupedPosts.semana)}
          {renderPostSection("Anteriores", groupedPosts.anteriores)}
        </>
      )}
    </div>
  );
} 
