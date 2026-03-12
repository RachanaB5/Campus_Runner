import { Clock, CheckCircle, Package, Bike } from "lucide-react";

export function Orders() {
  const orders = [
    {
      id: "ORD123",
      date: "Today, 2:30 PM",
      status: "delivered",
      items: ["Chicken Biryani", "Mango Juice"],
      total: 240,
      points: 12
    },
    {
      id: "ORD122",
      date: "Yesterday, 1:15 PM",
      status: "delivered",
      items: ["Masala Dosa (2)", "Cappuccino (2)"],
      total: 260,
      points: 13
    },
    {
      id: "ORD121",
      date: "Feb 19, 12:45 PM",
      status: "delivered",
      items: ["Veg Burger", "Samosa (2)"],
      total: 110,
      points: 6
    }
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "delivered":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "preparing":
        return <Package className="w-5 h-5 text-orange-500" />;
      case "on-the-way":
        return <Bike className="w-5 h-5 text-blue-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "delivered":
        return { text: "Delivered", color: "text-green-600 bg-green-50" };
      case "preparing":
        return { text: "Preparing", color: "text-orange-600 bg-orange-50" };
      case "on-the-way":
        return { text: "On the way", color: "text-blue-600 bg-blue-50" };
      default:
        return { text: "Pending", color: "text-gray-600 bg-gray-50" };
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div className="mb-8">
        <h1 className="text-3xl text-gray-900 mb-2">Order History</h1>
        <p className="text-gray-600">Track and review your past orders</p>
      </div>

      <div className="space-y-4">
        {orders.map((order) => {
          const statusInfo = getStatusText(order.status);
          
          return (
            <div key={order.id} className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  {getStatusIcon(order.status)}
                  <div>
                    <h3 className="text-lg text-gray-900">Order #{order.id}</h3>
                    <p className="text-sm text-gray-500">{order.date}</p>
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm ${statusInfo.color}`}>
                  {statusInfo.text}
                </span>
              </div>

              <div className="bg-gray-50 rounded-lg p-4 mb-4">
                <p className="text-sm text-gray-700 mb-2">Order Items:</p>
                <ul className="space-y-1">
                  {order.items.map((item, idx) => (
                    <li key={idx} className="text-sm text-gray-600 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-gray-400 rounded-full"></span>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                <div>
                  <p className="text-sm text-gray-600">Total Amount</p>
                  <p className="text-xl text-gray-900">₹{order.total}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600">Points Earned</p>
                  <p className="text-xl text-green-600">+{order.points}</p>
                </div>
              </div>

              <div className="mt-4 flex gap-3">
                <button className="flex-1 bg-orange-500 hover:bg-orange-600 text-white py-2 rounded-lg transition-colors">
                  Reorder
                </button>
                <button className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 rounded-lg transition-colors">
                  View Details
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {orders.length === 0 && (
        <div className="bg-white rounded-xl shadow-sm p-12 text-center">
          <Clock className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">No orders yet</p>
          <p className="text-gray-400 text-sm mt-2">Start ordering to see your history here</p>
        </div>
      )}
    </div>
  );
}
