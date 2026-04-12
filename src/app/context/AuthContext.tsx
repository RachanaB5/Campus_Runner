import { createContext, useContext, useState, ReactNode, useEffect } from "react";
import { authAPI, getToken, setToken, removeToken, API_BASE_URL } from "../services/api";
import { disconnectSocket } from "../services/socket";

interface User {
  id: string;
  name: string;
  email: string;
  phone?: string;
  role: string;
  profile_image?: string;
  avatar_url?: string;
  wallet_balance: number;
  member_since?: string;
  notification_preferences?: Record<string, boolean>;
  stats?: {
    total_orders: number;
    total_points: number;
    lifetime_points: number;
    deliveries_made: number;
  };
}

interface AuthContextType {
  isLoggedIn: boolean;
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string, phone?: string) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
  updateUser: (data: Partial<User>) => void;
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
      const token = getToken();
      if (token) {
        try {
          await fetch(`${API_BASE_URL}/cart/clear`, {
            method: "DELETE",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          });
        } catch {
          // Best-effort cart clear on logout
        }
      }
      await authAPI.logout();
    } catch {
      // Ignore errors on logout
    } finally {
      disconnectSocket();
      removeToken();
      setIsLoggedIn(false);
      setUser(null);
      window.dispatchEvent(new Event("auth:logout"));
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

  const updateUser = (data: Partial<User>) => {
    setUser((previous) => previous ? { ...previous, ...data } : previous);
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, user, isLoading, login, register, logout, updateProfile, updateUser }}>
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
