import { useState, useEffect } from "react";
import { Search, ShoppingCart, X, Bike, MapPin } from "lucide-react";
import { menuItems } from "../data/mockData";
import { FoodCard } from "../components/FoodCard";
import { FoodDetailModal } from "../components/FoodDetailModal";
import { FoodCardSkeleton } from "../components/FoodCardSkeleton";
import { CartDrawer } from "../components/CartDrawer";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router";
import useSound from "use-sound";
import * as api from "../services/api";
import { motion } from "motion/react";

interface Food {
  id: string;
  name: string;
  description: string;
  price: number;
  category: string;
  image_url?: string;
  prep_time?: number;
  available: boolean;
  rating: number;
  review_count: number;
  is_veg?: boolean;
}

const CATEGORIES = [
  { label: "All", emoji: "🍽️" },
  { label: "Meals", emoji: "🍱" },
  { label: "North Indian", emoji: "🫓" },
  { label: "Combos", emoji: "🥘" },
  { label: "Biriyanis", emoji: "🍛" },
  { label: "Parathas", emoji: "🫓" },
  { label: "Pasta", emoji: "🍝" },
  { label: "Pizzas", emoji: "🍕" },
  { label: "Rolls", emoji: "🌯" },
  { label: "Burgers", emoji: "🍔" },
  { label: "Maggi", emoji: "🍜" },
  { label: "Ice Cream", emoji: "🍦" },
  { label: "Beverages", emoji: "🥤" },
];

const CATEGORY_NORMALIZATION: Record<string, string> = {
  "biryani": "Biriyanis",
  "biryanis": "Biriyanis",
  "pizza & bread": "Pizzas",
  "pizzas": "Pizzas",
  "cold drinks": "Beverages",
  "tea & coffee": "Beverages",
  "other drinks": "Beverages",
  "fresh juices": "Beverages",
  "soda": "Beverages",
  "lassi": "Beverages",
  "smooth drinks": "Beverages",
  "special shakes": "Beverages",
  "paper boat": "Beverages",
  "tropicana": "Beverages",
  "milk shakes": "Beverages",
};

const normalizeCategory = (category?: string) => {
  const normalized = (category || "").trim().toLowerCase();
  return CATEGORY_NORMALIZATION[normalized] || category || "Other";
};

const normalizeSearchText = (value: string) =>
  value.toLowerCase().replace(/[^a-z0-9\s]/g, " ").replace(/\s+/g, " ").trim();

export function Home() {
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [items, setItems] = useState(menuItems);
  const [isLoading, setIsLoading] = useState(true);
  const [cartOpen, setCartOpen] = useState(false);
  const [showDeliveries, setShowDeliveries] = useState(false);
  const [availableDeliveries, setAvailableDeliveries] = useState<any[]>([]);
  const [isLoadingDeliveries, setIsLoadingDeliveries] = useState(false);
  const [selectedFoodId, setSelectedFoodId] = useState<string | null>(null);
  const { getTotalItems } = useCart();
  const { isLoggedIn } = useAuth();
  const navigate = useNavigate();
  const [canRunDeliveries, setCanRunDeliveries] = useState(false);
  const [isRunnerOnline, setIsRunnerOnline] = useState(false);
  const [playPop] = useSound("/notification.mp3", { volume: 0.4 });

  useEffect(() => {
    fetchMenuItems();
  }, []);

  useEffect(() => {
    if (!isLoggedIn) {
      setCanRunDeliveries(false);
      setIsRunnerOnline(false);
      return;
    }

    api.getRunnerProfile()
      .then((runner) => {
        setCanRunDeliveries(Boolean(runner?.id));
        setIsRunnerOnline(Boolean(runner?.is_available));
      })
      .catch(() => {
        setCanRunDeliveries(false);
        setIsRunnerOnline(false);
      });
  }, [isLoggedIn]);

  useEffect(() => {
    const syncRunnerState = (event: Event) => {
      const detail = (event as CustomEvent<{ isOnline?: boolean; hasRunnerProfile?: boolean }>).detail || {};
      if (typeof detail.hasRunnerProfile === "boolean") {
        setCanRunDeliveries(detail.hasRunnerProfile);
      }
      if (typeof detail.isOnline === "boolean") {
        setIsRunnerOnline(detail.isOnline);
      }
    };

    const refreshRunnerProfile = async () => {
      if (!isLoggedIn) return;
      try {
        const runner = await api.getRunnerProfile();
        setCanRunDeliveries(Boolean(runner?.id));
        setIsRunnerOnline(Boolean(runner?.is_available));
      } catch {
        setCanRunDeliveries(false);
        setIsRunnerOnline(false);
      }
    };

    window.addEventListener("runner:status-changed", syncRunnerState as EventListener);
    window.addEventListener("focus", refreshRunnerProfile);
    document.addEventListener("visibilitychange", refreshRunnerProfile);
    return () => {
      window.removeEventListener("runner:status-changed", syncRunnerState as EventListener);
      window.removeEventListener("focus", refreshRunnerProfile);
      document.removeEventListener("visibilitychange", refreshRunnerProfile);
    };
  }, [isLoggedIn]);

  const fetchMenuItems = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${api.API_BASE_URL}/menu/all`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      if (response.ok) {
        const data = await response.json();
        const mappedItems = data.foods?.map((food: Food) => ({
          id: food.id,
          name: food.name,
          description: food.description,
          price: food.price,
          category: normalizeCategory(food.category),
          image: food.image_url || "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop",
          prepTime: food.prep_time ? `${food.prep_time} min` : "15 min",
          rating: food.rating || 4.5,
          isVeg: food.is_veg ?? true,
        })) || [];
        setItems(mappedItems.length > 0 ? mappedItems : menuItems);
      } else {
        setItems(menuItems);
      }
    } catch {
      setItems(menuItems);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredItems = items.filter((item) => {
    const matchesCategory = selectedCategory === "All" || item.category === selectedCategory;
    const normalizedQuery = normalizeSearchText(searchQuery);
    const haystack = normalizeSearchText(`${item.name} ${item.description} ${item.category}`);
    const matchesSearch = !normalizedQuery || haystack.includes(normalizedQuery);
    return matchesCategory && matchesSearch;
  });

  const cartCount = getTotalItems();
  const handleRunnerClick = async () => {
    if (!isLoggedIn) {
      navigate("/login");
      return;
    }
    if (!canRunDeliveries) {
      alert("Register as a runner first to accept deliveries.");
      navigate("/runner");
      return;
    }
    if (!isRunnerOnline) {
      alert("Please switch on Runner Mode before viewing available deliveries.");
      navigate("/runner");
      return;
    }
    
    setShowDeliveries(true);
    setIsLoadingDeliveries(true);
    try {
      const response = await api.getAvailableOrders();
      setAvailableDeliveries(response?.available_orders || response?.orders || []);
    } catch (error) {
      console.error("Error fetching deliveries:", error);
      setAvailableDeliveries([]);
    } finally {
      setIsLoadingDeliveries(false);
    }
  };

  const handleAcceptDelivery = async (orderId: string) => {
    try {
      const response = await api.acceptOrder(orderId);
      setAvailableDeliveries(availableDeliveries.filter((delivery) => (delivery.id || delivery.order_id) !== orderId));
      setShowDeliveries(false);
      navigate(`/runner/delivery/${response.delivery_id}`, {
        state: {
          order: response.order,
          order_id: orderId,
          delivery_id: response.delivery_id,
          pickup_otp: response.pickup_otp,
        },
      });
    } catch (error) {
      console.error("Error accepting delivery:", error);
      alert("Failed to accept delivery. Please try again.");
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* ── Hero Banner ─────────────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="relative rounded-2xl overflow-hidden mb-8 shadow-xl"
        style={{
          background: "linear-gradient(270deg, #ff6b35, #f7931e, #ffcd3c, #ff6b35)",
          backgroundSize: "400% 400%",
          animation: "gradientFlow 15s ease infinite",
        }}
      >
        <div className="relative z-10 p-8 text-white">
          <div className="max-w-lg">
            <p className="text-sm font-semibold uppercase tracking-widest opacity-80 mb-2">
              RV University Canteen
            </p>
            <h2 className="text-3xl md:text-4xl font-bold mb-3 leading-tight drop-shadow-sm">
              Order Fresh, Earn Points 🎉
            </h2>
            <p className="text-base opacity-90 mb-6 drop-shadow-sm">
              From Biryani to Maggi — everything you love, delivered on campus
            </p>
            <div className="flex flex-wrap gap-3">
              {["⚡ 10 min pickup", "🌿 Fresh daily", "🏆 Earn rewards"].map((t) => (
                <span
                  key={t}
                  className="bg-white/20 backdrop-blur-md rounded-full px-4 py-1.5 text-sm font-medium border border-white/30 shadow-sm"
                >
                  {t}
                </span>
              ))}
            </div>
          </div>
        </div>
        {/* decorative circles */}
        <div className="absolute -right-10 -top-10 w-56 h-56 rounded-full bg-white/10 blur-xl" />
        <div className="absolute -right-4 bottom-0 w-32 h-32 rounded-full bg-white/10 blur-xl" />
      </motion.div>

      {/* ── Search + Cart Button Row ─────────────────────────────── */}
      <div className="flex gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search food items..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent bg-white shadow-sm"
          />
        </div>
        <button
          onClick={handleRunnerClick}
          disabled={!isLoggedIn || !canRunDeliveries || !isRunnerOnline}
          className="flex items-center gap-2 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed text-white px-5 py-3 rounded-xl shadow-sm transition-colors font-medium"
          title="View available deliveries"
        >
          <Bike className="w-5 h-5" />
          <span className="hidden sm:inline">Deliveries</span>
        </button>
        <button
          onClick={() => setCartOpen(true)}
          className="relative flex items-center gap-2 bg-orange-500 hover:bg-orange-600 text-white px-5 py-3 rounded-xl shadow-sm transition-colors font-medium"
        >
          <ShoppingCart className="w-5 h-5" />
          <span className="hidden sm:inline">Cart</span>
          {cartCount > 0 && (
            <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold shadow">
              {cartCount}
            </span>
          )}
        </button>
      </div>

      {/* ── Category Chips ───────────────────────────────────────── */}
      <div className="mb-8 overflow-x-auto scrollbar-hide py-1">
        <div className="flex gap-2 pb-2">
          {CATEGORIES.map(({ label, emoji }) => (
            <motion.button
              whileTap={{ scale: 0.95 }}
              key={label}
              onClick={() => setSelectedCategory(label)}
              className={`px-4 py-2 rounded-full whitespace-nowrap text-sm font-medium transition-colors flex items-center gap-1.5 ${
                selectedCategory === label
                  ? "bg-orange-500 text-white shadow-md shadow-orange-200"
                  : "bg-white text-gray-700 hover:bg-orange-50 hover:text-orange-600 border border-gray-100 shadow-sm"
              }`}
            >
              <span>{emoji}</span>
              {label}
            </motion.button>
          ))}
        </div>
      </div>

      {/* ── Food Grid ────────────────────────────────────────────── */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {Array.from({ length: 8 }).map((_, i) => (
            <FoodCardSkeleton key={i} />
          ))}
        </div>
      ) : (
        <>
          {selectedCategory !== "All" && (
            <div className="mb-4 flex items-center gap-2">
              <h2 className="text-xl font-bold text-gray-800">
                {CATEGORIES.find((c) => c.label === selectedCategory)?.emoji}{" "}
                {selectedCategory}
              </h2>
              <span className="text-sm text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
                {filteredItems.length} items
              </span>
            </div>
          )}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ staggerChildren: 0.05 }}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
          >
            {filteredItems.map((item) => (
              <motion.div key={item.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                <FoodCard 
                  item={item} 
                  onAddSuccess={() => {
                    playPop();
                    setCartOpen(true);
                  }} 
                  onOpenDetail={(id) => setSelectedFoodId(String(id))} 
                />
              </motion.div>
            ))}
          </motion.div>
          {filteredItems.length === 0 && (
            <div className="text-center py-20">
              <p className="text-5xl mb-4">🔍</p>
              <p className="text-gray-500 text-lg font-medium">No items found</p>
              <p className="text-gray-400 text-sm mt-1">
                Try a different search or category
              </p>
            </div>
          )}
        </>
      )}
      <FoodDetailModal foodId={selectedFoodId} open={Boolean(selectedFoodId)} onClose={() => setSelectedFoodId(null)} />

      {/* ── Cart Drawer Overlay ──────────────────────────────────── */}
      <CartDrawer isOpen={cartOpen} onClose={() => setCartOpen(false)} />

      {/* ── Deliveries Modal ────────────────────────────────────── */}
      {showDeliveries && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* backdrop */}
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setShowDeliveries(false)} />

          {/* modal */}
          <div className="relative bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden flex flex-col">
            {/* header */}
            <div className="flex items-center justify-between px-6 py-4 border-b bg-blue-500 text-white">
              <div className="flex items-center gap-3">
                <Bike className="w-5 h-5" />
                <h2 className="text-lg font-bold">Available Deliveries</h2>
              </div>
              <button
                onClick={() => setShowDeliveries(false)}
                className="p-1 hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* body */}
            <div className="flex-1 overflow-y-auto p-6">
              {isLoadingDeliveries ? (
                <div className="flex flex-col items-center justify-center h-full">
                  <Bike className="w-16 h-16 text-gray-300 mb-4 animate-bounce" />
                  <p className="text-gray-600">Loading deliveries...</p>
                </div>
              ) : availableDeliveries.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <Bike className="w-16 h-16 text-gray-300 mb-4" />
                  <p className="text-gray-600 font-semibold">No deliveries available</p>
                  <p className="text-gray-400 text-sm mt-2">Check back later for new orders to deliver</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {availableDeliveries.map((delivery) => (
                    <div key={delivery.id || delivery.order_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="font-semibold text-gray-900">
                            Order #{delivery.token_number || delivery.order_number || delivery.order_id}
                          </h3>
                          <p className="text-sm text-gray-600 mt-1">
                            ₹{Number(delivery.total_amount || 0).toFixed(2)}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            {(delivery.item_count || 0)} item{delivery.item_count === 1 ? "" : "s"}
                            {delivery.customer_name ? ` • ${delivery.customer_name}` : ""}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-green-600 font-semibold">
                            +{delivery.reward_points || Math.max(10, Math.round(Number(delivery.total_amount || 0) * 0.1))} pts
                          </p>
                        </div>
                      </div>

                      {(delivery.items_preview || delivery.items_summary)?.length > 0 && (
                        <p className="text-sm text-gray-500 mb-2">
                          {(delivery.items_preview || delivery.items_summary).join(", ")}
                          {delivery.item_count > 2 ? ` +${delivery.item_count - 2} more` : ""}
                        </p>
                      )}

                      {delivery.delivery_address && (
                        <div className="flex items-center gap-2 text-gray-600 mb-2">
                          <MapPin className="w-4 h-4" />
                          <span className="text-sm">{delivery.delivery_address}</span>
                        </div>
                      )}

                      {delivery.customer_phone && (
                        <div className="flex items-center gap-2 text-gray-600 mb-3">
                          <span className="text-sm">Phone: {delivery.customer_phone}</span>
                        </div>
                      )}

                      <button
                        onClick={() => handleAcceptDelivery(delivery.id || delivery.order_id)}
                        className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                      >
                        <Bike className="w-4 h-4" />
                        Accept Delivery
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      <style>{`
        @keyframes slideInRight {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
        @keyframes gradientFlow {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        .scrollbar-hide::-webkit-scrollbar { display: none; }
        .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
      `}</style>
    </div>
  );
}
