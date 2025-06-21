'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import {
  loginUser as apiLoginUser,
  fetchCurrentUser as apiFetchCurrentUser,
} from '@/services/authService';
import { setAuthToken } from '@/lib/api-client';
import { User, LoginResponse, UserCredentials } from '@/types/api';

export interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  avatarVersion: number;
  apiBaseUrl: string;
  bustAvatarCache: () => void;
  setAuthData: (data: LoginResponse) => void;
  loginWithCredentials: (credentials: UserCredentials) => Promise<void>;
  logout: () => void;
  setUser: React.Dispatch<React.SetStateAction<User | null>>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [avatarVersion, setAvatarVersion] = useState(1);
  const router = useRouter();

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

  if (!apiBaseUrl) {
    throw new Error("La variable de entorno NEXT_PUBLIC_API_BASE_URL no está definida.");
  }

  const bustAvatarCache = () => setAvatarVersion(v => v + 1);

  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    if (storedToken) {
      setToken(storedToken);
      setAuthToken(storedToken);
      apiFetchCurrentUser()
        .then(setUser)
        .catch(() => {
          // Token inválido o expirado
          localStorage.removeItem('authToken');
          setToken(null);
          setUser(null);
          setAuthToken(null);
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
    setAuthToken(data.access_token);
  };

  const loginWithCredentials = async (credentials: UserCredentials) => {
    const response = await apiLoginUser(credentials);
    setAuthData(response);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('authToken');
    setAuthToken(null);
    router.push('/login');
  };

  const value = {
    user,
    token,
    isLoading,
    avatarVersion,
    bustAvatarCache,
    apiBaseUrl,
    setAuthData,
    loginWithCredentials,
    logout,
    setUser,
  };

  return (
    <AuthContext.Provider value={value}>
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