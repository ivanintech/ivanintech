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
  console.log("Usuario en NoticiasPage:", user); // <--- AÑADIR ESTO
  const [allNewsData, setAllNewsData] = useState<NewsItem[]>([]);
  const [topSectors, setTopSectors] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSector, setSelectedSector] = useState<string | null>(null);
  const [showAddNewsModal, setShowAddNewsModal] = useState(false); // <--- Estado para el modal

  const loadNews = async () => {
    setIsLoading(true);
    const url = `${API_V1_URL}/news?limit=100`;
    try {
      const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`API Error ${response.status}`);
        }
        const data: NewsItem[] = await response.json();
        setAllNewsData(data);
        
        // Derive top sectors from the fetched data
        const derivedSectors = getTopSectorsFromNews(data);
        setTopSectors(derivedSectors);

        setError(null);
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
         console.log('Parseando fecha:', item.publishedAt, '->', dateObject.toISOString());
       } catch (e) { 
         console.error('[NoticiasPage] Error convirtiendo fecha:', item.id, e);
       }
       return {
         ...item,
         publishedDateObject: dateObject instanceof Date && !isNaN(dateObject.getTime()) ? dateObject : null,
       };
    })
    // Filtrar items sin fecha válida ANTES de ordenar
    .filter(item => item.publishedDateObject !== null)
    .sort((a, b) => {
      // Ordenar por fecha descendente (más reciente primero)
      return (b.publishedDateObject as Date).getTime() - (a.publishedDateObject as Date).getTime(); 
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
      // Redondear a días completos
      const diffDays = Math.floor((now.getTime() - item.publishedDateObject.getTime()) / MS_PER_DAY);

      if (diffDays <= 2) {
        ultimas.push(item);
      } else if (diffDays <= 6) {
        semana.push(item);
      } else if (diffDays <= 29) {
        mes.push(item);
      }
    });

    // Logging
    console.log(`Agrupación: Últimas: ${ultimas.length}, Semana: ${semana.length}, Mes: ${mes.length}`);

    return {
      ultimasNoticias: ultimas,
      noticiasSemana: semana,
      masNoticias: mes,
    };
  }, [sortedNewsWithDates]);

  // --- Renderizado --- 

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

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold text-primary">Noticias IA & Tech</h1>
        {user?.is_superuser && (
          <Button onClick={handleOpenAddNewsModal} variant="outline">
            <PlusCircle className="mr-2 h-4 w-4" /> Añadir Noticia
          </Button>
        )}
      </div>

      {user?.is_superuser && (
        <AddNewsModal 
          isOpen={showAddNewsModal} 
          onClose={handleCloseAddNewsModal} 
          onAddNews={handleConfirmAddNews} 
          defaultSectors={topSectors}
        />
      )}

      {/* Filtros por Sector */}
      <div className="flex flex-wrap justify-center gap-2 mb-12">
        <Button
          variant={!selectedSector ? "default" : "outline"}
          onClick={() => setSelectedSector(null)}
        >
          Todos
        </Button>
        {topSectors.map((sector) => (
          <Button 
            key={sector}
            variant={selectedSector === sector ? "default" : "outline"}
            onClick={() => setSelectedSector(sector)}
          >
            {sector}
          </Button>
        ))}
      </div>

      {/* Contenido condicional basado en noticias FILTRADAS */}
      {filteredBySectorNews.length === 0 && !isLoading && (
         <p className="text-center text-muted-foreground mt-12">
           No hay noticias disponibles para {selectedSector ? `el sector "${selectedSector}"` : 'mostrar'}.
        </p>
      )}

      {/* Sección Últimas Noticias (Hoy y Ayer) */} 
      {groupedNews.ultimasNoticias.length > 0 && (
        <section className="mb-16">
          <h2 className="text-3xl font-semibold mb-6 text-center md:text-left">Últimas Noticias</h2>
           {/* Podríamos destacar la primera si queremos */}
           {groupedNews.ultimasNoticias.length > 0 && (
             <NewsCard 
               item={groupedNews.ultimasNoticias[0]} 
               isFeatured={true} 
               className="shadow-lg dark:shadow-primary/20 mb-8" // Añadir margen inferior
             />
           )}
          {groupedNews.ultimasNoticias.length > 1 && (
             <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {groupedNews.ultimasNoticias.slice(1).map((item) => (
                  <NewsCard key={item.id} item={item} />
                ))}
              </div>
          )}
        </section>
      )}

      {/* Sección Noticias de la Semana */}
      {groupedNews.noticiasSemana.length > 0 && (
        <section className="mb-16">
          <h2 className="text-3xl font-semibold mb-6 text-center md:text-left">Noticias de esta Semana</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {groupedNews.noticiasSemana.map((item) => (
              <NewsCard 
                key={item.id} 
                item={item} 
                className={item.star_rating && item.star_rating >= 4.6 ? 'lg:col-span-2' : ''}
              />
            ))}
          </div>
        </section>
      )}

      {/* Sección Más Noticias (del mes) */}
      {groupedNews.masNoticias.length > 0 && (
        <section>
          <h2 className="text-3xl font-semibold mb-6 text-center md:text-left">Más Noticias</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {groupedNews.masNoticias.map((item) => (
              <NewsCard 
                key={item.id} 
                item={item} 
                className={item.star_rating && item.star_rating >= 4.6 ? 'lg:col-span-2' : ''}
              />
            ))}
          </div>
        </section>
      )}
      
       {/* Mensaje si hay noticias pero no caen en ninguna categoría (después de filtrar sector) */} 
       {filteredBySectorNews.length > 0 && 
        groupedNews.ultimasNoticias.length === 0 && 
        groupedNews.noticiasSemana.length === 0 && 
        groupedNews.masNoticias.length === 0 && 
        (
         <p className="text-center text-muted-foreground mt-12">
           No hay noticias recientes (último mes) para {selectedSector ? `el sector "${selectedSector}"` : 'mostrar'}.
        </p>
      )}

    </div>
  );
}

// Componente NewsCard Mejorado
// function NewsCard({ item }: { item: NewsItem }) {
//   // ... (código del componente eliminado)
// } 