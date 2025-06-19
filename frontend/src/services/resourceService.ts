import apiClient from '@/lib/api-client';
import type { ResourceLink, ResourceLinkCreate } from '@/types';

/**
 * Fetches all resource links.
 */
export const getResourceLinks = async (): Promise<ResourceLink[]> => {
  return apiClient<ResourceLink[]>('/resource-links/');
};

/**
 * Creates a new resource link.
 */
export const createResourceLink = async (
  token: string,
  resourceData: ResourceLinkCreate
): Promise<ResourceLink> => {
  return apiClient<ResourceLink>('/resource-links/', {
    method: 'POST',
    token,
    body: resourceData,
  });
};

/**
 * Pins a resource link.
 */
export const pinResource = async (token: string, resourceId: string): Promise<ResourceLink> => {
  return apiClient<ResourceLink>(`/resource-links/${resourceId}/pin`, {
    method: 'POST',
    token,
  });
};

/**
 * Unpins a resource link.
 */
export const unpinResource = async (token: string, resourceId: string): Promise<ResourceLink> => {
  return apiClient<ResourceLink>(`/resource-links/${resourceId}/unpin`, {
    method: 'POST',
    token,
  });
};

/**
 * Likes a resource link.
 */
export const likeResource = async (
  token: string,
  resourceId: string
): Promise<{ message: string; resource: ResourceLink | null }> => {
  return apiClient(`/resource-links/${resourceId}/like`, {
    method: 'POST',
    token,
  });
};

/**
 * Dislikes a resource link.
 */
export const dislikeResource = async (
  token: string,
  resourceId: string
): Promise<{ message:string; resource: ResourceLink | null }> => {
  return apiClient(`/resource-links/${resourceId}/dislike`, {
    method: 'POST',
    token,
  });
}; 