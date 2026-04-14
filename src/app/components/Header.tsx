import { Link, useLocation } from "react-router";
import { ShoppingCart, User, Award, Bike, Home, Clock, LogIn, Settings, LayoutDashboard } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import { useEffect, useState } from "react";
import { api } from "../services/api";
import { NotificationBell } from "./NotificationBell";
import { RunnerActiveDeliveryPanel } from "./RunnerActiveDeliveryPanel";
import { useRunnerState } from "../hooks/useRunnerState";
import { motion } from "motion/react";

export function Header() {
  const location = useLocation();
  const { isLoggedIn, user } = useAuth();
  const { getTotalItems } = useCart();
  const runner = useRunnerState();
  const [isTogglingRunner, setIsTogglingRunner] = useState(false);
  const [activeDelivery, setActiveDelivery] = useState<any | null>(null);
  const [showDeliveryPanel, setShowDeliveryPanel] = useState(false);

  useEffect(() => {
    if (!isLoggedIn) {
      return;
    }
  }, [isLoggedIn]);

  useEffect(() => {
    if (!isLoggedIn) {
      setActiveDelivery(null);
      return;
    }

    let isMounted = true;
    const checkActiveDelivery = async () => {
      try {
        const response = await api.getRunnerActiveDelivery();
        if (!isMounted) return;
        setActiveDelivery(response.active ? response : null);
        if (response.active && localStorage.getItem("runner-open-delivery")) {
          setShowDeliveryPanel(true);
        }
        if (!response.active) {
          localStorage.removeItem("runner-open-delivery");
        }
      } catch {
        if (isMounted) {
          setActiveDelivery(null);
        }
      }
    };

    checkActiveDelivery();
    const interval = window.setInterval(checkActiveDelivery, 10000);
    const handleActiveDeliveryChanged = () => {
      checkActiveDelivery();
    };
    window.addEventListener("runner:active-delivery-changed", handleActiveDeliveryChanged as EventListener);
    return () => {
      isMounted = false;
      window.clearInterval(interval);
      window.removeEventListener("runner:active-delivery-changed", handleActiveDeliveryChanged as EventListener);
    };
  }, [isLoggedIn]);
  
  const isActive = (path: string) => {
    return location.pathname === path;
  };

  // Hide header on login page
  if (location.pathname === '/login') {
    return null;
  }

  const cartItemCount = getTotalItems();
  const isAdmin = user && user.role === 'admin';

  const handleRunnerToggle = async () => {
    try {
      setIsTogglingRunner(true);
      if (!runner.isRunner) {
        await api.registerAsRunner({
          vehicle_type: "bike",
          license_number: `DL-${Date.now()}`,
        });
      }
      const nextAvailability = await runner.toggle();
      alert(
        nextAvailability
          ? "You are now available for deliveries"
          : "You are now unavailable"
      );
    } catch (error: any) {
      console.error("Error toggling runner mode:", error);
      alert(error.message || "Failed to toggle runner mode. Please try again.");
    } finally {
      setIsTogglingRunner(false);
    }
  };

  return (
    <motion.header 
      initial={{ y: -20, opacity: 0 }} 
      animate={{ y: 0, opacity: 1 }} 
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="bg-white/80 backdrop-blur-md shadow-sm sticky top-0 z-50 border-b border-gray-100"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-gradient-to-br from-orange-500 to-orange-600 text-white font-bold text-lg shadow-lg">
              🏃
            </div>
            <div>
              <h1 className="font-bold text-xl text-transparent bg-clip-text bg-gradient-to-r from-orange-600 to-orange-500">Campus Runner</h1>
              <p className="text-xs text-gray-500">Fast Food Delivery</p>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-6">
            <Link 
              to="/" 
              className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                isActive('/') ? 'bg-orange-50 text-orange-600' : 'text-gray-600 hover:text-orange-600'
              }`}
            >
              <Home className="w-5 h-5" />
              <span>Menu</span>
            </Link>
            {isLoggedIn && (
              <>
                <button
                  onClick={handleRunnerToggle}
                  disabled={isTogglingRunner}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                    runner.isAvailable
                      ? 'bg-orange-50 text-orange-600'
                      : 'text-gray-600 hover:text-orange-600'
                  } disabled:opacity-50`}
                  title={runner.isAvailable ? "Runner Mode Active" : "Click to Enable Runner Mode"}
                >
                  <Bike className="w-5 h-5" />
                  <span>Runner Mode</span>
                  {runner.isAvailable && (
                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  )}
                </button>
                {runner.isRunner && (
                  <Link
                    to="/runner"
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                      isActive('/runner') ? 'bg-orange-50 text-orange-600' : 'text-gray-600 hover:text-orange-600'
                    }`}
                  >
                    <LayoutDashboard className="w-5 h-5" />
                    <span>Runner Dashboard</span>
                  </Link>
                )}
                <Link 
                  to="/rewards" 
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                    isActive('/rewards') ? 'bg-orange-50 text-orange-600' : 'text-gray-600 hover:text-orange-600'
                  }`}
                >
                  <Award className="w-5 h-5" />
                  <span>Rewards</span>
                </Link>
                <Link 
                  to="/orders" 
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                    isActive('/orders') ? 'bg-orange-50 text-orange-600' : 'text-gray-600 hover:text-orange-600'
                  }`}
                >
                  <Clock className="w-5 h-5" />
                  <span>Orders</span>
                </Link>
                {activeDelivery && (
                  <button
                    type="button"
                    onClick={() => setShowDeliveryPanel(true)}
                    className="relative flex items-center gap-2 rounded-full bg-green-500 px-4 py-2 text-sm font-semibold text-white animate-pulse"
                  >
                    🛵 My Delivery
                    <span className="absolute -right-1 -top-1 h-3 w-3 rounded-full bg-orange-400" />
                  </button>
                )}
                {isAdmin && (
                  <Link 
                    to="/admin" 
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                      isActive('/admin') ? 'bg-orange-50 text-orange-600' : 'text-gray-600 hover:text-orange-600'
                    }`}
                    title="Admin Panel"
                  >
                    <Settings className="w-5 h-5" />
                    <span>Admin</span>
                  </Link>
                )}
              </>
            )}
          </nav>

          <div className="flex items-center gap-4">
            {isLoggedIn ? (
              <>
                <NotificationBell />
                <Link 
                  to="/cart" 
                  className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <ShoppingCart className="w-6 h-6 text-gray-700" />
                  {cartItemCount > 0 && (
                    <span className="absolute -top-1 -right-1 bg-orange-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                      {cartItemCount}
                    </span>
                  )}
                </Link>
                <Link 
                  to="/profile" 
                  className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <User className="w-6 h-6 text-gray-700" />
                </Link>
              </>
            ) : (
              <Link 
                to="/login" 
                className="flex items-center gap-2 bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <LogIn className="w-5 h-5" />
                <span className="hidden sm:inline">Login</span>
              </Link>
            )}
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden flex justify-around py-2 border-t">
          <Link 
            to="/" 
            className={`flex flex-col items-center gap-1 px-3 py-2 rounded-lg ${
              isActive('/') ? 'text-orange-600' : 'text-gray-600'
            }`}
          >
            <Home className="w-5 h-5" />
            <span className="text-xs">Menu</span>
          </Link>
          {isLoggedIn && (
            <>
              <button
                onClick={handleRunnerToggle}
                disabled={isTogglingRunner}
                className={`flex flex-col items-center gap-1 px-3 py-2 rounded-lg ${
                  runner.isAvailable ? 'text-orange-600' : 'text-gray-600'
                } disabled:opacity-50`}
              >
                <Bike className="w-5 h-5" />
                <span className="text-xs">Runner</span>
                {runner.isAvailable && (
                  <span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
                )}
              </button>
              {runner.isRunner && (
                <Link 
                  to="/runner" 
                  className={`flex flex-col items-center gap-1 px-3 py-2 rounded-lg ${
                    isActive('/runner') ? 'text-orange-600' : 'text-gray-600'
                  }`}
                >
                  <LayoutDashboard className="w-5 h-5" />
                  <span className="text-xs">Dashboard</span>
                </Link>
              )}
              <Link 
                to="/rewards" 
                className={`flex flex-col items-center gap-1 px-3 py-2 rounded-lg ${
                  isActive('/rewards') ? 'text-orange-600' : 'text-gray-600'
                }`}
              >
                <Award className="w-5 h-5" />
                <span className="text-xs">Rewards</span>
              </Link>
              <Link 
                to="/orders" 
                className={`flex flex-col items-center gap-1 px-3 py-2 rounded-lg ${
                  isActive('/orders') ? 'text-orange-600' : 'text-gray-600'
                }`}
              >
                <Clock className="w-5 h-5" />
                <span className="text-xs">Orders</span>
              </Link>
              {activeDelivery && (
                <button
                  type="button"
                  onClick={() => setShowDeliveryPanel(true)}
                  className="flex flex-col items-center gap-1 px-3 py-2 rounded-lg text-green-600"
                >
                  <span className="text-base animate-pulse">🛵</span>
                  <span className="text-xs">My Delivery</span>
                </button>
              )}
              {isAdmin && (
                <Link 
                  to="/admin" 
                  className={`flex flex-col items-center gap-1 px-3 py-2 rounded-lg ${
                    isActive('/admin') ? 'text-orange-600' : 'text-gray-600'
                  }`}
                >
                  <Settings className="w-5 h-5" />
                  <span className="text-xs">Admin</span>
                </Link>
              )}
            </>
          )}
        </div>
      </div>
      <RunnerActiveDeliveryPanel
        delivery={activeDelivery}
        open={showDeliveryPanel && Boolean(activeDelivery)}
        onClose={() => {
          setShowDeliveryPanel(false);
          if (activeDelivery?.delivery_status === 'delivered') {
            setActiveDelivery(null);
            localStorage.removeItem("runner-open-delivery");
          }
        }}
        onStatusUpdate={(nextDelivery) => {
          setActiveDelivery(nextDelivery);
          if (!nextDelivery) {
            setShowDeliveryPanel(false);
            localStorage.removeItem("runner-open-delivery");
          }
        }}
      />
    </motion.header>
  );
}
