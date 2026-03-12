import { Plus } from "lucide-react";
import { useState } from "react";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";

interface AddToCartButtonProps {
  foodId: string | number;
  quantity?: number;
  className?: string;
  variant?: "default" | "small";
}

export function AddToCartButton({ 
  foodId, 
  quantity = 1, 
  className = "",
  variant = "default" 
}: AddToCartButtonProps) {
  const { addToCart, isLoading } = useCart();
  const { isLoggedIn } = useAuth();
  const [isAdding, setIsAdding] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  const handleAddToCart = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isLoggedIn) {
      setMessage({ type: 'error', text: 'Please login to add items to cart' });
      setTimeout(() => setMessage(null), 3000);
      return;
    }

    try {
      setIsAdding(true);
      await addToCart(String(foodId), quantity);
      setMessage({ type: 'success', text: 'Added to cart!' });
      setTimeout(() => setMessage(null), 2000);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to add to cart' });
      setTimeout(() => setMessage(null), 3000);
    } finally {
      setIsAdding(false);
    }
  };

  if (variant === "small") {
    return (
      <div className="relative">
        <button
          onClick={handleAddToCart}
          disabled={isAdding || isLoading}
          className={`bg-orange-500 hover:bg-orange-600 disabled:bg-gray-400 text-white rounded px-2 py-1 text-xs flex items-center gap-1 transition-colors ${className}`}
        >
          <Plus className="w-3 h-3" />
          {isAdding ? "Adding..." : "Add"}
        </button>
        {message && (
          <div className={`absolute top-full mt-2 right-0 px-3 py-2 rounded whitespace-nowrap text-sm ${
            message.type === 'success' 
              ? 'bg-green-500 text-white' 
              : 'bg-red-500 text-white'
          }`}>
            {message.text}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={handleAddToCart}
        disabled={isAdding || isLoading}
        className={`bg-orange-500 hover:bg-orange-600 disabled:bg-gray-400 text-white rounded-lg px-4 py-2 flex items-center gap-2 transition-colors ${className}`}
      >
        <Plus className="w-4 h-4" />
        <span>{isAdding ? "Adding..." : "Add"}</span>
      </button>
      {message && (
        <div className={`absolute top-full mt-2 right-0 px-4 py-2 rounded whitespace-nowrap text-sm ${
          message.type === 'success' 
            ? 'bg-green-500 text-white' 
            : 'bg-red-500 text-white'
        }`}>
          {message.text}
        </div>
      )}
    </div>
  );
}
