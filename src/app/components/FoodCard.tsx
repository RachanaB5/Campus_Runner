import { Star, Clock, Leaf, Plus, Check } from "lucide-react";
import { MenuItem } from "../data/mockData";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { useState } from "react";
import { useNavigate } from "react-router";
import { getFoodImageUrl } from "../utils/foodImages";
import { motion } from "motion/react";

interface FoodCardProps {
  item: MenuItem;
  onAddSuccess?: () => void;  // callback to open cart drawer
  onOpenDetail?: (id: string | number) => void;
}

const scaleVariants = {
  hover: { y: -5, scale: 1.02, transition: { duration: 0.2, ease: "easeOut" } },
  tap: { scale: 0.98 }
};

export function FoodCard({ item, onAddSuccess, onOpenDetail }: FoodCardProps) {
  const { addToCart, isLoading } = useCart();
  const { isLoggedIn } = useAuth();
  const navigate = useNavigate();
  const [isAdding, setIsAdding] = useState(false);
  const [added, setAdded] = useState(false);

  const handleAdd = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isLoggedIn) {
      navigate("/login");
      return;
    }

    try {
      setIsAdding(true);
      await addToCart(String(item.id), 1);
      setAdded(true);
      onAddSuccess?.();            // open the cart drawer
      setTimeout(() => setAdded(false), 2000);
    } catch {
      // silent fail — toast could be added
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <motion.div
      variants={scaleVariants}
      whileHover="hover"
      whileTap="tap"
      className="bg-white/90 backdrop-blur-sm rounded-xl shadow-sm hover:shadow-xl transition-shadow duration-300 overflow-hidden group flex flex-col cursor-pointer border border-gray-100"
      onClick={() => onOpenDetail?.(item.id)}
    >
      {/* Image */}
      <div className="relative overflow-hidden h-44 flex-shrink-0">
        <ImageWithFallback
          src={getFoodImageUrl(item.image, item.category)}
          alt={item.name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        />

        {/* Veg badge */}
        <div className={`absolute top-2.5 left-2.5 rounded-full p-1.5 shadow-md ${item.isVeg ? "bg-green-500" : "bg-red-500"}`}>
          {item.isVeg
            ? <Leaf className="w-3 h-3 text-white" />
            : <span className="text-white text-[10px] font-bold leading-none">N</span>
          }
        </div>

        {/* Rating badge */}
        <div className="absolute top-2.5 right-2.5 bg-white/90 backdrop-blur-md rounded-full px-2 py-1 shadow-md flex items-center gap-1">
          <Star className="w-3 h-3 text-yellow-500 fill-yellow-500" />
          <span className="text-xs font-semibold text-gray-800">{item.rating}</span>
        </div>
      </div>

      {/* Body */}
      <div className="p-4 flex flex-col flex-1">
        <h3 className="font-bold text-gray-900 mb-1 leading-tight line-clamp-1">{item.name}</h3>
        <p className="text-xs text-gray-500 mb-3 line-clamp-2 flex-1">{item.description}</p>

        <div className="flex items-center gap-1.5 text-xs text-gray-400 mb-4">
          <Clock className="w-3.5 h-3.5" />
          <span>{item.prepTime}</span>
        </div>

        {/* Price + Add */}
        <div className="flex items-center justify-between">
          <div>
            <span className="text-xl font-bold text-gray-900">₹{item.price}</span>
          </div>

          <motion.button
            whileTap={{ scale: 0.9 }}
            onClick={handleAdd}
            disabled={isAdding || isLoading}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold transition-colors duration-200 shadow-sm
              ${added
                ? "bg-green-500 text-white shadow-green-200"
                : "bg-orange-500 hover:bg-orange-600 text-white shadow-orange-200 hover:shadow-md disabled:bg-gray-300"
              }`}
          >
            {isAdding ? (
              <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
            ) : added ? (
              <Check className="w-4 h-4" />
            ) : (
              <Plus className="w-4 h-4" />
            )}
            {isAdding ? "Adding…" : added ? "Added!" : "Add"}
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
}
