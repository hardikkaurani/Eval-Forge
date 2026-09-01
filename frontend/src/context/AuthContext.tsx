import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    try {
      const storedToken = localStorage.getItem(TOKEN_KEY) || localStorage.getItem('token');
      const storedUser = localStorage.getItem(USER_KEY);

      if (storedToken && storedUser) {
        const parsedUser = JSON.parse(storedUser);
        if (parsedUser && parsedUser.id && parsedUser.email) {
          setToken(storedToken);
          setUser(parsedUser);
        } else {
          // Incomplete or invalid stored user payload
          localStorage.removeItem(TOKEN_KEY);
          localStorage.removeItem('token');
          localStorage.removeItem(USER_KEY);
          setToken(null);
          setUser(null);
        }
      } else {
        // Token without verified user payload is invalid
        if (storedToken || storedUser) {
          localStorage.removeItem(TOKEN_KEY);
          localStorage.removeItem('token');
          localStorage.removeItem(USER_KEY);
        }
        setToken(null);
        setUser(null);
      }
    } catch {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem('token');
      localStorage.removeItem(USER_KEY);
      setToken(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const login = (newToken: string, newUser: User) => {
    if (!newToken || !newUser || !newUser.id || !newUser.email) {
      console.error('Invalid login payload: Token and User details are required');
      return;
    }
    setToken(newToken);
    setUser(newUser);
    localStorage.setItem(TOKEN_KEY, newToken);
    localStorage.setItem(USER_KEY, JSON.stringify(newUser));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem('token');
    localStorage.removeItem(USER_KEY);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
