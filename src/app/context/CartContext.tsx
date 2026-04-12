import { createContext, useContext, useState, ReactNode, useEffect } from "react";
import * as api from "../services/api";

export interface CartItem {
  id: string;
  cart_id: string;
  food_id: string;
  food_name?: string;
  quantity: number;
  price: number;
  total: number;
  customizations?: string;
  created_at: string;
  updated_at: string;
}

export interface Cart {
  id: string;
  user_id: string;
  total_price: number;
  item_count: number;
  items: CartItem[];
  created_at: string;
  updated_at: string;
}

interface CartContextType {
  cart: Cart | null;
  isLoading: boolean;
  addToCart: (foodId: string, quantity: number, customizations?: string) => Promise<void>;
  removeFromCart: (itemId: string) => Promise<void>;
  updateCartItem: (itemId: string, quantity: number, customizations?: string) => Promise<void>;
  clearCart: () => Promise<void>;
  getCart: () => Promise<void>;
  getTotalItems: () => number;
  getTotalPrice: () => number;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: ReactNode }) {
  const [cart, setCart] = useState<Cart | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Load cart on mount if user is authenticated
  useEffect(() => {
    const token = api.getToken();
    if (token) {
      getCart();
    }
  }, []);

  useEffect(() => {
    const handleLogout = () => {
      setCart(null);
      setIsLoading(false);
    };

    window.addEventListener("auth:logout", handleLogout);
    return () => window.removeEventListener("auth:logout", handleLogout);
  }, []);

  const getCart = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${api.API_BASE_URL}/cart`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${api.getToken()}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          api.removeToken();
          setCart(null);
          return;
        }
        throw new Error(`Failed to fetch cart: ${response.statusText}`);
      }

      const data = await response.json();
      setCart(data);
    } catch (error) {
      console.error("Error fetching cart:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const addToCart = async (foodId: string, quantity: number, customizations?: string) => {
    try {
      setIsLoading(true);
      const response = await fetch(`${api.API_BASE_URL}/cart/add`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${api.getToken()}`,
        },
        body: JSON.stringify({ food_id: foodId, quantity, customizations }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          api.removeToken();
          return;
        }
        throw new Error(`Failed to add to cart: ${response.statusText}`);
      }

      const data = await response.json();
      setCart(data.cart);
    } catch (error) {
      console.error("Error adding to cart:", error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const removeFromCart = async (itemId: string) => {
    try {
      setIsLoading(true);
      const response = await fetch(`${api.API_BASE_URL}/cart/item/${itemId}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${api.getToken()}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          api.removeToken();
          return;
        }
        throw new Error(`Failed to remove from cart: ${response.statusText}`);
      }

      const data = await response.json();
      setCart(data.cart);
    } catch (error) {
      console.error("Error removing from cart:", error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const updateCartItem = async (itemId: string, quantity: number, customizations?: string) => {
    try {
      setIsLoading(true);
      const response = await fetch(`${api.API_BASE_URL}/cart/item/${itemId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${api.getToken()}`,
        },
        body: JSON.stringify({ quantity, customizations }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          api.removeToken();
          return;
        }
        throw new Error(`Failed to update cart item: ${response.statusText}`);
      }

      const data = await response.json();
      setCart(data.cart);
    } catch (error) {
      console.error("Error updating cart item:", error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const clearCart = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${api.API_BASE_URL}/cart/clear`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${api.getToken()}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          api.removeToken();
          return;
        }
        throw new Error(`Failed to clear cart: ${response.statusText}`);
      }

      const data = await response.json();
      setCart(data.cart);
    } catch (error) {
      console.error("Error clearing cart:", error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const getTotalItems = () => {
    return cart?.item_count || 0;
  };

  const getTotalPrice = () => {
    return cart?.total_price || 0;
  };

  const value: CartContextType = {
    cart,
    isLoading,
    addToCart,
    removeFromCart,
    updateCartItem,
    clearCart,
    getCart,
    getTotalItems,
    getTotalPrice,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const context = useContext(CartContext);
  if (context === undefined) {
    throw new Error("useCart must be used within a CartProvider");
  }
  return context;
}
