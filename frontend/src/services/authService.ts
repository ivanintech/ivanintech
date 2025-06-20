// frontend/src/services/authService.ts

import { LoginResponse, UserCredentials, User } from '@/types/api';
import apiClient from '@/lib/api-client';
import { auth as firebaseAuth } from '@/lib/firebase';
import { GoogleAuthProvider, signInWithPopup, getIdToken } from "firebase/auth";

/**
 * Logs in a user with email and password.
 */
export const loginUser = async (credentials: UserCredentials): Promise<LoginResponse> => {
  const body = new URLSearchParams(credentials as unknown as Record<string, string>);
  const response = await apiClient<LoginResponse>('/login/access-token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body,
    isFormData: true, // Para que no intente convertirlo a JSON
  });
  console.log('Respuesta de la API de login:', response);
  return response;
};

/**
 * Fetches the current logged-in user's data by validating a token.
 * The token is automatically sent by the apiClient.
 */
export const fetchCurrentUser = async (): Promise<User> => {
  // We use the /login/test-token endpoint as it's designed for token validation
  // and returns the user associated with it.
  return apiClient<User>('/login/test-token');
};

/**
 * Registers a new user.
 */
export const registerUser = async (credentials: UserCredentials): Promise<User> => {
    return apiClient<User>('/users/', {
        method: 'POST',
        body: credentials,
    });
};

/**
 * Handles the Google login flow.
 */
export const loginWithGoogle = async (): Promise<LoginResponse> => {
  if (!firebaseAuth) {
    throw new Error("Firebase is not configured. Google login is disabled.");
  }
  
  try {
    const provider = new GoogleAuthProvider();
    const result = await signInWithPopup(firebaseAuth, provider);
    const idToken = await getIdToken(result.user);

    return apiClient<LoginResponse>('/login/google', {
        method: 'POST',
        body: { token: idToken },
    });
    
  } catch (error: unknown) {
    if (error instanceof Error && 'code' in error && (error as { code: string }).code === 'auth/popup-closed-by-user') {
      throw new Error('Login process was canceled.');
    }
    // Re-lanza el error para que sea manejado por el componente que llama
    throw error;
  }
};

/**
 * Exchanges a GitHub auth code for our system's token.
 */
export const loginWithGitHubCode = async (code: string): Promise<LoginResponse> => {
    return apiClient<LoginResponse>('/login/github', {
        method: 'POST',
        body: { code },
    });
}; 