import React, { useState } from 'react';
// import { ResourceLinkRead } from '@/types/api'; // Old import
import type { ResourceLink } from '@/types'; // New import
import ResourceLinkCard from './ResourceLinkCard'; 
import { Edit3 } from 'lucide-react'; 

interface ResourceSectionProps {
  title: string;
  resources: ResourceLink[]; // Use new ResourceLink type
  initialCount?: number;
  showEditIcon?: boolean;
  onEditClick?: () => void;
  isAdmin: boolean; // New prop
  onTogglePin: (resourceId: string, currentPinStatus: boolean) => Promise<void>; // New prop
}

const ResourceSection: React.FC<ResourceSectionProps> = ({ 
  title, 
  resources, 
  initialCount = 4, 
  showEditIcon = false,
  onEditClick,
  isAdmin, // Destructure new prop
  onTogglePin // Destructure new prop
}) => {
  const [showAll, setShowAll] = useState(false);

  if (!resources || resources.length === 0) {
    return null; 
  }

  const displayedResources = showAll ? resources : resources.slice(0, initialCount);

  return (
    <section className="mb-12 md:mb-16">
      <div className="flex justify-between items-center mb-6 md:mb-8 pb-3 border-b border-gray-300 dark:border-gray-700">
        <h2 className="text-2xl md:text-3xl font-bold text-gray-800 dark:text-white">
          {title}
        </h2>
        {showEditIcon && onEditClick && (
          <button 
            onClick={onEditClick}
            className="p-2 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            aria-label={`Editar sección ${title}`}
          >
            <Edit3 className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>
        )}
      </div>

      {displayedResources.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8">
          {displayedResources.map(resource => (
            <ResourceLinkCard 
              key={resource.id} 
              resource={resource} 
              isAdmin={isAdmin} // Pass isAdmin
              onTogglePin={onTogglePin} // Pass onTogglePin
            />
          ))}
        </div>
      ) : (
        <p className="text-gray-500 dark:text-gray-400">
          No hay recursos en esta sección por el momento.
        </p>
      )}

      {resources.length > initialCount && (
        <div className="mt-8 text-center">
          <button
            onClick={() => setShowAll(!showAll)}
            className="px-6 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900 transition-all duration-200 ease-in-out shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
          >
            {showAll ? 'Ver menos' : 'Ver más'}
          </button>
        </div>
      )}
    </section>
  );
};

export default ResourceSection; 