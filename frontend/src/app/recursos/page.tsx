'use client';

import React, { useState, useEffect, useCallback } from 'react';
import type { ResourceLink, UserSession } from '@/types';
import { useAuth } from '@/context/AuthContext';
import { toast } from 'sonner';
import ResourceSection from '@/components/recursos/ResourceSection';
import ResourceForm from '@/components/recursos/ResourceForm';
import { LayoutDashboard, Users, Brain } from 'lucide-react'; // Icons for sections
import { getResourceLinks, pinResource, unpinResource } from '@/lib/api-client'; // Import API functions

const RecursosPage: React.FC = () => {
  const [allResources, setAllResources] = useState<ResourceLink[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth() as { user: UserSession | null }; // Cast user to UserSession or null

  const fetchResources = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getResourceLinks();
      setAllResources(data);
    } catch (err: any) {
      const errorMessage = err.message || 'Ocurrió un error desconocido al cargar recursos.';
      setError(errorMessage);
      toast.error(errorMessage);
    }
    setIsLoading(false);
  }, []);

  useEffect(() => {
    fetchResources();
  }, [fetchResources]);

  const handleTogglePin = async (resourceId: string, currentPinStatus: boolean) => {
    if (!user || !user.token) { // Assuming token is part of UserSession or accessible via useAuth
      toast.error("Debes estar autenticado para realizar esta acción.");
      return;
    }
    try {
      const action = currentPinStatus ? unpinResource : pinResource;
      const updatedResource = await action(resourceId, user.token);
      toast.success(`Recurso ${currentPinStatus ? 'desfijado' : 'fijado'} correctamente.`);
      // Re-fetch to get the correct order and reflect changes
      // Or, update local state more surgically:
      setAllResources(prevResources => 
        prevResources.map(r => r.id === resourceId ? { ...r, is_pinned: updatedResource.is_pinned } : r)
                     .sort((a, b) => (b.is_pinned ? 1 : -1) - (a.is_pinned ? 1 : -1) || new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      );
    } catch (err: any) {
      const errorMessage = err.message || `Error al ${currentPinStatus ? 'desfijar' : 'fijar'} el recurso.`;
      toast.error(errorMessage);
      console.error("Error toggling pin:", err);
    }
  };

  // Filter resources for different sections
  const ivanResources = allResources.filter(r => r.is_ivan_recommended);
  const communityResources = allResources.filter(r => !r.is_ivan_recommended);

  const isAdmin = user?.is_superuser || false;

  const handleIvanEdit = () => {
    toast.info("Función de editar recursos de Iván aún no implementada.");
  };

  const handleCommunityEdit = () => {
    toast.info("Función de editar recursos de la comunidad aún no implementada.");
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-blue-50 dark:from-gray-900 dark:to-blue-900/20 py-10 md:py-16">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        
        <header className="mb-12 text-center">
          <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-primary-500 to-secondary-500 dark:from-primary-400 dark:to-secondary-400 sm:text-6xl lg:text-7xl tracking-tight">
            Centro de Recursos
          </h1>
          <p className="mt-5 text-lg md:text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            Explora, comparte y descubre enlaces, herramientas y materiales de aprendizaje sobre Inteligencia Artificial y tecnología, seleccionados por Iván y la comunidad.
          </p>
        </header>

        {user && (
          <div className="mb-12">
            <ResourceForm onResourceAdded={fetchResources} />
          </div>
        )}

        {isLoading && (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
            <p className="ml-4 text-gray-600 dark:text-gray-400 text-lg">Cargando recursos...</p>
          </div>
        )}

        {error && !isLoading && !allResources.length && (
          <div className="text-center py-12 bg-red-100 dark:bg-red-900/20 p-8 rounded-xl shadow-lg">
            <Users size={48} className="mx-auto text-red-500 dark:text-red-400 mb-4" />
            <h3 className="text-xl font-semibold text-red-700 dark:text-red-300 mb-2">Ocurrió un Error</h3>
            <p className="text-red-600 dark:text-red-300">{error}</p>
            <button 
              onClick={fetchResources}
              className="mt-6 px-5 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
            >
              Intentar de Nuevo
            </button>
          </div>
        )}

        {!isLoading && !error && (
          <>
            {ivanResources.length > 0 && (
              <ResourceSection 
                title="Recomendados por Iván"
                resources={ivanResources} 
                initialCount={4} 
                isAdmin={isAdmin}
                onTogglePin={handleTogglePin}
                showEditIcon={isAdmin} 
                onEditClick={handleIvanEdit}
              />
            )}
            
            {communityResources.length > 0 && (
              <ResourceSection 
                title="Aportes de la Comunidad"
                resources={communityResources} 
                initialCount={8} 
                isAdmin={isAdmin}
                onTogglePin={handleTogglePin}
                showEditIcon={isAdmin} 
                onEditClick={handleCommunityEdit}
              />
            )}

            {!ivanResources.length && !communityResources.length && (
              <div className="text-center py-20">
                <Brain size={64} className="mx-auto text-gray-400 dark:text-gray-500 mb-6" />
                <h2 className="text-2xl font-semibold text-gray-700 dark:text-gray-300 mb-3">
                  Aún no hay tesoros por descubrir
                </h2>
                <p className="text-gray-500 dark:text-gray-400 max-w-md mx-auto">
                  {user ? "Sé el primero en compartir un recurso valioso con la comunidad usando el formulario de arriba." : "Parece que la base de conocimiento está vacía. Vuelve más tarde o inicia sesión para contribuir."}
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
};

export default RecursosPage; 