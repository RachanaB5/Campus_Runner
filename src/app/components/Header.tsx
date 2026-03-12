import { Link, useLocation } from "react-router";
import { ShoppingCart, User, Award, Bike, Home, Clock, LogIn } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

export function Header() {
  const location = useLocation();
  const { isLoggedIn } = useAuth();
  const { getTotalItems } = useCart();
  
  const isActive = (path: string) => {
    return location.pathname === path;
  };

  // Hide header on login page
  if (location.pathname === '/login') {
    return null;
  }

  const cartItemCount = getTotalItems();

  return (
    <header className="bg-white shadow-sm sticky top-0 z-50">
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
            <Link 
              to="/runner" 
              className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                isActive('/runner') ? 'bg-orange-50 text-orange-600' : 'text-gray-600 hover:text-orange-600'
              }`}
            >
              <Bike className="w-5 h-5" />
              <span>Runner Mode</span>
            </Link>
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
          </nav>

          <div className="flex items-center gap-4">
            {isLoggedIn ? (
              <>
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
          <Link 
            to="/runner" 
            className={`flex flex-col items-center gap-1 px-3 py-2 rounded-lg ${
              isActive('/runner') ? 'text-orange-600' : 'text-gray-600'
            }`}
          >
            <Bike className="w-5 h-5" />
            <span className="text-xs">Runner</span>
          </Link>
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
        </div>
      </div>
    </header>
  );
}