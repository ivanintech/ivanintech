const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

if (!API_BASE_URL) {
  throw new Error("Falta la variable de entorno NEXT_PUBLIC_API_BASE_URL");
}

type ApiClientOptions = {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  body?: any;
  token?: string | null;
  isFormData?: boolean;
};

// --- Almacenamiento del Token ---
let authToken: string | null = null;

// Función para establecer el token desde fuera del módulo (por ejemplo, desde AuthContext)
export const setAuthToken = (token: string | null) => {
  authToken = token;
};

// --- Cliente de API Centralizado ---
async function apiClient<T>(endpoint: string, options: ApiClientOptions = {}): Promise<T> {
  const { method = 'GET', body, token, isFormData = false } = options;

  // Usa el token global si no se proporciona uno específico
  const finalToken = token !== undefined ? token : authToken;

  const headers: Record<string, string> = { ...options.headers };

  if (finalToken) {
    headers['Authorization'] = `Bearer ${finalToken}`;
  }

  if (!isFormData) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(`${API_BASE_URL}/api/v1${endpoint}`, {
    method,
    headers,
    body: isFormData ? body : (body ? JSON.stringify(body) : null),
  });

  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = { detail: await response.text() };
    }
    console.error("API Error:", response.status, errorData);
    throw new Error(errorData.detail || `API request failed with status ${response.status}`);
  }

  // Handle cases with no content in response
  if (response.status === 204) {
    return null as T;
  }
  
  return response.json() as Promise<T>;
}

export default apiClient;
