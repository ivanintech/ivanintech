import type { Project } from '@/types';
import apiClient from '@/lib/api-client';
import { AnimatedSection } from '@/components/ui/animated-section';
import { ProjectCard } from '@/components/portfolio/project-card';

async function getProjects(): Promise<Project[]> {
  try {
    const data = await apiClient<Project[]>('/projects/?limit=4');
    const featured = data.filter((p: Project) => p.is_featured || p.videoUrl).slice(0, 2);
    
    // Si no hay proyectos destacados, muestra los 2 más recientes como fallback.
    if (featured.length > 0) {
      return featured;
    }
    return data.slice(0, 2);

  } catch (error) {
    console.error("Failed to fetch projects:", error);
    return []; 
  }
}

export async function FeaturedProjectsList() {
  const projects = await getProjects();
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      {projects.map((project, index) => (
        <AnimatedSection key={project.id} delay={index * 0.1}>
          <ProjectCard project={project} />
        </AnimatedSection>
      ))}
    </div>
  );
} 