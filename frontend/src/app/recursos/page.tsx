'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import type { ResourceLink } from '@/types';
import { useAuth } from '@/context/AuthContext';
import { toast } from 'sonner';
import ResourceSection from '@/components/recursos/ResourceSection';
import ResourceForm from '@/components/recursos/ResourceForm';
import { getResourceLinks, pinResource, unpinResource, likeResource, dislikeResource } from '@/services/resourceService';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { LogIn } from 'lucide-react';

const capitalize = (s: string) => {
  if (typeof s !== 'string' || s.length === 0) return 'Otros';
  return s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();
};

const RecursosPage: React.FC = () => {
  const [resources, setResources] = useState<ResourceLink[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { user, token } = useAuth();
  const isAdmin = user?.is_superuser ?? false;
  const isLoggedIn = !!token;

  const fetchResources = useCallback(async () => {
    setIsLoading(true);
    try {
      const fetchedResources = await getResourceLinks();
      // Calcular la propiedad 'is_new' en el cliente
      const sevenDaysAgo = new Date();
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

      const processedResources = fetchedResources.map(res => ({
        ...res,
        is_new: new Date(res.created_at) > sevenDaysAgo,
      }));

      setResources(processedResources);
    } catch (error) {
      console.error('Error fetching resources:', error);
      toast.error('No se pudieron cargar los recursos.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchResources();
  }, [fetchResources]);

  const handleResourceAdded = (newResource: ResourceLink) => {
    fetchResources(); // Recargamos todo para re-ordenar
    toast.success(`Recurso "${newResource.title}" añadido con éxito.`);
  };

  const handleTogglePin = async (resourceId: string, currentPinStatus: boolean) => {
    if (!token) return;
    try {
      const action = currentPinStatus ? unpinResource : pinResource;
      await action(token, resourceId);
      // Recargamos todo para que el backend re-ordene correctamente
      fetchResources();
      toast.success(`Recurso ${currentPinStatus ? 'desfijado' : 'fijado'}.`);
    } catch (error) {
      console.error('Error pinning resource:', error);
      toast.error('Error al cambiar el estado de fijado.');
    }
  };

  const handleVote = async (resourceId: string, voteType: 'like' | 'dislike') => {
    if (!token) {
      toast.error("Debes iniciar sesión para votar.");
      return;
    }

    // Actualización optimista
    setResources(prev =>
      prev.map(r => {
        if (r.id === resourceId) {
          const newLikes = voteType === 'like' ? (r.likes || 0) + 1 : r.likes;
          const newDislikes = voteType === 'dislike' ? (r.dislikes || 0) + 1 : r.dislikes;
          return { ...r, likes: newLikes, dislikes: newDislikes };
        }
        return r;
      })
    );

    try {
      const action = voteType === 'like' ? likeResource : dislikeResource;
      const { message } = await action(token, resourceId);
      
      toast.info(message);
      // El backend ahora reordena y puede borrar, así que lo más seguro es recargar.
      await fetchResources();

    } catch (error) {
      const apiError = error as { response?: { data?: { detail?: string } } };
      const errorMessage = apiError?.response?.data?.detail || 'Error al registrar el voto.';
      toast.error(errorMessage);
      // Quitar la recarga en caso de error para no revertir el estado optimista inmediatamente
      // fetchResources(); 
    }
  };


  const groupedResources = useMemo(() => {
    if (resources.length === 0) return {};
    return resources.reduce((acc, resource) => {
      const type = resource.resource_type || 'General';
      if (!acc[type]) {
        acc[type] = [];
      }
      acc[type].push(resource);
      return acc;
    }, {} as Record<string, ResourceLink[]>);
  }, [resources]);

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="text-center mb-12">
        <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-5xl md:text-6xl">
          Centro de Recursos
        </h1>
        <p className="mt-3 max-w-2xl mx-auto text-lg text-gray-500 dark:text-gray-400 sm:mt-4">
          Una colección de herramientas, artículos y vídeos curada por la comunidad.
        </p>
      </header>

      {isLoggedIn && (
        <div className="mb-12 max-w-4xl mx-auto">
          <ResourceForm onResourceAdded={handleResourceAdded} />
        </div>
      )}

      {/* Mensaje para usuarios no logueados */}
      {!isLoggedIn && (
        <Link href="/login" className="block mb-12 transform hover:-translate-y-1 transition-transform duration-300 ease-in-out max-w-4xl mx-auto">
          <Card className="bg-secondary/40 border-primary/20 hover:border-primary/50 transition-all duration-300">
            <CardContent className="p-6 flex items-center justify-center space-x-4">
              <LogIn className="w-8 h-8 text-primary" />
              <div>
                <p className="font-bold text-lg text-primary">¡Únete a la comunidad!</p>
                <p className="text-muted-foreground">Inicia sesión para proponer recursos y participar.</p>
              </div>
            </CardContent>
          </Card>
        </Link>
      )}

      <main>
        {isLoading ? (
          <div className="text-center">
            <p className="text-lg text-gray-500 dark:text-gray-400">Cargando recursos...</p>
          </div>
        ) : (
          Object.keys(groupedResources).length > 0 ? (
            Object.entries(groupedResources).map(([type, links]) => (
                <ResourceSection
                    key={type}
                    title={capitalize(type)}
                    resources={links}
                    isAdmin={isAdmin}
                    isLoggedIn={isLoggedIn}
                    onTogglePin={handleTogglePin}
                    onVote={handleVote} // Pasar la nueva función
                />
            ))
          ) : (
            <div className="text-center py-16">
                 <p className="text-xl text-gray-600 dark:text-gray-400">No hay recursos disponibles en este momento.</p>
                 <p className="text-md text-gray-500 dark:text-gray-500 mt-2">¡Sé el primero en añadir uno!</p>
            </div>
          )
        )}
      </main>
    </div>
  );
};

export default RecursosPage;