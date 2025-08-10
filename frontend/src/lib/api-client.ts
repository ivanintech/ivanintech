// Función para obtener la URL base de la API de forma segura
function getApiBaseUrl() {
  if (typeof window === 'undefined') {
    return 'http://backend:8000';
  }
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  if (!apiBaseUrl) {
    throw new Error("Falta la variable de entorno NEXT_PUBLIC_API_BASE_URL");
  }
  return apiBaseUrl;
}

// Log para depuración en el navegador del cliente
if (typeof window !== 'undefined') {
  console.log(`[CONFIG] Frontend loaded with API_BASE_URL: ${getApiBaseUrl()}`);
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
if (typeof window !== 'undefined') {
    authToken = localStorage.getItem('token');
}


// Función para establecer el token desde fuera del módulo (por ejemplo, desde AuthContext)
export const setAuthToken = (token: string | null) => {
  authToken = token;
  if (typeof window !== 'undefined') {
      if (token) {
          localStorage.setItem('token', token);
      } else {
          localStorage.removeItem('token');
      }
  }
};

// --- Cliente de API Centralizado con Reintentos ---
async function apiClient<T>(endpoint: string, options: ApiClientOptions = {}): Promise<T> {
  const { method = 'GET', body, token, isFormData = false } = options;
  const maxRetries = 3;
  let lastError: Error | null = null;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      // Usa el token global si no se proporciona uno específico
      const finalToken = token !== undefined ? token : authToken;

      const headers: Record<string, string> = { ...options.headers };

      if (finalToken) {
        headers['Authorization'] = `Bearer ${finalToken}`;
      }

      if (!isFormData) {
        headers['Content-Type'] = 'application/json';
      }

      const API_BASE_URL = getApiBaseUrl();
      const base = API_BASE_URL.endsWith('/api/v1') 
        ? API_BASE_URL 
        : `${API_BASE_URL}/api/v1`;

      const url = `${base}${endpoint}`;
      
      // Log para debugging en desarrollo
      if (process.env.NODE_ENV === 'development') {
        console.log(`[API] Attempt ${attempt}/${maxRetries}: ${method} ${url}`);
      }

      const response = await fetch(url, {
        method,
        headers: {
          ...headers,
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        },
        body: isFormData ? body : (body ? JSON.stringify(body) : null),
      });

      if (!response.ok) {
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          errorData = { detail: await response.text() };
        }
        
        // Si es un error 500 o CORS, reintentar
        if (response.status >= 500 || response.status === 0) {
          throw new Error(`Server error: ${response.status} - ${errorData.detail || 'Unknown error'}`);
        }
        
        // Para otros errores (4xx), no reintentar
        console.error("API Error:", response.status, errorData);
        throw new Error(errorData.detail || `API request failed with status ${response.status}`);
      }

      if (response.status === 204) {
        return null as T;
      }
      
      return response.json() as Promise<T>;
      
    } catch (error) {
      lastError = error as Error;
      
      // Si es el último intento, lanzar el error
      if (attempt === maxRetries) {
        console.error(`[API] Final attempt failed after ${maxRetries} retries:`, error);
        throw error;
      }
      
      // Esperar antes del siguiente intento (backoff exponencial)
      const delay = Math.min(1000 * Math.pow(2, attempt - 1), 5000);
      console.warn(`[API] Attempt ${attempt} failed, retrying in ${delay}ms:`, error);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw lastError || new Error('Unknown API error');
}

export default apiClient;
