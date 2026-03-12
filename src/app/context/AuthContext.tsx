import { createContext, useContext, useState, ReactNode, useEffect } from "react";
import { authAPI, getToken, setToken, removeToken } from "../services/api";

interface User {
  id: string;
  name: string;
  email: string;
  phone?: string;
  role: string;
  profile_image?: string;
  wallet_balance: number;
}

interface AuthContextType {
  isLoggedIn: boolean;
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string, phone?: string) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if token exists on mount
  useEffect(() => {
    const token = getToken();
    if (token) {
      // Try to get current user
      authAPI.getCurrentUser()
        .then(data => {
          setUser(data);
          setIsLoggedIn(true);
        })
        .catch(() => {
          removeToken();
          setIsLoggedIn(false);
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const data = await authAPI.login(email, password);
      if (data.access_token) {
        setToken(data.access_token);
        setUser(data.user);
        setIsLoggedIn(true);
      }
    } catch (error) {
      throw error;
    }
  };

  const register = async (name: string, email: string, password: string, phone?: string) => {
    try {
      const data = await authAPI.register({ name, email, password, phone });
      if (data.access_token) {
        setToken(data.access_token);
        setUser(data.user);
        setIsLoggedIn(true);
      }
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch {
      // Ignore errors on logout
    } finally {
      removeToken();
      setIsLoggedIn(false);
      setUser(null);
    }
  };

  const updateProfile = async (data: Partial<User>) => {
    try {
      const response = await authAPI.updateProfile(data as any);
      setUser(response.user);
    } catch (error) {
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, user, isLoading, login, register, logout, updateProfile }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
