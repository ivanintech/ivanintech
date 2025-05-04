import { Suspense } from 'react'; // Importar Suspense
import Link from 'next/link';
import type { Project } from '@/lib/types';
// import { projectsData } from '@/lib/portfolio-data'; // Ya no se importa
import { ProjectCard } from '@/components/project-card';
import { ProjectCardSkeleton } from '@/components/project-card-skeleton'; // Importar Skeleton
import { API_V1_URL } from '@/lib/api-client'; // Importar URL base

// Función para obtener datos de la API (¡Ahora lanza errores!)
async function getProjects(): Promise<Project[]> {
  let res: Response | undefined;
  try {
    res = await fetch(`${API_V1_URL}/portfolio/projects`, {
      // Opciones de caché de Next.js (ej: revalidar cada hora)
      next: { revalidate: 3600 } 
    });

    if (!res.ok) {
      // Lanzar error específico basado en la respuesta HTTP
      throw new Error(`Error ${res.status}: Fallo al obtener los proyectos (${res.statusText})`);
    }

    // Simular una pequeña demora para ver el skeleton
    // await new Promise(resolve => setTimeout(resolve, 1500));
    return await res.json();

  } catch (error) {
    // Si el error es del fetch mismo (ej. red) o el lanzado arriba, relanzarlo
    console.error("Error detallado en getProjects:", error);
    // Lanzar un error genérico o el error original
    throw new Error('No se pudieron cargar los datos del portfolio.'); 
    // Opcional: podrías intentar relanzar el error original: throw error;
  }
}

// Componente Async que realmente obtiene y muestra los datos
async function PortfolioGrid() {
  // Si getProjects lanza un error, Suspense lo capturará
  // y Next.js buscará el error.tsx más cercano.
  const projectsData = await getProjects();

  // Ya no necesitamos comprobar longitud 0 aquí si lanzamos error
  // if (projectsData.length === 0) { ... }

  // Si llegamos aquí, projectsData tiene datos
  if (projectsData.length === 0) {
     // Esto ahora solo se mostraría si la API devuelve OK pero un array vacío
     return <p className="text-center text-muted-foreground">No hay proyectos disponibles por el momento.</p>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {projectsData.map((project) => (
        <ProjectCard key={project.id} project={project} />
      ))}
    </div>
  );
}

// Componente Fallback para Suspense
function PortfolioSkeletonFallback() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {/* Mostrar varios skeletons */} 
      {[...Array(6)].map((_, index) => (
        <ProjectCardSkeleton key={index} />
      ))}
    </div>
  );
}

// Página principal del Portfolio (ya no es async directa)
export default function PortfolioPage() {
  return (
    <div className="container mx-auto px-4 py-16">
      <h1 className="text-center mb-12">Portfolio de Proyectos</h1>
      <Suspense fallback={<PortfolioSkeletonFallback />}>
        <PortfolioGrid />
      </Suspense>
    </div>
  );
} 