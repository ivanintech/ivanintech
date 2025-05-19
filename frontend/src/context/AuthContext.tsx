'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import {
  loginUser as apiLoginUser,
  registerUser as apiRegisterUser,
  fetchCurrentUser as apiFetchCurrentUser,
  User,
  TokenResponse
} from '@/services/authService';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true); // Start with loading true to check for token
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    if (storedToken) {
      setToken(storedToken);
      apiFetchCurrentUser(storedToken)
        .then(fetchedUser => {
          console.log("Usuario obtenido de apiFetchCurrentUser:", fetchedUser); 
          setUser(fetchedUser);
        })
        .catch((err) => { 
          console.error("Error en apiFetchCurrentUser:", err);
          localStorage.removeItem('authToken');
          setToken(null);
          setUser(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      console.log("No se encontró authToken en localStorage."); 
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const tokenResponse = await apiLoginUser(email, password);
      localStorage.setItem('authToken', tokenResponse.access_token);
      setToken(tokenResponse.access_token);
      const currentUser = await apiFetchCurrentUser(tokenResponse.access_token);
      setUser(currentUser);
      router.push('/'); // Redirect to home page after login
    } catch (err: any) {
      setError(err.message || 'Login failed');
      setUser(null);
      setToken(null);
      localStorage.removeItem('authToken');
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, fullName?: string) => {
    setIsLoading(true);
    setError(null);
    try {
      // Backend's /users/ endpoint returns the created user, not a token directly.
      // For auto-login after register, we'd call loginUser after successful registration.
      await apiRegisterUser(email, password, fullName);
      // Optionally, log the user in automatically after registration:
      // await login(email, password); 
      // Or redirect to login page with a success message:
      router.push('/login?registered=true'); // Example redirect
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('authToken');
    router.push('/login'); // Redirect to login page after logout
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, error, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 