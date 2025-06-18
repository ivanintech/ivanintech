import Link from "next/link";
import { FaGithub, FaExternalLinkAlt, FaThumbtack, FaCode } from "react-icons/fa";
import type { Project } from "@/types";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
// import { Separator } from '@/components/ui/separator';

interface ProjectCardProps {
  project: Project;
  onToggleFeatured?: (projectId: string) => void;
  isSuperuser?: boolean;
}

export function ProjectCard({
  project,
  onToggleFeatured,
  isSuperuser,
}: ProjectCardProps) {
  const {
    id,
    title,
    description,
    technologies,
    imageUrl,
    githubUrl,
    liveUrl,
    is_featured,
    videoUrl,
  } = project;

  // Determine if the video URL is a GIF or a video file
  const isGif = videoUrl?.endsWith('.gif');

  const handlePinClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (onToggleFeatured) {
      onToggleFeatured(id);
    }
  };

  return (
    <Card className="flex flex-col h-full overflow-hidden transition-transform duration-300 ease-in-out hover:shadow-xl hover:scale-140">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <CardTitle className="text-xl font-semibold mb-2 hover:text-primary transition-colors">
            {liveUrl ? (
              <Link
                href={liveUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:underline"
              >
                {title}
              </Link>
            ) : githubUrl ? (
              <Link
                href={githubUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="hover:underline"
              >
                {title}
              </Link>
            ) : (
              title
            )}
          </CardTitle>
          {isSuperuser && onToggleFeatured && (
            <button
              onClick={handlePinClick}
              title={is_featured ? "Remove from featured" : "Feature project"}
              className={`p-1 rounded-full transition-colors duration-200 
                          ${
                            is_featured
                              ? "text-primary hover:text-primary/80"
                              : "text-muted-foreground hover:text-foreground"
                          }`}
            >
              <FaThumbtack size={20} />
            </button>
          )}
        </div>
        {/* Media container */}
        <div className="aspect-video relative w-full mt-2 mb-2 overflow-hidden rounded-md bg-muted/50">
          {videoUrl ? (
            isGif ? (
              <img
                src={videoUrl}
                alt={`Animation of ${title}`}
                className="absolute top-0 left-0 w-full h-full object-cover transition-transform duration-500 ease-in-out group-hover:scale-110"
                loading="lazy"
              />
            ) : (
              <video
                src={videoUrl}
                title={`Animation of ${title}`}
                autoPlay
                loop
                muted
                playsInline
                className="object-cover w-full h-full transition-transform duration-500 ease-in-out group-hover:scale-110"
              />
            )
          ) : imageUrl ? (
            <img
              src={imageUrl}
              alt={`Image of ${title}`}
              className="absolute top-0 left-0 w-full h-full object-cover transition-transform duration-500 ease-in-out group-hover:scale-110"
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-slate-200 to-slate-300 dark:from-slate-800 dark:to-slate-900 flex items-center justify-center">
              <FaCode className="w-12 h-12 text-slate-500" />
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex-grow pb-3">
        <p className="text-sm text-muted-foreground line-clamp-3">
          {description || "No description available."}
        </p>
      </CardContent>
      {/* <Separator className="my-0" /> */}
      <CardFooter className="flex-col items-start pt-3 pb-3">
        {technologies && technologies.length > 0 && (
          <div className="mb-3">
            <h4 className="text-xs font-semibold mb-1.5 text-muted-foreground uppercase tracking-wider">
              Technologies:
            </h4>
            <div className="flex flex-wrap gap-1.5">
              {technologies.map((tech: string) => (
                <Badge key={tech} variant="secondary" className="text-xs">
                  {tech}
                </Badge>
              ))}
            </div>
          </div>
        )}
        <div className="flex items-center space-x-3 mt-auto pt-2 w-full justify-end">
          {githubUrl && (
            <Link
              href={githubUrl}
              target="_blank"
              rel="noopener noreferrer"
              aria-label={`GitHub repository for ${title}`}
              title="View on GitHub"
            >
              <FaGithub className="h-5 w-5 text-muted-foreground hover:text-foreground transition-colors" />
            </Link>
          )}
          {liveUrl && (
            <Link
              href={liveUrl}
              target="_blank"
              rel="noopener noreferrer"
              aria-label={`View ${title} live`}
              title="View live"
            >
              <FaExternalLinkAlt className="h-5 w-5 text-muted-foreground hover:text-foreground transition-colors" />
            </Link>
          )}
        </div>
      </CardFooter>
    </Card>
  );
}
