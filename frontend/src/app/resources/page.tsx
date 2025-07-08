'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import type { ResourceLink, ResourceLinkUpdate } from '@/types';
import { useAuth } from '@/context/AuthContext';
import { toast } from 'sonner';
import ResourceSection from '@/components/resources/ResourceSection';
import ResourceForm from '@/components/resources/ResourceForm';
import { getResourceLinks, pinResource, unpinResource, likeResource, dislikeResource, updateResource, deleteResource } from '@/services/resourceService';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { LogIn } from 'lucide-react';
import { EditResourceModal } from '@/components/admin/EditResourceModal';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

const capitalize = (s: string) => {
  if (typeof s !== 'string' || s.length === 0) return 'Others';
  return s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();
};

const ResourcesPage: React.FC = () => {
  const [resources, setResources] = useState<ResourceLink[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { user, token } = useAuth();
  const isAdmin = user?.is_superuser ?? false;
  const isLoggedIn = !!token;

  const [editingItem, setEditingItem] = useState<ResourceLink | null>(null);
  const [deletingItem, setDeletingItem] = useState<ResourceLink | null>(null);

  const fetchResources = useCallback(async () => {
    setIsLoading(true);
    try {
      // The service now returns a paginated object. We need to get the .items property.
      const response = await getResourceLinks();
      const fetchedResources = response.items || [];

      // Calculate 'is_new' property on the client
      const sevenDaysAgo = new Date();
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

      const processedResources = fetchedResources.map(res => ({
        ...res,
        is_new: new Date(res.created_at) > sevenDaysAgo,
      }));

      setResources(processedResources);
    } catch (error) {
      console.error('Error fetching resources:', error);
      toast.error('Could not load resources.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchResources();
  }, [fetchResources]);

  const handleResourceAdded = (newResource: ResourceLink) => {
    fetchResources(); // Reload everything to reorder
    toast.success(`Resource "${newResource.title}" added successfully.`);
  };

  const handleTogglePin = async (resourceId: string, currentPinStatus: boolean) => {
    if (!token) return;
    try {
      const action = currentPinStatus ? unpinResource : pinResource;
      await action(token, resourceId);
      // Reload everything so the backend reorders correctly
      fetchResources();
      toast.success(`Resource ${currentPinStatus ? 'unpinned' : 'pinned'}.`);
    } catch (error) {
      console.error('Error pinning resource:', error);
      toast.error('Error changing pin status.');
    }
  };

  const handleVote = async (resourceId: string, voteType: 'like' | 'dislike') => {
    if (!token) {
      toast.error("You must be logged in to vote.");
      return;
    }

    // Optimistic update
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
      // The backend now reorders and can delete, so it's safest to reload.
      await fetchResources();

    } catch (error) {
      const apiError = error as { response?: { data?: { detail?: string } } };
      const errorMessage = apiError?.response?.data?.detail || 'Error submitting vote.';
      toast.error(errorMessage);
      // Don't reload on error to avoid reverting the optimistic state immediately
      // fetchResources(); 
    }
  };

  const handleOpenEditModal = (resource: ResourceLink) => {
    setEditingItem(resource);
  };
  
  const handleOpenDeleteDialog = (resource: ResourceLink) => {
    setDeletingItem(resource);
  };

  const handleUpdateResource = async (itemData: ResourceLinkUpdate) => {
    if (!editingItem || !token) return;
    
    try {
      const updatedItem = await updateResource(editingItem.id, itemData, token);
      setResources(resources.map(item => item.id === updatedItem.id ? { ...item, ...updatedItem } : item));
      toast.success("Resource updated successfully.");
      setEditingItem(null);
    } catch (error) {
      console.error("Failed to update resource:", error);
      toast.error("Could not update resource.");
    }
  };

  const handleDeleteResource = async () => {
    if (!deletingItem || !token) return;

    try {
      await deleteResource(deletingItem.id, token);
      setResources(resources.filter(item => item.id !== deletingItem.id));
      toast.success("Resource deleted.");
      setDeletingItem(null);
    } catch (error) {
      console.error("Failed to delete resource:", error);
      toast.error("Could not delete resource.");
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
          Resource Hub
        </h1>
        <p className="mt-3 max-w-2xl mx-auto text-lg text-gray-500 dark:text-gray-400 sm:mt-4">
          A collection of tools, articles, and videos curated by the community.
        </p>
      </header>
      {isLoggedIn && (
        <div className="mb-12 max-w-4xl mx-auto">
          <ResourceForm onResourceAdded={handleResourceAdded} />
        </div>
      )}
      {/* Message for non-logged-in users */}
      {!isLoggedIn && (
        <Link
          href="/login"
          className="block mb-12 transform hover:-translate-y-1 transition-transform duration-300 ease-in-out max-w-4xl mx-auto"
          legacyBehavior>
          <Card className="bg-secondary/40 border-primary/20 hover:border-primary/50 transition-all duration-300">
            <CardContent className="p-6 flex items-center justify-center space-x-4">
              <LogIn className="w-8 h-8 text-primary" />
              <div>
                <p className="font-bold text-lg text-primary">Join the community!</p>
                <p className="text-muted-foreground">Log in to suggest resources and participate.</p>
              </div>
            </CardContent>
          </Card>
        </Link>
      )}
      <main className="mt-8">
        {isLoading ? (
          <div className="text-center">
            <p className="text-lg text-gray-500 dark:text-gray-400">Loading resources...</p>
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
                    onVote={handleVote}
                    onEdit={handleOpenEditModal}
                    onDelete={handleOpenDeleteDialog}
                />
            ))
          ) : (
            <div className="text-center py-16">
                 <p className="text-xl text-gray-600 dark:text-gray-400">No resources available at the moment.</p>
                 <p className="text-md text-gray-500 dark:text-gray-500 mt-2">Be the first to add one!</p>
            </div>
          )
        )}
      </main>
      <EditResourceModal
        isOpen={!!editingItem}
        onClose={() => setEditingItem(null)}
        onConfirm={handleUpdateResource}
        itemToEdit={editingItem}
      />
      <AlertDialog open={!!deletingItem} onOpenChange={() => setDeletingItem(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action is permanent and cannot be undone. The resource
              &quot;{deletingItem?.title}&quot; will be deleted.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setDeletingItem(null)}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDeleteResource}>
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default ResourcesPage;