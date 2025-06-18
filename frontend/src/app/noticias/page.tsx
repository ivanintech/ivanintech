'use client'; // Necesario para useState y onClick

// import Link from 'next/link'; // Removed unused import
import { useState, useMemo, useEffect } from 'react'; // Importar useState, useMemo y useEffect
// import Image from 'next/image'; // Ya no se usa aquí
// import type { NewsItem } from '@/lib/types'; // Cambiar a NewsItemRead
import type { NewsItem, NewsItemCreate } from '@/types'; // Corrected import path
import { API_V1_URL } from '@/lib/api-client'; // Importar URL base
import { NewsCard } from '@/components/content/NewsCard'; // Importar el componente externo
import { Button } from "@/components/ui/button"; // Importar Button de shadcn
import { useAuth } from '@/context/AuthContext'; // <--- Importar useAuth
import { PlusCircle } from 'lucide-react'; // <--- Icono para el botón
import { AddNewsModal } from '@/components/admin/AddNewsModal'; // <--- Importar el modal
import { toast } from 'sonner'; // Para notificaciones

// Derives top sectors from the full list of news on the client-side.
const getTopSectorsFromNews = (news: NewsItem[], limit: number = 10): string[] => {
  if (!news || news.length === 0) {
    return [];
  }

  const sectorCounts = new Map<string, number>();

  news.forEach(item => {
    if (item.sectors && Array.isArray(item.sectors)) {
      item.sectors.forEach(sector => {
        sectorCounts.set(sector, (sectorCounts.get(sector) || 0) + 1);
      });
    }
  });

  // Sort sectors by frequency and return the top 'limit'
  return Array.from(sectorCounts.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(entry => entry[0]);
};

// Página de Noticias (¡Convertida a Client Component!)
export default function NoticiasPage() {
  const { user, token } = useAuth(); // <--- Obtener token también
  const [allNewsData, setAllNewsData] = useState<NewsItem[]>([]);
  const [topSectors, setTopSectors] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSector, setSelectedSector] = useState<string | null>(null);
  const [showAddNewsModal, setShowAddNewsModal] = useState(false); // <--- Estado para el modal

  const loadNews = async () => {
    setIsLoading(true);
    setError(null);
    const url = `${API_V1_URL}/news?limit=100`;
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`API Error ${response.status}`);
      }
      const data: NewsItem[] = await response.json();
      setAllNewsData(data);
      const derivedSectors = getTopSectorsFromNews(data);
      setTopSectors(derivedSectors);
    } catch (err) {
      console.error("[NoticiasPage] Error fetching news:", err);
      setError("No se pudieron cargar las noticias.");
      setAllNewsData([]);
      setTopSectors([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadNews();
  }, []);

  // 1. Filtrar por sector seleccionado (usando useMemo para optimizar)
  const filteredBySectorNews = useMemo(() => {
    if (!selectedSector) {
      return allNewsData; // Devolver todo si no hay sector seleccionado
    }
    return allNewsData.filter(item => 
      item.sectors && Array.isArray(item.sectors) && item.sectors.includes(selectedSector)
    );
  }, [allNewsData, selectedSector]);

  // 2. Convertir fechas y ordenar (sobre datos filtrados por sector)
  const sortedNewsWithDates = useMemo(() => {
     return filteredBySectorNews.map(item => {
       let dateObject: Date | null = null;
       try {
         dateObject = new Date(item.publishedAt);
       } catch (e) { 
         console.error('[NoticiasPage] Error convirtiendo fecha:', item.id, e);
       }
       return {
         ...item,
         publishedDateObject: dateObject instanceof Date && !isNaN(dateObject.getTime()) ? dateObject : null,
       };
    })
    .filter(item => item.publishedDateObject !== null)
    .sort((a, b) => {
      const dateDiff = (b.publishedDateObject as Date).getTime() - (a.publishedDateObject as Date).getTime();
      if (dateDiff !== 0) return dateDiff;
      return (b.relevance_rating ?? 0) - (a.relevance_rating ?? 0);
    });
  }, [filteredBySectorNews]);

  // 3. Agrupar por los nuevos periodos de tiempo (usando diferencia real de días)
  const groupedNews = useMemo(() => {
    const now = new Date();
    const MS_PER_DAY = 24 * 60 * 60 * 1000;

    const ultimas: typeof sortedNewsWithDates = [];
    const semana: typeof sortedNewsWithDates = [];
    const mes: typeof sortedNewsWithDates = [];

    sortedNewsWithDates.forEach(item => {
      if (!item.publishedDateObject) return;
      const diffDays = Math.floor((now.getTime() - item.publishedDateObject.getTime()) / MS_PER_DAY);

      if (diffDays <= 2) {
        ultimas.push(item);
      } else if (diffDays <= 6) {
        semana.push(item);
      } else if (diffDays <= 29) {
        mes.push(item);
      }
    });

    return {
      ultimasNoticias: ultimas,
      noticiasSemana: semana,
      masNoticias: mes,
    };
  }, [sortedNewsWithDates]);

  // --- Renderizado ---

  const renderNewsSection = (title: string, news: (NewsItem & { publishedDateObject: Date | null })[]) => {
    if (news.length === 0) return null;
    return (
      <section key={title} className="mb-12">
        <h2 className="text-3xl font-bold mb-6 text-foreground">{title}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 auto-rows-fr gap-6">
          {news.map((item) => {
            const isFeatured = item.relevance_rating === 5;
            const cardClassName = isFeatured
              ? 'md:col-span-2 lg:col-span-2 xl:col-span-2 md:row-span-2'
              : 'row-span-1';
            return (
              <div key={item.id} className={cardClassName}>
                <NewsCard item={item} isFeatured={isFeatured} className="h-full" />
              </div>
            );
          })}
        </div>
      </section>
    );
  };

  if (isLoading && allNewsData.length === 0) {
    // Modificamos el mensaje de carga para tener en cuenta el chequeo de Auth
    return <div className="container mx-auto px-4 py-16 text-center">Cargando...</div>;
  }

  if (error && allNewsData.length === 0) {
    return <div className="container mx-auto px-4 py-16 text-center text-destructive">{error}</div>;
  }

  const handleOpenAddNewsModal = () => {
    setShowAddNewsModal(true);
  };

  const handleCloseAddNewsModal = () => {
    setShowAddNewsModal(false);
  };

  // Función que se pasará al modal para añadir la noticia
  const handleConfirmAddNews = async (newsData: NewsItemCreate) => {
    if (!token) {
      toast.error("No estás autenticado.");
      return;
    }
    console.log("Datos de la nueva noticia a enviar:", newsData);
    
    try {
      const response = await fetch(`${API_V1_URL}/news/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(newsData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Error al crear la noticia (respuesta no ok):", errorData);
        toast.error(`Error al crear noticia: ${errorData.detail || 'Error desconocido'}`);
        return;
      }

      toast.success("¡Noticia creada con éxito!");
      
      loadNews(); // Recargar las noticias para mostrar la nueva
      handleCloseAddNewsModal(); // Cerrar el modal

    } catch (err) {
      console.error("Error al crear la noticia (catch):", err);
      toast.error(`Error al crear noticia: ${err instanceof Error ? err.message : 'Error de red o desconocido'}`);
    }
  };

  const hasNewsToDisplay = groupedNews.ultimasNoticias.length > 0 || groupedNews.noticiasSemana.length > 0 || groupedNews.masNoticias.length > 0;

  return (
    <>
      <section className="bg-muted dark:bg-card border-b border-border py-20 md:py-28">
        <div className="container mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight text-primary mb-4">
            Actualidad en IA & Tech
          </h1>
          <p className="text-lg md:text-xl mt-4 mb-8 text-muted-foreground max-w-3xl mx-auto">
            Un feed de noticias seleccionadas y analizadas con IA para mantenerte al día con los avances más importantes del sector.
          </p>
          {user?.is_superuser && (
            <Button onClick={handleOpenAddNewsModal} size="lg">
              <PlusCircle className="mr-2 h-5 w-5" />
              Añadir Noticia
            </Button>
          )}
        </div>
      </section>

      <div className="container mx-auto px-4 py-12">
        {user?.is_superuser && (
          <AddNewsModal 
            isOpen={showAddNewsModal} 
            onClose={handleCloseAddNewsModal} 
            onAddNews={handleConfirmAddNews} 
            defaultSectors={topSectors}
          />
        )}

        <div className="mb-12 flex flex-wrap items-center justify-center gap-2">
          <Button
            variant={selectedSector === null ? "default" : "outline"}
            onClick={() => setSelectedSector(null)}
            className="rounded-full"
          >
            Todas
          </Button>
          {topSectors.map((sector) => (
            <Button 
              key={sector}
              variant={selectedSector === sector ? "default" : "outline"}
              onClick={() => setSelectedSector(sector)}
              className="rounded-full"
            >
              {sector}
            </Button>
          ))}
        </div>

        {isLoading && <div className="text-center py-16">Cargando noticias...</div>}
        
        {error && <div className="text-center py-16 text-destructive">{error}</div>}

        {!isLoading && !error && (
          <>
            {renderNewsSection("Últimas Noticias", groupedNews.ultimasNoticias)}
            {renderNewsSection("Esta Semana", groupedNews.noticiasSemana)}
            {renderNewsSection("Este Mes", groupedNews.masNoticias)}

            {!hasNewsToDisplay && (
              <p className="text-center text-muted-foreground mt-12 text-lg">
                No hay noticias disponibles para {selectedSector ? `el sector "${selectedSector}"` : 'mostrar'}.
              </p>
            )}
          </>
        )}
      </div>
    </>
  );
}

// Componente NewsCard Mejorado
// function NewsCard({ item }: { item: NewsItem }) {
//   // ... (código del componente eliminado)
// } 