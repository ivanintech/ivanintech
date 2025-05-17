import Image from 'next/image';
import Link from 'next/link';
import type { Project } from '@/lib/types';

export function ProjectCard({ project }: { project: Project }) {
  return (
    <div className="border border-border rounded-lg overflow-hidden shadow-sm hover:shadow-xl transition-all duration-300 bg-muted/50 dark:bg-muted/10 flex flex-col group hover:scale-[2]">
      {/* Media: Video > Imagen > Placeholder */}
      <div className="aspect-video bg-muted flex items-center justify-center text-muted-foreground overflow-hidden">
        {project.videoUrl ? (
          <video 
            src={project.videoUrl} 
            width="400" 
            height="225" 
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" 
            autoPlay 
            loop 
            muted 
            playsInline // Importante para iOS
            preload="metadata" // Carga solo metadatos inicialmente
          >
            Tu navegador no soporta el tag de vídeo.
            {/* Podríamos añadir <source> para múltiples formatos si los conviertes */}
            {/* <source src="/path/to/video.mp4" type="video/mp4"> */}
            {/* <source src="/path/to/video.webm" type="video/webm"> */}
          </video>
        ) : project.imageUrl ? (
          <Image 
              src={project.imageUrl}
              alt={`Imagen del proyecto ${project.title}`}
              width={400} 
              height={225}
              className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
        ) : (
          <span className="text-xs">(Media Proyecto)</span> // Cambiar texto placeholder
        )}
      </div>
      {/* Contenido */}
      <div className="p-5 flex flex-col flex-grow">
        <h3 className="text-lg font-semibold mb-2">{project.title}</h3> {/* Re-añadir text-lg y font-semibold */}
        <p className="text-sm text-muted-foreground mb-4 flex-grow">{project.description}</p>
        {/* Tecnologías */}
        <div className="mb-4">
          {project.technologies.map((tech) => (
            <span 
              key={tech} 
              className="inline-block bg-primary/10 text-primary dark:bg-primary/20 dark:text-blue-300 text-[0.7rem] font-medium tracking-wider mr-1.5 mb-1.5 px-2.5 py-0.5 rounded-full"
            >
              {tech.toUpperCase()}
            </span>
          ))}
        </div>
        {/* Enlaces */}
        <div className="flex justify-end space-x-3 mt-auto">
          {project.githubUrl && (
            <Link href={project.githubUrl} target="_blank" rel="noopener noreferrer" className="text-sm text-primary hover:underline font-medium">
              GitHub
            </Link>
          )}
          {project.liveUrl && (
            <Link href={project.liveUrl} target="_blank" rel="noopener noreferrer" className="text-sm text-accent hover:underline font-medium">
              Demo
            </Link>
          )}
        </div>
      </div>
    </div>
  );
} 