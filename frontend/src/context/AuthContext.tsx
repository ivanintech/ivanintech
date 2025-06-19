'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import {
  loginUser as apiLoginUser,
  fetchCurrentUser as apiFetchCurrentUser,
} from '@/services/authService';
import { User, LoginResponse, UserCredentials } from '@/types/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  setAuthData: (data: LoginResponse) => void;
  loginWithCredentials: (credentials: UserCredentials) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    if (storedToken) {
      setToken(storedToken);
      apiFetchCurrentUser(storedToken)
        .then(setUser)
        .catch(() => {
          // Token inválido o expirado
          localStorage.removeItem('authToken');
          setToken(null);
          setUser(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);
  
  const setAuthData = (data: LoginResponse) => {
    localStorage.setItem('authToken', data.access_token);
    setToken(data.access_token);
    setUser(data.user);
  };

  const loginWithCredentials = async (credentials: UserCredentials) => {
    const response = await apiLoginUser(credentials);
    setAuthData(response);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('authToken');
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, setAuthData, loginWithCredentials, logout }}>
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