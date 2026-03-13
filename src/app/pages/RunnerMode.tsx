import { useState, useEffect } from "react";
import { Bike, MapPin, Clock, Award, CheckCircle, TrendingUp } from "lucide-react";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router";

interface Delivery {
  id: string;
  order_id: string;
  status: string;
  estimated_time?: string;
  delivery_address?: string;
  customer_phone?: string;
  total_amount?: number;
}

export function RunnerMode() {
  const { isLoggedIn } = useAuth();
  const navigate = useNavigate();
  const [availableDeliveries, setAvailableDeliveries] = useState<Delivery[]>([]);
  const [activeDeliveries, setActiveDeliveries] = useState<Delivery[]>([]);
  const [completedToday, setCompletedToday] = useState(0);
  const [totalPoints, setTotalPoints] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [totalDeliveries, setTotalDeliveries] = useState(0);

  useEffect(() => {
    if (!isLoggedIn) {
      navigate("/login");
      return;
    }
    fetchDeliveries();
  }, [isLoggedIn, navigate]);

  const fetchDeliveries = async () => {
    try {
      setIsLoading(true);
      const [availableRes, myRes, profileRes] = await Promise.all([
        api.getAvailableDeliveries().catch(() => ({ deliveries: [] })),
        api.getMyDeliveries().catch(() => ({ deliveries: [] })),
        api.getRunnerProfile().catch(() => null),
      ]);

      const available = availableRes?.deliveries || [];
      const active = myRes?.deliveries?.filter((d: any) => d.status !== 'completed') || [];
      const completed = myRes?.deliveries?.filter((d: any) => d.status === 'completed') || [];

      setAvailableDeliveries(available);
      setActiveDeliveries(active);
      setTotalDeliveries(completed.length);
      
      // Calculate points: 10% of each completed order value
      const completedPoints = completed.reduce((sum: number, d: any) => sum + Math.floor((d.total_amount || 0) / 10), 0);
      
      // First delivery gets 50 bonus points
      const bonusPoints = completed.length > 0 ? 50 : 0;
      const calculatedPoints = completedPoints + bonusPoints;
      
      setTotalPoints(calculatedPoints);

      if (profileRes) {
        setCompletedToday(profileRes.deliveries_today || 0);
      }
    } catch (error) {
      console.error("Error fetching deliveries:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const acceptDelivery = async (deliveryId: string) => {
    try {
      await api.acceptDelivery(deliveryId);
      const delivery = availableDeliveries.find(d => d.id === deliveryId);
      if (delivery) {
        setActiveDeliveries([...activeDeliveries, delivery]);
        setAvailableDeliveries(availableDeliveries.filter(d => d.id !== deliveryId));
        alert("Delivery accepted! Head to the restaurant.");
      }
    } catch (error) {
      console.error("Error accepting delivery:", error);
      alert("Failed to accept delivery. Please try again.");
    }
  };

  const completeDelivery = async (deliveryId: string, earnedPoints: number) => {
    try {
      await api.updateDeliveryStatus(deliveryId, 'completed');

      setActiveDeliveries(activeDeliveries.filter(d => d.id !== deliveryId));
      setCompletedToday(completedToday + 1);
      setTotalDeliveries(totalDeliveries + 1);
      setTotalPoints(totalPoints + earnedPoints);
      alert(`Delivery completed! You earned ${earnedPoints} points.`);
    } catch (error) {
      console.error("Error completing delivery:", error);
      alert("Failed to complete delivery. Please try again.");
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl text-gray-900 mb-2">Runner Mode</h1>
        <p className="text-gray-600">Deliver orders and earn reward points!</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-gradient-to-br from-orange-500 to-red-500 rounded-xl p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <Bike className="w-8 h-8" />
            <span className="text-3xl">{completedToday}</span>
          </div>
          <p className="text-orange-100">Deliveries Today</p>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <Award className="w-8 h-8" />
            <span className="text-3xl">{totalPoints}</span>
          </div>
          <p className="text-green-100">Total Points</p>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl p-6 text-white">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="w-8 h-8" />
            <span className="text-3xl">{activeDeliveries.length}</span>
          </div>
          <p className="text-blue-100">Active Deliveries</p>
        </div>
      </div>

      {/* How it Works */}
      <div className="bg-orange-50 border border-orange-200 rounded-xl p-6 mb-8">
        <h3 className="text-lg text-gray-900 mb-3">How Runner Mode Works</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex gap-3">
            <div className="w-8 h-8 bg-orange-500 text-white rounded-full flex items-center justify-center flex-shrink-0">
              1
            </div>
            <div>
              <p className="text-sm text-gray-700">Accept available delivery orders</p>
            </div>
          </div>
          <div className="flex gap-3">
            <div className="w-8 h-8 bg-orange-500 text-white rounded-full flex items-center justify-center flex-shrink-0">
              2
            </div>
            <div>
              <p className="text-sm text-gray-700">Pick up from canteen and deliver to location</p>
            </div>
          </div>
          <div className="flex gap-3">
            <div className="w-8 h-8 bg-orange-500 text-white rounded-full flex items-center justify-center flex-shrink-0">
              3
            </div>
            <div>
              <p className="text-sm text-gray-700">Earn points (10% of order value) for rewards</p>
            </div>
          </div>
        </div>
      </div>

      {/* Active Deliveries */}
      {activeDeliveries.length > 0 && (
        <div className="mb-8">
          <h2 className="text-2xl text-gray-900 mb-4">My Active Deliveries</h2>
          <div className="space-y-4">
            {activeDeliveries.map((delivery) => (
              <div key={delivery.id} className="bg-white rounded-xl shadow-md p-6 border-2 border-orange-500">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-lg text-gray-900">Order #{delivery.order_id}</span>
                      <span className="bg-orange-100 text-orange-700 text-xs px-2 py-1 rounded-full">
                        In Progress
                      </span>
                    </div>
                    <p className="text-gray-600">Phone: {delivery.customer_phone || "N/A"}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xl text-gray-900">₹{delivery.total_amount?.toFixed(2) || "N/A"}</p>
                    <p className="text-sm text-green-600">+{Math.floor((delivery.total_amount || 0) / 10)} points</p>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-gray-600 mb-4">
                  <MapPin className="w-5 h-5" />
                  <span>{delivery.delivery_address || "N/A"}</span>
                </div>

                {delivery.estimated_time && (
                  <div className="flex items-center gap-2 text-gray-600 mb-4">
                    <Clock className="w-5 h-5" />
                    <span>Est. delivery: {new Date(delivery.estimated_time).toLocaleTimeString()}</span>
                  </div>
                )}

                <button
                  onClick={() => {
                    const earnedPoints = Math.floor((delivery.total_amount || 0) / 10) + (totalDeliveries === 0 ? 50 : 0);
                    completeDelivery(delivery.id, earnedPoints);
                  }}
                  className="w-full bg-green-500 hover:bg-green-600 text-white py-3 rounded-lg flex items-center justify-center gap-2 transition-colors"
                >
                  <CheckCircle className="w-5 h-5" />
                  <span>Mark as Delivered</span>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Available Orders */}
      <div>
        <h2 className="text-2xl text-gray-900 mb-4">Available Orders</h2>
        {isLoading ? (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <Bike className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">Loading available deliveries...</p>
          </div>
        ) : availableDeliveries.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <Bike className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">No orders available for delivery right now</p>
            <p className="text-gray-400 text-sm mt-2">Check back soon for new opportunities!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {availableDeliveries.map((delivery) => (
              <div key={delivery.id} className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <span className="text-lg text-gray-900">Order #{delivery.order_id}</span>
                    <p className="text-sm text-gray-600 mt-1">
                      {delivery.customer_phone || "Customer"}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xl text-gray-900">₹{delivery.total_amount?.toFixed(2) || "N/A"}</p>
                    <p className="text-sm text-green-600">+{Math.floor((delivery.total_amount || 0) / 10)} pts</p>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-gray-600 mb-2">
                  <MapPin className="w-4 h-4" />
                  <span className="text-sm">{delivery.delivery_address || "Location TBD"}</span>
                </div>

                {delivery.estimated_time && (
                  <div className="flex items-center gap-2 text-gray-600 mb-4">
                    <Clock className="w-4 h-4" />
                    <span className="text-sm">
                      Est: {new Date(delivery.estimated_time).toLocaleTimeString()}
                    </span>
                  </div>
                )}

                <button
                  onClick={() => acceptDelivery(delivery.id)}
                  className="w-full bg-orange-500 hover:bg-orange-600 text-white py-3 rounded-lg flex items-center justify-center gap-2 transition-colors"
                >
                  <Bike className="w-5 h-5" />
                  <span>Accept Delivery</span>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
