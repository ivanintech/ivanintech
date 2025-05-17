'use client'; // Necesario para useState y onClick

import Link from 'next/link';
import { useState, useMemo, useEffect } from 'react'; // Importar useState, useMemo y useEffect
// import Image from 'next/image'; // Ya no se usa aquí
// import type { NewsItem } from '@/lib/types'; // Cambiar a NewsItemRead
import type { NewsItem } from '@/lib/types'; // Corregir a NewsItem
import { API_V1_URL } from '@/lib/api-client'; // Importar URL base
import { NewsCard } from '@/components/content/NewsCard'; // Importar el componente externo
import { Button } from "@/components/ui/button"; // Importar Button de shadcn

// --- Funciones Helper para Fechas ---
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

// Lista predefinida de sectores
const SECTORES_COMUNES = [
  'Software', 'Hardware', 'Cloud Computing', 'Robótica',
  'Finanzas', 'Salud', 'Gaming', 'Ciberseguridad', 'Automoción'
];

// Página de Noticias (¡Convertida a Client Component!)
export default function NoticiasPage() {
  const [allNewsData, setAllNewsData] = useState<NewsItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSector, setSelectedSector] = useState<string | null>(null);

  // Fetch de datos usando useEffect
  useEffect(() => {
    async function loadNews() {
      const url = `${API_V1_URL}/news?limit=100`;
      console.log('[NoticiasPage] Intentando fetch:', url);
      try {
        const news = await fetch(url);
        console.log('[NoticiasPage] Respuesta fetch:', news);
        if (!news.ok) {
          throw new Error(`API Error ${news.status}`);
        }
        const data = await news.json();
        console.log('[NoticiasPage] Datos recibidos:', data);
        setAllNewsData(data);
        setError(null);
      } catch (err: any) {
        console.error("[NoticiasPage] Error fetching news:", err, 'URL:', url);
        setError("No se pudieron cargar las noticias.");
        setAllNewsData([]);
      } finally {
        setIsLoading(false);
      }
    }
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
         // Guardamos el objeto Date para ordenar y filtrar fácil
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

  // 3. Agrupar por los nuevos periodos de tiempo
  const groupedNews = useMemo(() => {
    const now = new Date();
    const todayStart = getStartOfDay(now);
    const yesterdayStart = getStartOfDay(new Date(now.getTime() - 24 * 60 * 60 * 1000));
    const weekStart = getStartOfWeek(now);
    const monthStart = getStartOfMonth(now);

    // --- LOGGING --- 
    console.log('[NoticiasPage: Agrupación]');
    console.log(` - Referencia AHORA: ${now.toISOString()}`);
    console.log(` - Inicio AYER:       ${yesterdayStart.toISOString()}`);
    console.log(` - Inicio SEMANA:    ${weekStart.toISOString()}`);
    console.log(` - Inicio MES:       ${monthStart.toISOString()}`);
    if (sortedNewsWithDates.length > 0) {
      console.log(' - Primera noticia (ordenada): ', {
        id: sortedNewsWithDates[0].id,
        published_date_str: sortedNewsWithDates[0].publishedAt,
        publishedDateObject: sortedNewsWithDates[0].publishedDateObject?.toISOString(),
        title: sortedNewsWithDates[0].title
      });
    }
    // --- FIN LOGGING ---

    const ultimas = sortedNewsWithDates.filter(item => 
      item.publishedDateObject && item.publishedDateObject >= yesterdayStart
    );
    const semana = sortedNewsWithDates.filter(item => 
      item.publishedDateObject && item.publishedDateObject >= weekStart && item.publishedDateObject < yesterdayStart
    );
    const anteriores = sortedNewsWithDates.filter(item => 
      item.publishedDateObject && item.publishedDateObject >= monthStart && item.publishedDateObject < weekStart
    );
    
    // --- LOGGING RESULTADOS ---
    console.log(` - RESULTADO Agrupación - Últimas: ${ultimas.length}, Semana: ${semana.length}, Anteriores: ${anteriores.length}`);
    // --- FIN LOGGING RESULTADOS ---

    return {
      ultimasNoticias: ultimas,
      noticiasSemana: semana,
      noticiasAnteriores: anteriores,
    };

  }, [sortedNewsWithDates]);

  // --- Renderizado --- 

  if (isLoading) {
    return <div className="container mx-auto px-4 py-16 text-center">Cargando noticias...</div>;
  }

  if (error) {
    return <div className="container mx-auto px-4 py-16 text-center text-destructive">{error}</div>;
  }

  return (
    <div className="container mx-auto px-4 py-16">
      <h1 className="text-4xl font-bold text-center mb-8 text-primary">Noticias IA & Tech</h1>

      {/* Filtros por Sector */}
      <div className="flex flex-wrap justify-center gap-2 mb-12">
        <Button
          variant={!selectedSector ? "default" : "outline"}
          onClick={() => setSelectedSector(null)}
        >
          Todos
        </Button>
        {SECTORES_COMUNES.map((sector) => (
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

      {/* Sección Noticias de esta Semana */} 
      {groupedNews.noticiasSemana.length > 0 && (
        <section className="mb-16">
          <h2 className="text-2xl font-semibold mb-6">Noticias de esta Semana</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {groupedNews.noticiasSemana.map((item) => (
              <NewsCard key={item.id} item={item} />
            ))}
          </div>
        </section>
      )}

      {/* Sección Noticias Anteriores (Resto del mes) */} 
      {groupedNews.noticiasAnteriores.length > 0 && (
        <section className="mb-16">
          <h2 className="text-2xl font-semibold mb-6">Noticias Anteriores (este mes)</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {groupedNews.noticiasAnteriores.map((item) => (
              <NewsCard key={item.id} item={item} />
            ))}
          </div>
        </section>
      )}
      
       {/* Mensaje si hay noticias pero no caen en ninguna categoría (después de filtrar sector) */} 
       {filteredBySectorNews.length > 0 && 
        groupedNews.ultimasNoticias.length === 0 && 
        groupedNews.noticiasSemana.length === 0 && 
        groupedNews.noticiasAnteriores.length === 0 && 
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