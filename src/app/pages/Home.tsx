import { useState, useEffect, useRef } from "react";
import { Search, ShoppingCart, X, Plus, Minus, Trash2, ArrowRight, Leaf, Bike, MapPin, Clock } from "lucide-react";
import { menuItems } from "../data/mockData";
import { FoodCard } from "../components/FoodCard";
import { FoodDetailModal } from "../components/FoodDetailModal";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router";
import * as api from "../services/api";

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
  const drawerRef = useRef<HTMLDivElement>(null);

  const {
    cart,
    addToCart,
    removeFromCart,
    updateCartItem,
    isLoading: cartLoading,
    getTotalItems,
    getTotalPrice,
  } = useCart();
  const { isLoggedIn } = useAuth();
  const navigate = useNavigate();

  // Close drawer on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (drawerRef.current && !drawerRef.current.contains(e.target as Node)) {
        setCartOpen(false);
      }
    }
    if (cartOpen) document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [cartOpen]);

  // Prevent body scroll when drawer is open
  useEffect(() => {
    document.body.style.overflow = cartOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [cartOpen]);

  useEffect(() => {
    fetchMenuItems();
  }, []);

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
  const cartTotal = getTotalPrice();

  const handleQuantityChange = async (itemId: string, newQty: number) => {
    if (newQty < 1) await removeFromCart(itemId);
    else await updateCartItem(itemId, newQty);
  };

  const handleCheckout = () => {
    setCartOpen(false);
    navigate("/checkout");
  };

  const handleRunnerClick = async () => {
    if (!isLoggedIn) {
      navigate("/login");
      return;
    }
    
    setShowDeliveries(true);
    setIsLoadingDeliveries(true);
    try {
      const response = await api.getAvailableDeliveries();
      setAvailableDeliveries(response?.deliveries || []);
    } catch (error) {
      console.error("Error fetching deliveries:", error);
      setAvailableDeliveries([]);
    } finally {
      setIsLoadingDeliveries(false);
    }
  };

  const handleAcceptDelivery = async (deliveryId: string) => {
    try {
      await api.acceptDelivery(deliveryId);
      setAvailableDeliveries(availableDeliveries.filter(d => d.id !== deliveryId));
      alert("Delivery accepted! Head to the restaurant.");
    } catch (error) {
      console.error("Error accepting delivery:", error);
      alert("Failed to accept delivery. Please try again.");
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* ── Hero Banner ─────────────────────────────────────────── */}
      <div
        className="relative rounded-2xl overflow-hidden mb-8"
        style={{
          background: "linear-gradient(135deg, #ff6b35 0%, #f7931e 50%, #ffcd3c 100%)",
        }}
      >
        <div className="relative z-10 p-8 text-white">
          <div className="max-w-lg">
            <p className="text-sm font-semibold uppercase tracking-widest opacity-80 mb-2">
              RV University Canteen
            </p>
            <h2 className="text-3xl md:text-4xl font-bold mb-3 leading-tight">
              Order Fresh, Earn Points 🎉
            </h2>
            <p className="text-base opacity-90 mb-6">
              From Biryani to Maggi — everything you love, delivered on campus
            </p>
            <div className="flex flex-wrap gap-3">
              {["⚡ 10 min pickup", "🌿 Fresh daily", "🏆 Earn rewards"].map((t) => (
                <span
                  key={t}
                  className="bg-white/20 backdrop-blur-sm rounded-full px-4 py-1.5 text-sm font-medium"
                >
                  {t}
                </span>
              ))}
            </div>
          </div>
        </div>
        {/* decorative circles */}
        <div className="absolute -right-10 -top-10 w-56 h-56 rounded-full bg-white/10" />
        <div className="absolute -right-4 bottom-0 w-32 h-32 rounded-full bg-white/10" />
      </div>

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
          className="flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-5 py-3 rounded-xl shadow-sm transition-colors font-medium"
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
      <div className="mb-8 overflow-x-auto scrollbar-hide">
        <div className="flex gap-2 pb-2">
          {CATEGORIES.map(({ label, emoji }) => (
            <button
              key={label}
              onClick={() => setSelectedCategory(label)}
              className={`px-4 py-2 rounded-full whitespace-nowrap text-sm font-medium transition-all flex items-center gap-1.5 ${
                selectedCategory === label
                  ? "bg-orange-500 text-white shadow-md shadow-orange-200"
                  : "bg-white text-gray-700 hover:bg-orange-50 hover:text-orange-600 border border-gray-200"
              }`}
            >
              <span>{emoji}</span>
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* ── Food Grid ────────────────────────────────────────────── */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl overflow-hidden shadow-sm animate-pulse">
              <div className="h-48 bg-gray-200" />
              <div className="p-4 space-y-2">
                <div className="h-4 bg-gray-200 rounded w-3/4" />
                <div className="h-3 bg-gray-200 rounded w-full" />
                <div className="h-3 bg-gray-200 rounded w-2/3" />
              </div>
            </div>
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
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredItems.map((item) => (
              <FoodCard key={item.id} item={item} onAddSuccess={() => setCartOpen(true)} onOpenDetail={(id) => setSelectedFoodId(String(id))} />
            ))}
          </div>
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
      {cartOpen && (
        <div className="fixed inset-0 z-50 flex">
          {/* backdrop */}
          <div className="flex-1 bg-black/40 backdrop-blur-sm" onClick={() => setCartOpen(false)} />

          {/* drawer */}
          <div
            ref={drawerRef}
            className="w-full max-w-md bg-white h-full flex flex-col shadow-2xl"
            style={{ animation: "slideInRight 0.25s ease-out" }}
          >
            {/* header */}
            <div className="flex items-center justify-between px-6 py-4 border-b bg-orange-500 text-white">
              <div className="flex items-center gap-3">
                <ShoppingCart className="w-5 h-5" />
                <h2 className="text-lg font-bold">Your Cart</h2>
                {cartCount > 0 && (
                  <span className="bg-white text-orange-500 text-xs font-bold rounded-full px-2 py-0.5">
                    {cartCount}
                  </span>
                )}
              </div>
              <button
                onClick={() => setCartOpen(false)}
                className="p-1 hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* body */}
            <div className="flex-1 overflow-y-auto">
              {!isLoggedIn ? (
                <div className="flex flex-col items-center justify-center h-full px-6 text-center">
                  <ShoppingCart className="w-16 h-16 text-gray-200 mb-4" />
                  <p className="text-gray-700 font-semibold text-lg mb-2">Login to view your cart</p>
                  <p className="text-gray-400 text-sm mb-6">
                    Sign in with your RVU email to start ordering
                  </p>
                  <button
                    onClick={() => { setCartOpen(false); navigate("/login"); }}
                    className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-2.5 rounded-xl font-medium transition-colors"
                  >
                    Go to Login
                  </button>
                </div>
              ) : !cart || cart.items.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full px-6 text-center">
                  <span className="text-6xl mb-4">🛒</span>
                  <p className="text-gray-700 font-semibold text-lg mb-2">Your cart is empty</p>
                  <p className="text-gray-400 text-sm mb-6">
                    Add some delicious items from the menu!
                  </p>
                  <button
                    onClick={() => setCartOpen(false)}
                    className="border border-orange-500 text-orange-500 hover:bg-orange-50 px-6 py-2.5 rounded-xl font-medium transition-colors"
                  >
                    Browse Menu
                  </button>
                </div>
              ) : (
                <div className="divide-y">
                  {cart.items.map((item) => (
                    <div key={item.id} className="flex items-center gap-3 px-5 py-4">
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-gray-900 truncate">{item.food_name}</p>
                        <p className="text-sm text-gray-500 mt-0.5">₹{item.price.toFixed(0)} each</p>
                      </div>
                      <div className="flex items-center gap-2 bg-gray-100 rounded-lg px-2 py-1">
                        <button
                          onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                          disabled={cartLoading}
                          className="p-0.5 hover:bg-gray-200 rounded disabled:opacity-40 transition-colors"
                        >
                          <Minus className="w-3.5 h-3.5 text-gray-700" />
                        </button>
                        <span className="w-6 text-center text-sm font-bold text-gray-800">
                          {item.quantity}
                        </span>
                        <button
                          onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                          disabled={cartLoading}
                          className="p-0.5 hover:bg-gray-200 rounded disabled:opacity-40 transition-colors"
                        >
                          <Plus className="w-3.5 h-3.5 text-gray-700" />
                        </button>
                      </div>
                      <div className="text-right min-w-[56px]">
                        <p className="font-bold text-gray-900 text-sm">₹{item.total.toFixed(0)}</p>
                      </div>
                      <button
                        onClick={() => removeFromCart(item.id)}
                        disabled={cartLoading}
                        className="p-1.5 text-red-400 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-40"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* footer — only show if logged in and cart has items */}
            {isLoggedIn && cart && cart.items.length > 0 && (
              <div className="border-t bg-gray-50 px-5 py-5 space-y-3">
                <div className="flex justify-between text-sm text-gray-600">
                  <span>Subtotal</span>
                  <span>₹{cartTotal.toFixed(0)}</span>
                </div>
                <div className="flex justify-between text-sm text-gray-600">
                  <span>Delivery fee</span>
                  <span>₹10</span>
                </div>
                <div className="flex justify-between font-bold text-gray-900 text-base border-t pt-3">
                  <span>Total</span>
                  <span>₹{(cartTotal + 10).toFixed(0)}</span>
                </div>
                <button
                  onClick={handleCheckout}
                  className="w-full bg-orange-500 hover:bg-orange-600 text-white font-semibold py-3.5 rounded-xl flex items-center justify-center gap-2 transition-colors shadow-md shadow-orange-200"
                >
                  Proceed to Checkout
                  <ArrowRight className="w-4 h-4" />
                </button>
                <button
                  onClick={() => { setCartOpen(false); navigate("/cart"); }}
                  className="w-full text-orange-500 hover:text-orange-600 text-sm font-medium py-1 transition-colors"
                >
                  View full cart →
                </button>
              </div>
            )}
          </div>
        </div>
      )}

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
                    <div key={delivery.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="font-semibold text-gray-900">Order #{delivery.order_id}</h3>
                          <p className="text-sm text-gray-600 mt-1">₹{delivery.total_amount?.toFixed(2) || "N/A"}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-green-600 font-semibold">+{Math.floor((delivery.total_amount || 0) / 10)} pts</p>
                        </div>
                      </div>

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
                        onClick={() => handleAcceptDelivery(delivery.id)}
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
        .scrollbar-hide::-webkit-scrollbar { display: none; }
        .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
      `}</style>
    </div>
  );
}
