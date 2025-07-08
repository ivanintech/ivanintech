'use client';

import { useEffect, useState } from 'react';
import type { Project } from '@/types';
import apiClient from '@/lib/api-client';
import { AnimatedSection } from '@/components/ui/animated-section';
import { ProjectCard } from '@/components/portfolio/project-card';
import { ProjectCardSkeleton } from '@/components/portfolio/project-card-skeleton';

// Define the paginated response structure matching the backend
interface PaginatedProjectsResponse {
  items: Project[];
  total: number;
}

export function FeaturedProjectsList() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await apiClient<PaginatedProjectsResponse>('/projects/?limit=6');
        const allProjects = response.items || [];
        const featured = allProjects.filter((p: Project) => p.is_featured === true).slice(0, 3);
        
        // Si no hay proyectos destacados, muestra los 3 más recientes como fallback.
        if (featured.length > 0) {
          setProjects(featured);
        } else {
          setProjects(allProjects.slice(0, 3));
        }
      } catch (error) {
        console.error("Failed to fetch projects:", error);
        setProjects([]);
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <ProjectCardSkeleton />
        <ProjectCardSkeleton />
        <ProjectCardSkeleton />
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {projects.map((project, index) => (
        <AnimatedSection key={project.id} delay={index * 0.1}>
          <ProjectCard project={project} />
        </AnimatedSection>
      ))}
    </div>
  );
} 