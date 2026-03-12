import { useState } from "react";
import { Bike, MapPin, Clock, Award, CheckCircle, TrendingUp } from "lucide-react";
import { availableOrders } from "../data/mockData";

export function RunnerMode() {
  const [activeDeliveries, setActiveDeliveries] = useState<string[]>([]);
  const [completedToday, setCompletedToday] = useState(5);
  const [totalPoints, setTotalPoints] = useState(245);

  const acceptDelivery = (orderId: string) => {
    setActiveDeliveries([...activeDeliveries, orderId]);
  };

  const completeDelivery = (orderId: string, points: number) => {
    setActiveDeliveries(activeDeliveries.filter(id => id !== orderId));
    setCompletedToday(completedToday + 1);
    setTotalPoints(totalPoints + points);
  };

  const availableForDelivery = availableOrders.filter(
    order => order.status === "ready" && !activeDeliveries.includes(order.id)
  );

  const myActiveDeliveries = availableOrders.filter(
    order => activeDeliveries.includes(order.id)
  );

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
      {myActiveDeliveries.length > 0 && (
        <div className="mb-8">
          <h2 className="text-2xl text-gray-900 mb-4">My Active Deliveries</h2>
          <div className="space-y-4">
            {myActiveDeliveries.map((order) => (
              <div key={order.id} className="bg-white rounded-xl shadow-md p-6 border-2 border-orange-500">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-lg text-gray-900">Order #{order.id}</span>
                      <span className="bg-orange-100 text-orange-700 text-xs px-2 py-1 rounded-full">
                        In Progress
                      </span>
                    </div>
                    <p className="text-gray-600">Customer: {order.customerName}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xl text-gray-900">₹{order.total}</p>
                    <p className="text-sm text-green-600">+{order.points} points</p>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-gray-600 mb-4">
                  <MapPin className="w-5 h-5" />
                  <span>{order.deliveryLocation}</span>
                </div>

                <div className="bg-gray-50 rounded-lg p-3 mb-4">
                  <p className="text-sm text-gray-700 mb-2">Order Items:</p>
                  {order.items.map((item, idx) => (
                    <p key={idx} className="text-sm text-gray-600">
                      {item.quantity}x {item.item.name}
                    </p>
                  ))}
                </div>

                <button
                  onClick={() => completeDelivery(order.id, order.points!)}
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
        {availableForDelivery.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <Bike className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">No orders available for delivery right now</p>
            <p className="text-gray-400 text-sm mt-2">Check back soon for new opportunities!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {availableForDelivery.map((order) => (
              <div key={order.id} className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <span className="text-lg text-gray-900">Order #{order.id}</span>
                    <p className="text-sm text-gray-600 mt-1">
                      {order.customerName}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xl text-gray-900">₹{order.total}</p>
                    <p className="text-sm text-green-600">+{order.points} pts</p>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-gray-600 mb-2">
                  <MapPin className="w-4 h-4" />
                  <span className="text-sm">{order.deliveryLocation}</span>
                </div>

                <div className="flex items-center gap-2 text-gray-600 mb-4">
                  <Clock className="w-4 h-4" />
                  <span className="text-sm">
                    {Math.floor((Date.now() - order.timestamp.getTime()) / 60000)} mins ago
                  </span>
                </div>

                <div className="bg-gray-50 rounded-lg p-3 mb-4">
                  <p className="text-sm text-gray-700 mb-1">Items:</p>
                  {order.items.map((item, idx) => (
                    <p key={idx} className="text-sm text-gray-600">
                      {item.quantity}x {item.item.name}
                    </p>
                  ))}
                </div>

                <button
                  onClick={() => acceptDelivery(order.id)}
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
