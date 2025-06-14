// src/lib/api-client.ts
import type { ResourceLink } from "@/types"; // Asegúrate que la ruta a tus tipos es correcta

// Asegúrate de que este puerto coincida con donde corre tu backend FastAPI
// Cambiar a localhost en lugar de 127.0.0.1 para probar
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export const API_V1_URL = `${API_BASE_URL}/api/v1`;

// Función genérica para manejar errores de fetch
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.text();
    console.error("API Error:", response.status, errorData);
    throw new Error(`API request failed with status ${response.status}: ${errorData}`);
  }
  return response.json() as Promise<T>;
}

export async function getResourceLinks(): Promise<ResourceLink[]> {
  const response = await fetch(`${API_V1_URL}/resource-links/`);
  return handleResponse<ResourceLink[]>(response);
}

export async function getResourceLinkById(id: string): Promise<ResourceLink> {
  const response = await fetch(`${API_V1_URL}/resource-links/${id}`);
  return handleResponse<ResourceLink>(response);
}

export async function pinResource(resourceId: string, token: string): Promise<ResourceLink> {
  const response = await fetch(`${API_V1_URL}/resource-links/${resourceId}/pin`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  return handleResponse<ResourceLink>(response);
}

export async function unpinResource(resourceId: string, token: string): Promise<ResourceLink> {
  const response = await fetch(`${API_V1_URL}/resource-links/${resourceId}/unpin`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  return handleResponse<ResourceLink>(response);
}

// --- Nuevas funciones para Votos ---

export async function likeResource(token: string, resourceId: string): Promise<{ message: string; resource: ResourceLink | null }> {
  const response = await fetch(`${API_V1_URL}/resource-links/${resourceId}/like`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  return handleResponse<{ message: string; resource: ResourceLink | null }>(response);
}

export async function dislikeResource(token: string, resourceId: string): Promise<{ message: string; resource: ResourceLink | null }> {
  const response = await fetch(`${API_V1_URL}/resource-links/${resourceId}/dislike`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });
  return handleResponse<{ message: string; resource: ResourceLink | null }>(response);
}

// Podríamos añadir una función para crear/actualizar recursos aquí también si es necesario
// export async function createResourceLink(data: any, token: string): Promise<ResourceLink> { ... }

// Podríamos añadir funciones fetch genéricas aquí más adelante
// export async function fetchData(endpoint: string) { ... }