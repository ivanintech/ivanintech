// src/lib/api-client.ts
import type { ResourceLink } from "@/types"; // Asegúrate que la ruta a tus tipos es correcta

// Asegurarse de que la variable de entorno esté disponible
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

if (!API_BASE_URL) {
  // En el entorno del servidor (durante la construcción o SSR), esto lanzará un error si falta la variable.
  // En el cliente, puede que quieras manejarlo de otra forma, pero para Render esto es suficiente.
  throw new Error("Falta la variable de entorno NEXT_PUBLIC_API_BASE_URL");
}

// La URL completa a la API v1. Ahora es simplemente el valor de la variable de entorno.
// El valor que debes tener en Render es: https://ivanintech.onrender.com/api/v1
export const API_V1_URL = API_BASE_URL;

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