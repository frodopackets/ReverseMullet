'use client'

import React, { createContext, useContext, useEffect, useState } from 'react';
import { authService, AuthUser } from '@/lib/auth-service';

interface AuthContextType {
  user: AuthUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  signOut: () => Promise<void>;
  getAuthToken: () => Promise<string | null>;
  authMode: 'alb' | 'amplify';
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const authMode = (process.env.NEXT_PUBLIC_AUTH_MODE as 'alb' | 'amplify') || 'alb';

  useEffect(() => {
    checkAuthState();
  }, []);

  const checkAuthState = async () => {
    try {
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      console.error('Auth check failed:', error);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignOut = async () => {
    try {
      await authService.signOut();
      setUser(null);
    } catch (error) {
      console.error('Error signing out:', error);
      throw error;
    }
  };

  const getAuthToken = async (): Promise<string | null> => {
    try {
      return await authService.getAuthToken();
    } catch (error) {
      console.error('Error getting auth token:', error);
      return null;
    }
  };

  const value = {
    user,
    isLoading,
    isAuthenticated: !!user,
    signOut: handleSignOut,
    getAuthToken,
    authMode,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}