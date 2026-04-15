import { Clock, CheckCircle, Phone, MapPin, User } from "lucide-react";
import { useState, useEffect } from "react";
import { Link } from "react-router";
import { api } from "../services/api";
import { RateOrderSheet } from "../components/RateOrderSheet";
import { ImageWithFallback } from "../components/figma/ImageWithFallback";
import { useCart } from "../context/CartContext";
import { useNavigate } from "react-router";
import { toast } from "sonner";

export function Orders() {
  const [orders, setOrders] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedOrderId, setExpandedOrderId] = useState<string | null>(null);
  const [ratingOrderId, setRatingOrderId] = useState<string | null>(null);
  const [ratingDeliveryId, setRatingDeliveryId] = useState<string | null>(null);
  const [isReordering, setIsReordering] = useState<string | null>(null);
  const { clearCart, addToCart } = useCart();
  const navigate = useNavigate();

  useEffect(() => {
    fetchMyOrders();
    
    // Set up polling for live updates every 5 seconds
    const pollInterval = setInterval(() => {
      fetchMyOrders();
    }, 5000);

    return () => clearInterval(pollInterval);
  }, []);

  const fetchMyOrders = async () => {
    try {
      const response = await api.getMyOrders();
      if (response && response.orders) {
        setOrders(response.orders);
      }
    } catch (error) {
      console.error("Error fetching orders:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const getOrderStages = (order: any) => {
    const delivery = order.delivery;
    const stages = [
      {
        number: 1,
        title: "Order Received",
        description: "Your order has been confirmed",
        completed: order.status !== 'pending',
      },
      {
        number: 2,
        title: "Delivery Partner Assigned",
        description: delivery?.runner_name ? `${delivery.runner_name} is your delivery partner` : "Finding a delivery partner",
        completed: delivery?.status === 'assigned' || delivery?.status === 'picked_up' || delivery?.status === 'in_transit' || delivery?.status === 'delivered',
      },
      {
        number: 3,
        title: "Order On The Way",
        description: "Your order is being delivered to you",
        completed: delivery?.status === 'picked_up' || delivery?.status === 'in_transit' || delivery?.status === 'delivered',
      },
      {
        number: 4,
        title: "Order Delivered",
        description: "Order delivered successfully",
        completed: delivery?.status === 'delivered' || order.status === 'delivered',
      }
    ];
    return stages;
  };

  const getDeliveryStatus = (status: string) => {
    const statusMap: Record<string, { text: string; color: string }> = {
      pending: { text: "Awaiting", color: "bg-gray-100 text-gray-800" },
      assigned: { text: "Assigned", color: "bg-blue-100 text-blue-800" },
      picked_up: { text: "Picked Up", color: "bg-purple-100 text-purple-800" },
      in_transit: { text: "In Transit", color: "bg-blue-100 text-blue-800" },
      delivered: { text: "Delivered", color: "bg-green-100 text-green-800" },
    };
    return statusMap[status] || { text: "Processing", color: "bg-gray-100 text-gray-800" };
  };

  const handleReorder = async (order: any) => {
    try {
      setIsReordering(order.id);
      await clearCart();
      for (const item of order.items) {
        await addToCart(item.food_id, item.quantity);
      }
      toast.success("Added to cart! Ready for checkout.");
      navigate("/checkout");
    } catch (err: any) {
      console.error(err);
      toast.error(err.message || "Failed to reorder items");
      setIsReordering(null);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Order Tracking</h1>
        <p className="text-gray-600">Track your orders in real-time</p>
      </div>

      <div className="space-y-4">
        {isLoading && orders.length === 0 ? (
          <div className="text-center py-12">
            <Clock className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600">Loading your orders...</p>
          </div>
        ) : orders.length > 0 ? (
          orders.map((order) => {
            const stages = getOrderStages(order);
            const delivery = order.delivery;
            const isExpanded = expandedOrderId === order.id;
            const orderDate = order.created_at 
              ? new Date(order.created_at).toLocaleDateString() + " " + new Date(order.created_at).toLocaleTimeString() 
              : "N/A";

            return (
              <div key={order.id} className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow overflow-hidden">
                {/* Header */}
                <div 
                  className="p-6 cursor-pointer hover:bg-gray-50 transition-colors"
                  onClick={() => setExpandedOrderId(isExpanded ? null : order.id)}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900">Order #{order.order_number}</h3>
                      <p className="text-sm text-gray-500">{orderDate}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-gray-900">₹{Number(order.total_amount).toFixed(2)}</p>
                      <p className="text-sm text-green-600 font-medium">+{Math.floor(order.total_amount / 10)} pts</p>
                      {order.has_unreviewed_items && (
                        <button type="button" onClick={(e) => { e.stopPropagation(); setRatingOrderId(order.id); setRatingDeliveryId(order.delivery?.id || null); }} className="mt-2 rounded-full bg-orange-100 px-3 py-1 text-xs font-semibold text-orange-700">
                          Rate Order
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Stage Progress */}
                  <div className="flex items-center justify-between gap-2">
                    {stages.map((stage, idx) => (
                      <div key={stage.number} className="flex-1 flex items-center">
                        <div className="flex flex-col items-center w-full">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm transition-colors ${
                            stage.completed 
                              ? 'bg-green-500 text-white' 
                              : 'bg-gray-200 text-gray-600'
                          }`}>
                            {stage.completed ? <CheckCircle className="w-5 h-5" /> : stage.number}
                          </div>
                          <p className="text-xs text-gray-600 mt-1 text-center">{stage.title}</p>
                        </div>
                        {idx < stages.length - 1 && (
                          <div className={`h-1 flex-1 mx-1 ${stage.completed ? 'bg-green-500' : 'bg-gray-200'}`}></div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="border-t border-gray-200 p-6 bg-gray-50 space-y-6">
                    {/* Delivery Partner Info */}
                    {delivery && delivery.runner_name && (
                      <div className="bg-white rounded-lg p-4 border border-blue-200">
                        <p className="text-sm font-semibold text-gray-900 mb-3">Delivery Partner</p>
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            {delivery.runner_image ? (
                              <ImageWithFallback src={delivery.runner_image} alt={delivery.runner_name} className="w-12 h-12 rounded-full object-cover" />
                            ) : (
                              <div className="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center">
                                <User className="w-6 h-6 text-orange-600" />
                              </div>
                            )}
                            <div>
                              <p className="font-semibold text-gray-900">{delivery.runner_name}</p>
                              <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium mt-1 ${getDeliveryStatus(delivery.status).color}`}>
                                {getDeliveryStatus(delivery.status).text}
                              </span>
                            </div>
                          </div>
                          {delivery.runner_phone && (
                            <a href={`tel:${delivery.runner_phone}`} className="flex items-center gap-2 px-3 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors">
                              <Phone className="w-4 h-4" />
                              <span className="text-sm">Call</span>
                            </a>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Delivery Address */}
                    {order.delivery_address && (
                      <div className="bg-white rounded-lg p-4 border border-gray-200">
                        <div className="flex items-start gap-3">
                          <MapPin className="w-5 h-5 text-orange-500 flex-shrink-0 mt-0.5" />
                          <div className="flex-1">
                            <p className="text-sm font-semibold text-gray-900 mb-1">Delivery Address</p>
                            <p className="text-sm text-gray-600">{order.delivery_address}</p>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Order Items */}
                    <div className="bg-white rounded-lg p-4 border border-gray-200">
                      <p className="text-sm font-semibold text-gray-900 mb-3">Order Items</p>
                      <ul className="space-y-2">
                        {order.items && order.items.length > 0 ? (
                          order.items.map((item: any, idx: number) => (
                            <li key={idx} className="flex items-center justify-between text-sm">
                              <span className="text-gray-700">{item.food_name || `Food ${item.food_id}`}</span>
                              <div className="flex items-center gap-3">
                                <span className="text-gray-500">x {item.quantity}</span>
                                <span className="font-medium text-gray-900">₹{(item.total_price || 0).toFixed(2)}</span>
                              </div>
                            </li>
                          ))
                        ) : (
                          <li className="text-sm text-gray-600">No items</li>
                        )}
                      </ul>
                    </div>

                    {/* Stage Timeline */}
                    <div className="bg-white rounded-lg p-4 border border-gray-200">
                      <p className="text-sm font-semibold text-gray-900 mb-4">Order Timeline</p>
                      <div className="space-y-4">
                        {stages.map((stage) => (
                          <div key={stage.number} className="flex gap-3">
                            <div className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center font-semibold text-xs ${
                              stage.completed 
                                ? 'bg-green-500 text-white' 
                                : 'bg-gray-300 text-gray-600'
                            }`}>
                              {stage.completed ? <CheckCircle className="w-4 h-4" /> : stage.number}
                            </div>
                            <div className="flex-1">
                              <p className={`font-medium ${stage.completed ? 'text-gray-900' : 'text-gray-500'}`}>
                                {stage.title}
                              </p>
                              <p className="text-sm text-gray-600">{stage.description}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3">
                      {order.status !== "delivered" && (
                        <Link to={`/orders/${order.id}/track`} className="flex-1 bg-orange-500 hover:bg-orange-600 text-white py-2 rounded-lg transition-colors font-medium text-center">
                          Track
                        </Link>
                      )}
                      <button 
                        onClick={() => handleReorder(order)}
                        disabled={isReordering === order.id}
                        className="flex-1 bg-orange-100 hover:bg-orange-200 text-orange-700 py-2 rounded-lg transition-colors font-medium disabled:opacity-50"
                      >
                        {isReordering === order.id ? "Adding..." : "Reorder"}
                      </button>
                      <button className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 rounded-lg transition-colors font-medium">
                        Help
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        ) : (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <Clock className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg font-medium">No orders yet</p>
            <p className="text-gray-400 text-sm mt-2">Start ordering to see your history here</p>
          </div>
        )}
      </div>
      <RateOrderSheet orderId={ratingOrderId} deliveryId={ratingDeliveryId} open={Boolean(ratingOrderId)} onClose={() => { setRatingOrderId(null); setRatingDeliveryId(null); }} onSubmitted={fetchMyOrders} />
    </div>
  );
}
