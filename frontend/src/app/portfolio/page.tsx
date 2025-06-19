'use client';

import { useState, useEffect, useCallback } from 'react';
import type { Project } from '@/types';
import { ProjectCard } from '@/components/project-card';
import { ProjectCardSkeleton } from '@/components/project-card-skeleton';
import apiClient from '@/lib/api-client'; // Cambiado
import { useAuth } from '@/context/AuthContext';

// --- Funciones de API refactorizadas ---

async function getProjectsApi(): Promise<Project[]> {
  // Ahora usamos el cliente centralizado. El manejo de errores ya está incluido.
  return apiClient<Project[]>('/projects/');
}

async function toggleFeaturedApi(projectId: string, token: string): Promise<void> {
  // Usamos el cliente para la llamada PUT y pasamos el token
  await apiClient<void>(`/projects/${projectId}/toggle-featured/`, {
    method: 'PUT',
    token: token,
  });
}

// --- Componente principal de la cuadrícula ---

function PortfolioGrid({ isSuperuser }: { isSuperuser: boolean }) {
  const [allProjects, setAllProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuth();

  const fetchProjects = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getProjectsApi();
      setAllProjects(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unknown error loading projects.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const handleToggleFeatured = async (projectId: string) => {
    if (!token) {
      setError("Action not allowed. You must be logged in.");
      return;
    }
    try {
      await toggleFeaturedApi(projectId, token);
      await fetchProjects(); // Recargar proyectos para ver el cambio
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error changing featured status.';
      console.error("Error toggling featured status:", errorMessage);
      alert(`Error changing status: ${errorMessage}`);
    }
  };

  if (isLoading) {
    return <PortfolioSkeletonFallback />;
  }

  if (error) {
    return <p className="text-center text-red-500">Error: {error}</p>;
  }

  const featuredProjects = allProjects.filter(p => p.videoUrl || p.is_featured);
  const moreProjects = allProjects.filter(p => !p.videoUrl && !p.is_featured);

  if (allProjects.length === 0) {
     return <p className="text-center text-muted-foreground">No projects available at the moment.</p>;
  }

  return (
    <div className="space-y-12">
      {featuredProjects.length > 0 && (
        <section>
          <h2 className="text-2xl font-semibold mb-6">Featured Projects</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {featuredProjects.map((project) => (
              <ProjectCard key={project.id} project={project} onToggleFeatured={handleToggleFeatured} isSuperuser={isSuperuser} />
            ))}
          </div>
        </section>
      )}

      {moreProjects.length > 0 && (
        <section>
          <h2 className="text-2xl font-semibold mb-6">More Projects</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {moreProjects.map((project) => (
              <ProjectCard key={project.id} project={project} onToggleFeatured={handleToggleFeatured} isSuperuser={isSuperuser} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function PortfolioSkeletonFallback() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {[...Array(6)].map((_, index) => (
        <ProjectCardSkeleton key={index} />
      ))}
    </div>
  );
}

export default function PortfolioPage() {
  const { user, isLoading: authLoading } = useAuth(); // Get user and auth loading state

  if (authLoading) {
    // Optional: show a loader while auth state is being determined
    return <div className="container mx-auto px-4 py-16 text-center">Verifying session...</div>;
  }

  return (
    <div className="container mx-auto px-4 py-16">
      <h1 className="text-center mb-12">Project Portfolio</h1>
      <PortfolioGrid isSuperuser={user?.is_superuser || false} />
    </div>
  );
}
