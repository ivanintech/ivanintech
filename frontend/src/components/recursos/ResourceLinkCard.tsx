import React from 'react';
// import { ResourceLinkRead } from '@/types/api'; // Antigua importación
import type { ResourceLink } from '@/types'; // Nueva importación de nuestro tipo unificado
import { ExternalLink, Tag, Video, FileText, Github, BookOpen, MessageSquare, Star, Pin } from 'lucide-react'; // Añadir Pin

interface ResourceLinkCardProps {
  resource: ResourceLink;
  isAdmin: boolean;
  onTogglePin: (resourceId: string, currentPinStatus: boolean) => Promise<void>;
}

const ResourceLinkCard: React.FC<ResourceLinkCardProps> = ({ resource, isAdmin, onTogglePin }) => {
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

  const renderStars = (rating?: number | null) => {
    if (typeof rating !== 'number' || rating < 0 || rating > 5) {
      return null; // Or some default like "No rating"
    }
    const fullStars = Math.floor(rating);
    const halfStar = rating % 1 !== 0;
    const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);

    return (
      <div className="flex items-center">
        {[...Array(fullStars)].map((_, i) => (
          <Star key={`full-${i}`} className="w-4 h-4 text-yellow-400 fill-yellow-400" />
        ))}
        {halfStar && <Star key="half" className="w-4 h-4 text-yellow-400" /> /* Consider a half-filled icon */}
        {[...Array(emptyStars)].map((_, i) => (
          <Star key={`empty-${i}`} className="w-4 h-4 text-gray-300 dark:text-gray-600" />
        ))}
        <span className="ml-1.5 text-xs text-gray-500 dark:text-gray-400">({rating.toFixed(1)})</span>
      </div>
    );
  };

  return (
    <div className="relative bg-white dark:bg-gray-800 shadow-lg rounded-lg overflow-hidden transition-all duration-300 hover:shadow-xl flex flex-col h-full">
      {/* Pin Icon for Admins */}
      {isAdmin && (
        <button
          onClick={() => onTogglePin(resource.id, resource.is_pinned)}
          title={resource.is_pinned ? "Desfijar recurso" : "Fijar recurso"}
          className={`absolute top-2 right-2 z-10 p-1.5 rounded-full transition-colors duration-200 
                      ${resource.is_pinned 
                        ? 'bg-primary/80 hover:bg-primary text-primary-foreground' 
                        : 'bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-300'}
                    `}
        >
          <Pin className={`w-4 h-4 ${resource.is_pinned ? 'fill-current' : ''}`} />
        </button>
      )}

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
            {!resource.is_ivan_recommended && resource.rating !== null && resource.rating !== undefined && (
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {renderStars(resource.rating)}
                </div>
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

        {resource.personal_note && resource.is_ivan_recommended && (
          <div className="mt-auto pt-4 border-t border-gray-200 dark:border-gray-700">
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-1 flex items-center">
              <MessageSquare className="w-4 h-4 mr-2 text-amber-500" />
              Por qué lo recomiendo:
            </h4>
            <p className="text-gray-500 dark:text-gray-400 text-xs italic">
              {resource.personal_note}
            </p>
          </div>
        )}
        
        <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700 flex flex-wrap items-center justify-between text-xs text-gray-400 dark:text-gray-500">
          {resource.tags && (
            <div className="flex flex-wrap gap-1 mb-2 md:mb-0">
              {resource.tags.split(',').map((tag: string, index: number) => tag.trim()).filter((tag: string) => tag).map((tag: string, index: number) => (
                <span key={index} className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-xs">
                  #{tag}
                </span>
              ))}
            </div>
          )}
          {resource.created_at && (
            <span className="flex-shrink-0">
              {formatDate(resource.created_at)}
            </span>
          )}
        </div>

        {/* Author Name */}
        {resource.author_name && (
          <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
            Subido por: <span className="font-medium">{resource.author_name}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResourceLinkCard; 