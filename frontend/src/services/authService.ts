// frontend/src/services/authService.ts

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const API_V1_STR = '/api/v1'; // Assuming your backend API v1 string

export interface User {
  id: number | string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  // Add any other fields your User schema returns
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export const loginUser = async (email: string, password: string): Promise<TokenResponse> => {
  const formData = new URLSearchParams();
  formData.append('username', email); // FastAPI's OAuth2PasswordRequestForm uses 'username'
  formData.append('password', password);

  const response = await fetch(`${API_BASE_URL}${API_V1_STR}/login/access-token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData.toString(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Login failed' }));
    throw new Error(errorData.detail || 'Failed to login');
  }
  return response.json();
};

export const registerUser = async (email: string, password: string, fullName?: string): Promise<User> => {
  const userData: any = {
    email,
    password,
  };
  if (fullName) {
    userData.full_name = fullName;
  }

  const response = await fetch(`${API_BASE_URL}${API_V1_STR}/users/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Registration failed' }));
    throw new Error(errorData.detail || 'Failed to register');
  }
  return response.json();
};

export const fetchCurrentUser = async (token: string): Promise<User> => {
  const response = await fetch(`${API_BASE_URL}${API_V1_STR}/login/test-token`, { // or /users/me if you create it
    method: 'POST', // The test-token endpoint is POST in your backend
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Failed to fetch user' }));
    throw new Error(errorData.detail || 'Failed to fetch current user');
  }
  return response.json();
}; 