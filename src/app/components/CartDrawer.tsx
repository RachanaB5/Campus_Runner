import React, { useEffect, useRef } from 'react';
import { ShoppingCart, X, Plus, Minus, Trash2, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { useNavigate } from 'react-router';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';

interface CartDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CartDrawer({ isOpen, onClose }: CartDrawerProps) {
  const navigate = useNavigate();
  const { isLoggedIn } = useAuth();
  const {
    cart,
    removeFromCart,
    updateCartItem,
    isLoading: cartLoading,
    getTotalItems,
    getTotalPrice,
  } = useCart();
  
  const drawerRef = useRef<HTMLDivElement>(null);
  const cartCount = getTotalItems();
  const cartTotal = getTotalPrice();

  // Close drawer on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (drawerRef.current && !drawerRef.current.contains(e.target as Node)) {
        onClose();
      }
    }
    if (isOpen) document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [isOpen, onClose]);

  // Prevent body scroll when drawer is open
  useEffect(() => {
    document.body.style.overflow = isOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [isOpen]);

  const handleQuantityChange = async (itemId: string, newQty: number) => {
    if (newQty < 1) await removeFromCart(itemId);
    else await updateCartItem(itemId, newQty);
  };

  const handleCheckout = () => {
    onClose();
    navigate("/checkout");
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex justify-end">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Drawer */}
          <motion.div
            ref={drawerRef}
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="relative w-full max-w-md bg-white dark:bg-gray-900 h-full flex flex-col shadow-2xl"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b dark:border-gray-800 bg-orange-500 text-white">
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
                onClick={onClose}
                className="p-1 hover:bg-white/20 rounded-lg transition-colors"
                aria-label="Close cart"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Body */}
            <div className="flex-1 overflow-y-auto">
              {!isLoggedIn ? (
                <div className="flex flex-col items-center justify-center h-full px-6 text-center">
                  <ShoppingCart className="w-16 h-16 text-gray-200 dark:text-gray-700 mb-4" />
                  <p className="text-gray-700 dark:text-gray-300 font-semibold text-lg mb-2">Login to view your cart</p>
                  <p className="text-gray-400 text-sm mb-6">
                    Sign in with your RVU email to start ordering
                  </p>
                  <button
                    onClick={() => { onClose(); navigate("/login"); }}
                    className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-2.5 rounded-xl font-medium transition-colors"
                  >
                    Go to Login
                  </button>
                </div>
              ) : !cart || cart.items.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full px-6 text-center">
                  <span className="text-6xl mb-4">🛒</span>
                  <p className="text-gray-700 dark:text-gray-300 font-semibold text-lg mb-2">Your cart is empty</p>
                  <p className="text-gray-400 text-sm mb-6">
                    Add some delicious items from the menu!
                  </p>
                  <button
                    onClick={onClose}
                    className="border border-orange-500 text-orange-500 hover:bg-orange-50 dark:hover:bg-orange-500/10 px-6 py-2.5 rounded-xl font-medium transition-colors"
                  >
                    Browse Menu
                  </button>
                </div>
              ) : (
                <div className="divide-y dark:divide-gray-800">
                  {cart.items.map((item) => (
                    <motion.div 
                      key={item.id} 
                      layout
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex items-center gap-3 px-5 py-4"
                    >
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-gray-900 dark:text-gray-100 truncate">{item.food_name}</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">₹{item.price.toFixed(2)} each</p>
                      </div>
                      <div className="flex items-center gap-2 bg-gray-100 dark:bg-gray-800 rounded-lg px-2 py-1">
                        <button
                          onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                          disabled={cartLoading}
                          className="p-0.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded disabled:opacity-40 transition-colors"
                          aria-label="Decrease quantity"
                        >
                          <Minus className="w-3.5 h-3.5 text-gray-700 dark:text-gray-300" />
                        </button>
                        <span className="w-6 text-center text-sm font-bold text-gray-800 dark:text-gray-200">
                          {item.quantity}
                        </span>
                        <button
                          onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                          disabled={cartLoading}
                          className="p-0.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded disabled:opacity-40 transition-colors"
                          aria-label="Increase quantity"
                        >
                          <Plus className="w-3.5 h-3.5 text-gray-700 dark:text-gray-300" />
                        </button>
                      </div>
                      <div className="text-right min-w-[56px]">
                        <p className="font-bold text-gray-900 dark:text-gray-100 text-sm">₹{item.total.toFixed(2)}</p>
                      </div>
                      <button
                         onClick={() => removeFromCart(item.id)}
                         disabled={cartLoading}
                         className="p-1.5 text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 rounded-lg transition-colors disabled:opacity-40"
                         aria-label="Remove item"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            {isLoggedIn && cart && cart.items.length > 0 && (
              <div className="border-t dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 px-5 py-5 space-y-3">
                <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                  <span>Subtotal</span>
                  <span>₹{cartTotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                  <span>Delivery fee</span>
                  <span>₹10.00</span>
                </div>
                <div className="flex justify-between font-bold text-gray-900 dark:text-gray-100 text-base border-t dark:border-gray-700 pt-3">
                  <span>Total</span>
                  <span>₹{(cartTotal + 10).toFixed(2)}</span>
                </div>
                <button
                  onClick={handleCheckout}
                  className="w-full bg-orange-500 hover:bg-orange-600 text-white font-semibold py-3.5 rounded-xl flex items-center justify-center gap-2 transition-colors shadow-md shadow-orange-200 dark:shadow-none"
                >
                  Proceed to Checkout
                  <ArrowRight className="w-4 h-4" />
                </button>
                <button
                  onClick={() => { onClose(); navigate("/cart"); }}
                  className="w-full text-orange-500 hover:text-orange-600 text-sm font-medium py-1 transition-colors"
                >
                  View full cart →
                </button>
              </div>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
