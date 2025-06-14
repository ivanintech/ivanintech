import React, { useState } from 'react';
import type { ResourceLink } from '@/types';
import { ExternalLink, Tag, Video, FileText, Github, BookOpen, ThumbsUp, ThumbsDown, Pin } from 'lucide-react';
import { cn } from '@/lib/utils'; // Importar cn para clases condicionales

interface ResourceLinkCardProps {
  resource: ResourceLink;
  isAdmin: boolean;
  isLoggedIn: boolean; // Necesitamos saber si el usuario está logueado para mostrar los botones de voto
  onTogglePin: (resourceId: string, currentPinStatus: boolean) => Promise<void>;
  onVote: (resourceId: string, voteType: 'like' | 'dislike') => Promise<void>; // Para notificar al padre
}

const ResourceLinkCard: React.FC<ResourceLinkCardProps> = ({ resource, isAdmin, isLoggedIn, onTogglePin, onVote }) => {
  const [isVoting, setIsVoting] = useState(false);

  const handleVote = async (voteType: 'like' | 'dislike') => {
    if (isVoting) return;
    setIsVoting(true);
    try {
      await onVote(resource.id, voteType);
    } catch (error) {
      console.error(`Error al votar ${voteType}`, error);
      // Aquí podrías mostrar una notificación de error al usuario
    } finally {
      setIsVoting(false);
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const getResourceTypeIcon = (resourceType?: string) => {
    switch (resourceType?.toLowerCase()) {
      case 'video':
        return <Video className="w-5 h-5 mr-2 text-blue-500" />;
      case 'artículo':
      case 'article':
        return <FileText className="w-5 h-5 mr-2 text-green-500" />;
      case 'github':
        return <Github className="w-5 h-5 mr-2 text-gray-700 dark:text-gray-300" />;
      case 'documentación':
      case 'documentation':
        return <BookOpen className="w-5 h-5 mr-2 text-purple-500" />;
      default:
        return <Tag className="w-5 h-5 mr-2 text-gray-500" />;
    }
  };

  return (
    <div className="relative bg-white dark:bg-gray-800 shadow-lg rounded-lg overflow-hidden transition-all duration-300 hover:shadow-xl flex flex-col h-full group">
      {/* Pin & New Badges */}
      <div className="absolute top-2 right-2 z-10 flex flex-col items-end gap-2">
        {isAdmin && (
          <button
            onClick={() => onTogglePin(resource.id, resource.is_pinned)}
            title={resource.is_pinned ? "Desfijar recurso" : "Fijar recurso"}
            className={cn(
              "p-1.5 rounded-full transition-colors duration-200",
              resource.is_pinned
                ? 'bg-primary/80 hover:bg-primary text-primary-foreground'
                : 'bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-300'
            )}
          >
            <Pin className={cn("w-4 h-4", resource.is_pinned && 'fill-current')} />
          </button>
        )}
        {resource.is_new && (
           <span className="px-2 py-1 text-xs font-bold text-white bg-green-500 rounded-md shadow-sm animate-pulse">
             NUEVO
           </span>
        )}
      </div>

      {resource.thumbnail_url && (
        <a href={String(resource.url)} target="_blank" rel="noopener noreferrer" className="block h-48 overflow-hidden">
          <img 
            src={String(resource.thumbnail_url)} 
            alt={`Thumbnail de ${resource.title}`} 
            className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
          />
        </a>
      )}
      <div className="p-5 flex flex-col flex-grow">
        <div className="mb-3">
          <div className="flex justify-between items-start mb-1.5">
            {resource.resource_type && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                {getResourceTypeIcon(resource.resource_type)}
                {resource.resource_type}
              </span>
            )}
          </div>
          <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-1">
            <a 
              href={String(resource.url)} 
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-200 flex items-center group"
            >
              {resource.title}
              <ExternalLink className="w-4 h-4 ml-2 opacity-70 group-hover:opacity-100" />
            </a>
          </h3>
        </div>

        {resource.ai_generated_description && (
          <p className="text-gray-600 dark:text-gray-300 text-sm mb-4 flex-grow">
            {resource.ai_generated_description}
          </p>
        )}

        <div className="mt-auto pt-4 border-t border-gray-200 dark:border-gray-700 space-y-3">
          {/* Likes/Dislikes Section */}
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <button
                onClick={() => handleVote('like')}
                disabled={!isLoggedIn || isVoting}
                className={cn(
                  "flex items-center gap-1.5 text-sm font-medium text-gray-500 dark:text-gray-400 transition-colors",
                  isLoggedIn ? "hover:text-green-500" : "cursor-not-allowed opacity-60"
                )}
                title={isLoggedIn ? "Me gusta" : "Inicia sesión para votar"}
              >
                <ThumbsUp className="w-4 h-4" />
                <span>{resource.likes}</span>
              </button>
              <button
                onClick={() => handleVote('dislike')}
                disabled={!isLoggedIn || isVoting}
                className={cn(
                  "flex items-center gap-1.5 text-sm font-medium text-gray-500 dark:text-gray-400 transition-colors",
                  isLoggedIn ? "hover:text-red-500" : "cursor-not-allowed opacity-60"
                )}
                title={isLoggedIn ? "No me gusta" : "Inicia sesión para votar"}
              >
                <ThumbsDown className="w-4 h-4" />
                <span>{resource.dislikes}</span>
              </button>
            </div>
            {resource.created_at && (
              <span className="text-xs text-gray-400 dark:text-gray-500 flex-shrink-0">
                {formatDate(resource.created_at)}
              </span>
            )}
          </div>
          
          {/* Tags */}
          {resource.tags && (
            <div className="flex flex-wrap gap-1">
              {resource.tags.split(',').map((tag: string) => tag.trim()).filter(tag => tag).map((tag: string, index: number) => (
                <span key={index} className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-xs">
                  #{tag}
                </span>
              ))}
            </div>
          )}
          
          {/* Author */}
          {resource.author_name && (
            <div className="text-xs text-gray-500 dark:text-gray-400 pt-2 border-t border-gray-200 dark:border-gray-700/50">
              Subido por: <span className="font-medium text-gray-600 dark:text-gray-300">{resource.author_name}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResourceLinkCard;