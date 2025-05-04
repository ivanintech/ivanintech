// src/lib/api-client.ts

// Asegúrate de que este puerto coincida con donde corre tu backend FastAPI
// Cambiar a localhost en lugar de 127.0.0.1 para probar
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export const API_V1_URL = `${API_BASE_URL}/api/v1`;

// Podríamos añadir funciones fetch genéricas aquí más adelante
// export async function fetchData(endpoint: string) { ... } 