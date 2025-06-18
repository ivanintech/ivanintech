'use client';

import { useState, useEffect, useCallback } from 'react'; // Removed Suspense
import type { Project } from '@/types'; // Changed path from @/lib/types to @/types
import { ProjectCard } from '@/components/project-card';
import { ProjectCardSkeleton } from '@/components/project-card-skeleton';
import { API_V1_URL } from '@/lib/api-client';
import { useAuth } from '@/context/AuthContext';

async function getProjectsApi(): Promise<Project[]> {
  let res: Response | undefined;
  try {
    res = await fetch(`${API_V1_URL}/projects`, {
      next: { revalidate: 3600 } 
    });
    if (!res.ok) {
      throw new Error(`Error ${res.status}: Failed to fetch projects (${res.statusText})`);
    }
    return await res.json();
  } catch (error: unknown) { // Changed to unknown
    console.error("Detailed error in getProjectsApi:", error);
    if (error instanceof Error) {
        throw new Error(`Could not load portfolio data: ${error.message}`);
    }
    throw new Error('Could not load portfolio data due to an unknown error.'); 
  }
}

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
    } catch (err: unknown) { // Changed to unknown
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Unknown error loading projects.');
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const handleToggleFeatured = async (projectId: string) => {
    if (!token) {
      console.error("No auth token found for toggling featured status.");
      setError("Action not allowed. You must be logged in.");
      return;
    }
    try {
      const res = await fetch(`${API_V1_URL}/projects/${projectId}/toggle-featured/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: 'Error changing featured status' }));
        throw new Error(errorData.detail || `Error ${res.status}`);
      }
      await fetchProjects(); 
    } catch (err: unknown) { // Changed to unknown
      console.error("Error toggling featured status:", err);
      if (err instanceof Error) {
        alert(`Error changing status: ${err.message}`);
      } else {
        alert('Unknown error changing featured status.');
      }
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