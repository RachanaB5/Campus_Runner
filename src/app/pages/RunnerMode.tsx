import { useState, useEffect, useRef } from "react";
import { 
  Bike, MapPin, Clock, Award, CheckCircle, TrendingUp, Bell, Loader, 
  AlertCircle, PhoneCall, DollarSign, Navigation 
} from "lucide-react";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router";

interface Order {
  id: string;
  order_number: string;
  customer_name: string;
  customer_phone: string;
  delivery_address: string;
  total_amount: number;
  status: string;
  items: any[];
  received_by_canteen_at?: string;
  preparation_started_at?: string;
  ready_for_pickup_at?: string;
  picked_up_at?: string;
  in_transit_at?: string;
  delivered_at?: string;
}

interface ActiveDelivery {
  order: Order;
  currentStatus: 'picked_up' | 'in_transit' | 'awaiting_otp';
  otp?: string;
  showOtpInput?: boolean;
}

export function RunnerMode() {
  const { isLoggedIn, user } = useAuth();
  const navigate = useNavigate();
  const [availableOrders, setAvailableOrders] = useState<Order[]>([]);
  const [activeDeliveries, setActiveDeliveries] = useState<ActiveDelivery[]>([]);
  const [completedCount, setCompletedCount] = useState(0);
  const [totalEarnings, setTotalEarnings] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showNotification, setShowNotification] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState("");
  const [otpInput, setOtpInput] = useState<{ [key: string]: string }>({});
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  // Set up polling for new orders
  useEffect(() => {
    if (!isLoggedIn) {
      navigate("/login");
      return;
    }

    // Initial fetch
    fetchAvailableOrders();

    // Poll every 3 seconds for new orders
    pollingRef.current = setInterval(() => {
      fetchAvailableOrders();
    }, 3000);

    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [isLoggedIn, navigate]);

  const fetchAvailableOrders = async () => {
    try {
      const response = await api.getAvailableOrders();
      const newOrders = response.available_orders || [];
      
      // Check if there are new orders
      if (newOrders.length > availableOrders.length) {
        showNotificationMessage(`🆕 ${newOrders.length - availableOrders.length} new order(s) available!`);
        // Play notification sound (optional)
        const audio = new Audio('data:audio/wav;base64,UklGRiYAAABXQVZFZm10IBAAAAABAAEAQB8AAAB9AAACABAAZGF0YQIAAAAAAA==');
        audio.play().catch(() => {});
      }
      
      setAvailableOrders(newOrders);
      setError(null);
    } catch (err) {
      console.error("Error fetching available orders:", err);
      setError("Failed to load available orders");
    } finally {
      setIsLoading(false);
    }
  };

  const showNotificationMessage = (message: string) => {
    setNotificationMessage(message);
    setShowNotification(true);
    setTimeout(() => setShowNotification(false), 4000);
  };

  const pickupOrder = async (order: Order) => {
    try {
      const response = await api.pickupOrder(order.id);
      
      // Add to active deliveries
      const newDelivery: ActiveDelivery = {
        order,
        currentStatus: 'picked_up',
      };
      setActiveDeliveries([...activeDeliveries, newDelivery]);
      
      // Remove from available
      setAvailableOrders(availableOrders.filter(o => o.id !== order.id));
      
      showNotificationMessage(`✅ Order ${order.order_number} picked up!`);
    } catch (err) {
      console.error("Error picking up order:", err);
      alert("Failed to pick up order. Please try again.");
    }
  };

  const markInTransit = async (orderId: string) => {
    try {
      await api.markInTransit(orderId);
      
      // Update delivery status
      setActiveDeliveries(activeDeliveries.map(d => 
        d.order.id === orderId 
          ? { ...d, currentStatus: 'in_transit' }
          : d
      ));
      
      showNotificationMessage("🚴 Order is now in transit!");
    } catch (err) {
      console.error("Error marking in transit:", err);
      alert("Failed to update status. Please try again.");
    }
  };

  const startDelivery = async (orderId: string) => {
    try {
      const response = await api.deliverOrder(orderId);
      const otp = response.otp;
      
      // Update delivery status
      setActiveDeliveries(activeDeliveries.map(d => 
        d.order.id === orderId 
          ? { ...d, currentStatus: 'awaiting_otp', otp, showOtpInput: true }
          : d
      ));
      
      showNotificationMessage(`📧 OTP sent to customer! (Test OTP: ${otp})`);
    } catch (err) {
      console.error("Error starting delivery:", err);
      alert("Failed to generate OTP. Please try again.");
    }
  };

  const submitOtp = async (orderId: string) => {
    const enteredOtp = otpInput[orderId];
    
    if (!enteredOtp || enteredOtp.length !== 6) {
      alert("Please enter a valid 6-digit OTP");
      return;
    }

    try {
      await api.confirmDelivery(orderId, enteredOtp);
      
      // Remove from active deliveries
      const completedDelivery = activeDeliveries.find(d => d.order.id === orderId);
      setActiveDeliveries(activeDeliveries.filter(d => d.order.id !== orderId));
      
      // Update stats
      if (completedDelivery) {
        const earnings = Math.floor(completedDelivery.order.total_amount / 10);
        setCompletedCount(completedCount + 1);
        setTotalEarnings(totalEarnings + earnings);
      }
      
      // Clear OTP input
      setOtpInput({ ...otpInput, [orderId]: "" });
      
      showNotificationMessage("🎉 Delivery confirmed! Order complete!");
    } catch (err) {
      console.error("Error confirming delivery:", err);
      alert("Invalid OTP. Please try again.");
      setOtpInput({ ...otpInput, [orderId]: "" });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Notification Toast */}
      {showNotification && (
        <div className="fixed top-4 right-4 bg-orange-500 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-2 z-50 animate-bounce">
          <Bell className="w-5 h-5" />
          {notificationMessage}
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">🚴 Runner Dashboard</h1>
          <p className="text-gray-600">Real-time delivery management with live order tracking</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gradient-to-br from-orange-500 to-red-500 rounded-xl p-6 text-white shadow-lg">
            <div className="flex items-center justify-between mb-3">
              <Bike className="w-8 h-8 opacity-80" />
              <span className="text-4xl font-bold">{completedCount}</span>
            </div>
            <p className="text-orange-100 text-sm">Completed Today</p>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl p-6 text-white shadow-lg">
            <div className="flex items-center justify-between mb-3">
              <DollarSign className="w-8 h-8 opacity-80" />
              <span className="text-4xl font-bold">₹{totalEarnings}</span>
            </div>
            <p className="text-green-100 text-sm">Total Earnings</p>
          </div>

          <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl p-6 text-white shadow-lg">
            <div className="flex items-center justify-between mb-3">
              <TrendingUp className="w-8 h-8 opacity-80" />
              <span className="text-4xl font-bold">{activeDeliveries.length}</span>
            </div>
            <p className="text-blue-100 text-sm">Active Deliveries</p>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl p-6 text-white shadow-lg">
            <div className="flex items-center justify-between mb-3">
              <Bell className="w-8 h-8 opacity-80" />
              <span className="text-4xl font-bold">{availableOrders.length}</span>
            </div>
            <p className="text-purple-100 text-sm">Orders Ready</p>
          </div>
        </div>

        {/* Active Deliveries Section */}
        {activeDeliveries.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <Navigation className="w-6 h-6 text-orange-600" />
              <h2 className="text-2xl font-bold text-gray-900">My Active Deliveries ({activeDeliveries.length})</h2>
            </div>
            
            <div className="space-y-4">
              {activeDeliveries.map((delivery) => (
                <div key={delivery.order.id} className="bg-white rounded-xl shadow-lg border-l-4 border-orange-500 overflow-hidden">
                  {/* Order Header */}
                  <div className="p-6 border-b border-gray-200">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-xl font-bold text-gray-900">#{delivery.order.order_number}</h3>
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            delivery.currentStatus === 'picked_up' ? 'bg-blue-100 text-blue-700' :
                            delivery.currentStatus === 'in_transit' ? 'bg-orange-100 text-orange-700' :
                            'bg-red-100 text-red-700'
                          }`}>
                            {delivery.currentStatus === 'picked_up' ? '📦 Picked Up' :
                             delivery.currentStatus === 'in_transit' ? '🚴 In Transit' :
                             '🔐 Verify OTP'}
                          </span>
                        </div>
                        <p className="text-gray-600 font-semibold">{delivery.order.customer_name}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-3xl font-bold text-green-600">₹{delivery.order.total_amount}</p>
                        <p className="text-sm text-gray-500">{Math.floor(delivery.order.total_amount / 10)} units earn</p>
                      </div>
                    </div>
                  </div>

                  {/* Order Details */}
                  <div className="p-6 space-y-3 border-b border-gray-200 bg-gray-50">
                    <div className="flex items-center gap-3">
                      <PhoneCall className="w-5 h-5 text-blue-600" />
                      <span className="text-gray-700 font-mono">{delivery.order.customer_phone}</span>
                    </div>
                    <div className="flex items-start gap-3">
                      <MapPin className="w-5 h-5 text-red-600 mt-1" />
                      <div>
                        <p className="text-gray-700 font-semibold">Delivery Address</p>
                        <p className="text-gray-600">{delivery.order.delivery_address}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 mt-3 pt-3 border-t border-gray-200">
                      <Clock className="w-5 h-5 text-orange-600" />
                      <span className="text-sm text-gray-600">
                        Ready since: {delivery.order.ready_for_pickup_at ? 
                          new Date(delivery.order.ready_for_pickup_at).toLocaleTimeString() : 'N/A'}
                      </span>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="p-6 bg-white">
                    {delivery.currentStatus === 'picked_up' && (
                      <button
                        onClick={() => markInTransit(delivery.order.id)}
                        className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all"
                      >
                        <Navigation className="w-5 h-5" />
                        Mark as In Transit
                      </button>
                    )}

                    {delivery.currentStatus === 'in_transit' && (
                      <button
                        onClick={() => startDelivery(delivery.order.id)}
                        className="w-full bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-white py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all"
                      >
                        <MapPin className="w-5 h-5" />
                        I've Arrived - Generate OTP
                      </button>
                    )}

                    {delivery.currentStatus === 'awaiting_otp' && (
                      <div className="space-y-4">
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                          <p className="text-sm text-red-700 mb-3">
                            <strong>Test OTP (for demo):</strong> <span className="font-mono font-bold text-lg">{delivery.otp}</span>
                          </p>
                          <div className="space-y-2">
                            <label className="block">
                              <span className="text-sm font-semibold text-gray-700 mb-2 block">Enter 6-digit OTP from Customer:</span>
                              <input
                                type="text"
                                maxLength="6"
                                value={otpInput[delivery.order.id] || ''}
                                onChange={(e) => setOtpInput({
                                  ...otpInput,
                                  [delivery.order.id]: e.target.value.replace(/\D/g, '').slice(0, 6)
                                })}
                                placeholder="000000"
                                className="w-full px-4 py-2 text-center text-2xl letter-spacing-wide border-2 border-gray-300 rounded-lg font-mono font-bold focus:border-green-500 focus:outline-none"
                              />
                            </label>
                            <button
                              onClick={() => submitOtp(delivery.order.id)}
                              disabled={!otpInput[delivery.order.id] || otpInput[delivery.order.id].length !== 6}
                              className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 disabled:from-gray-300 disabled:to-gray-400 text-white py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all"
                            >
                              <CheckCircle className="w-5 h-5" />
                              Confirm Delivery
                            </button>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Available Orders Section */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Bell className="w-6 h-6 text-green-600 animate-bounce" />
              <h2 className="text-2xl font-bold text-gray-900">Available Orders ({availableOrders.length})</h2>
            </div>
            {isLoading && <Loader className="w-5 h-5 text-gray-400 animate-spin" />}
          </div>

          {isLoading && availableOrders.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-16 text-center">
              <Loader className="w-16 h-16 text-orange-400 mx-auto mb-4 animate-spin" />
              <p className="text-gray-600 text-lg font-semibold">Looking for new orders...</p>
              <p className="text-gray-400 text-sm mt-2">Checking every 3 seconds</p>
            </div>
          ) : availableOrders.length === 0 ? (
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl shadow-sm p-16 text-center border border-blue-200">
              <Bike className="w-20 h-20 text-blue-300 mx-auto mb-4" />
              <p className="text-gray-600 text-lg font-semibold">No orders available right now</p>
              <p className="text-gray-400 text-sm mt-2">Don't worry! New orders will appear here as soon as customers place them 📍</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {availableOrders.map((order) => (
                <div key={order.id} className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all transform hover:scale-105 overflow-hidden border-t-4 border-green-500">
                  {/* Order Card Header */}
                  <div className="p-5 bg-gradient-to-r from-green-50 to-emerald-50 border-b border-gray-100">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <p className="text-sm text-gray-500 font-semibold">Order #{order.order_number}</p>
                        <h3 className="text-lg font-bold text-gray-900">{order.customer_name}</h3>
                      </div>
                      <div className="text-right bg-green-500 text-white px-3 py-2 rounded-lg">
                        <p className="text-xl font-bold">₹{order.total_amount}</p>
                        <p className="text-xs">Earn {Math.floor(order.total_amount / 10)}</p>
                      </div>
                    </div>
                  </div>

                  {/* Order Details */}
                  <div className="p-5 space-y-3">
                    <div className="flex items-center gap-2">
                      <PhoneCall className="w-4 h-4 text-blue-600 flex-shrink-0" />
                      <a href={`tel:${order.customer_phone}`} className="text-blue-600 hover:underline font-mono text-sm">
                        {order.customer_phone}
                      </a>
                    </div>
                    <div className="flex items-start gap-2">
                      <MapPin className="w-4 h-4 text-red-600 flex-shrink-0 mt-1" />
                      <p className="text-sm text-gray-700 line-clamp-2">{order.delivery_address}</p>
                    </div>
                    {order.items && order.items.length > 0 && (
                      <div className="pt-2 border-t border-gray-200">
                        <p className="text-xs font-semibold text-gray-600 mb-1">Items ({order.items.length}):</p>
                        <ul className="text-xs text-gray-600 space-y-1">
                          {order.items.slice(0, 2).map((item: any, idx: number) => (
                            <li key={idx}>• {item.food_name || 'Item'} x{item.quantity || 1}</li>
                          ))}
                          {order.items.length > 2 && (
                            <li className="text-gray-500">... +{order.items.length - 2} more</li>
                          )}
                        </ul>
                      </div>
                    )}
                  </div>

                  {/* Pickup Button */}
                  <div className="p-5 bg-gray-50 border-t border-gray-100">
                    <button
                      onClick={() => pickupOrder(order)}
                      className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white py-3 rounded-lg font-bold flex items-center justify-center gap-2 transition-all shadow-md"
                    >
                      <TrendingUp className="w-5 h-5" />
                      Pick Up Order
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
