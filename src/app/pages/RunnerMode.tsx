import { useEffect, useMemo, useState } from "react";
import { AlertCircle, Bell, Bike, CheckCircle, DollarSign, Power, TrendingUp } from "lucide-react";
import { useNavigate } from "react-router";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { useSocket } from "../hooks/useSocket";
import { RunnerOrderCard } from "../components/RunnerOrderCard";

interface RunnerOrder {
  id: string;
  order_id?: string;
  order_number: string;
  customer_name?: string;
  customer_phone?: string | null;
  delivery_address: string;
  total_amount: number;
  status: string;
  items_summary?: string[];
  item_count?: number;
  reward_points?: number;
  pickup_location?: string;
  delivery_location?: string;
  estimated_prep_time?: number;
  placed_at?: string;
}

interface ActiveDelivery {
  deliveryId?: string;
  order: RunnerOrder;
  currentStatus: "assigned" | "picked_up" | "in_transit" | "awaiting_otp";
  otp?: string;
}

function playNotificationChime() {
  try {
    const audioContext = new window.AudioContext();
    const oscillator = audioContext.createOscillator();
    const gain = audioContext.createGain();
    oscillator.connect(gain);
    gain.connect(audioContext.destination);
    oscillator.type = "sine";
    oscillator.frequency.value = 880;
    gain.gain.value = 0.06;
    oscillator.start();
    oscillator.stop(audioContext.currentTime + 0.15);
  } catch {
    return;
  }
}

export function RunnerMode() {
  const { isLoggedIn, user } = useAuth();
  const navigate = useNavigate();
  const socket = useSocket(isLoggedIn);

  const [availableOrders, setAvailableOrders] = useState<RunnerOrder[]>([]);
  const [activeDeliveries, setActiveDeliveries] = useState<ActiveDelivery[]>([]);
  const [completedCount, setCompletedCount] = useState(0);
  const [totalEarnings, setTotalEarnings] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isOnline, setIsOnline] = useState(false);
  const [isTogglingOnline, setIsTogglingOnline] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState("");
  const [acceptingOrderId, setAcceptingOrderId] = useState<string | null>(null);
  const [otpInputs, setOtpInputs] = useState<Record<string, string>>({});
  const [takenOrderIds, setTakenOrderIds] = useState<string[]>([]);
  const activeCount = activeDeliveries.length;

  useEffect(() => {
    if (!isLoggedIn) {
      navigate("/login");
      return;
    }
    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission().catch(() => undefined);
    }
  }, [isLoggedIn, navigate]);

  const showToast = (message: string) => {
    setToastMessage(message);
    window.setTimeout(() => setToastMessage(""), 3000);
  };

  const fetchAvailableOrders = async () => {
    try {
      const response = await api.getAvailableOrders();
      setAvailableOrders(response.available_orders || []);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to load runner orders");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!isLoggedIn) return;
    fetchAvailableOrders();
    const interval = window.setInterval(fetchAvailableOrders, 15000);
    return () => window.clearInterval(interval);
  }, [isLoggedIn]);

  useEffect(() => {
    if (!socket || !isLoggedIn) {
      return;
    }

    const handleNewOrder = (order: RunnerOrder) => {
      const normalizedOrder = {
        ...order,
        id: order.id || order.order_id || "",
      };
      playNotificationChime();
      if ("Notification" in window && Notification.permission === "granted") {
        new Notification("New Order!", {
          body: `${normalizedOrder.item_count || 0} items • Earn ${normalizedOrder.reward_points || 0} pts`,
          tag: `order-${normalizedOrder.id}`,
        });
      }
      setAvailableOrders((previous) => {
        if (!normalizedOrder.id || previous.some((item) => item.id === normalizedOrder.id)) {
          return previous;
        }
        return [normalizedOrder, ...previous];
      });
      showToast("New order available nearby");
    };

    const handleOrderTaken = ({ order_id }: { order_id: string }) => {
      setTakenOrderIds((previous) => [...new Set([...previous, order_id])]);
      window.setTimeout(() => {
        setAvailableOrders((previous) => previous.filter((order) => order.id !== order_id));
        setTakenOrderIds((previous) => previous.filter((id) => id !== order_id));
      }, 900);
    };

    socket.on("new_order_available", handleNewOrder);
    socket.on("order_taken", handleOrderTaken);

    if (isOnline) {
      socket.emit("runner_online");
    }

    return () => {
      socket.off("new_order_available", handleNewOrder);
      socket.off("order_taken", handleOrderTaken);
      if (isOnline) {
        socket.emit("runner_offline");
      }
    };
  }, [isLoggedIn, isOnline, socket]);

  const toggleOnline = async () => {
    setIsTogglingOnline(true);
    try {
      const response = await api.toggleRunnerAvailability();
      const nextOnline = Boolean(response.runner?.is_available ?? response.is_available);
      setIsOnline(nextOnline);
      if (socket) {
        socket.emit(nextOnline ? "runner_online" : "runner_offline");
      }
      showToast(nextOnline ? "Runner mode is live" : "Runner mode paused");
    } catch (err: any) {
      setError(err.message || "Could not update runner availability");
    } finally {
      setIsTogglingOnline(false);
    }
  };

  const acceptOrder = async (orderId: string) => {
    setAcceptingOrderId(orderId);
    try {
      const response = await api.acceptOrder(orderId);
      const order = availableOrders.find((item) => item.id === orderId);
      if (order) {
        setActiveDeliveries((previous) => [{ order, deliveryId: response.delivery_id, currentStatus: "assigned" }, ...previous]);
      }
      setAvailableOrders((previous) => previous.filter((item) => (item.id || item.order_id) !== orderId));
      showToast(response.message || "Order accepted");
      localStorage.setItem("runner-open-delivery", response.delivery_id);
      window.dispatchEvent(new CustomEvent("runner:active-delivery-changed", {
        detail: { deliveryId: response.delivery_id },
      }));
      navigate(`/runner/delivery/${response.delivery_id}`, {
        state: {
          order: response.order,
          order_id: orderId,
          delivery_id: response.delivery_id,
          pickup_otp: response.pickup_otp,
        },
      });
    } catch (err: any) {
      setTakenOrderIds((previous) => [...new Set([...previous, orderId])]);
      showToast(err.message || "Order was already taken");
      window.setTimeout(() => {
        setAvailableOrders((previous) => previous.filter((item) => (item.id || item.order_id) !== orderId));
        setTakenOrderIds((previous) => previous.filter((id) => id !== orderId));
      }, 900);
    } finally {
      setAcceptingOrderId(null);
    }
  };

  const pickupOrder = async (orderId: string) => {
    try {
      await api.pickupOrder(orderId);
      setActiveDeliveries((previous) =>
        previous.map((delivery) =>
          delivery.order.id === orderId ? { ...delivery, currentStatus: "picked_up" } : delivery,
        ),
      );
      showToast("Order picked up");
    } catch (err: any) {
      showToast(err.message || "Could not pick up order");
    }
  };

  const markInTransit = async (orderId: string) => {
    try {
      await api.markInTransit(orderId);
      setActiveDeliveries((previous) =>
        previous.map((delivery) =>
          delivery.order.id === orderId ? { ...delivery, currentStatus: "in_transit" } : delivery,
        ),
      );
      showToast("Order is now in transit");
    } catch (err: any) {
      showToast(err.message || "Could not update order");
    }
  };

  const requestOtp = async (orderId: string) => {
    try {
      const response = await api.deliverOrder(orderId);
      setActiveDeliveries((previous) =>
        previous.map((delivery) =>
          delivery.order.id === orderId
            ? { ...delivery, currentStatus: "awaiting_otp", otp: response.otp }
            : delivery,
        ),
      );
      showToast("Customer OTP requested");
    } catch (err: any) {
      showToast(err.message || "Could not request delivery OTP");
    }
  };

  const confirmOtp = async (orderId: string) => {
    try {
      await api.confirmDelivery(orderId, otpInputs[orderId] || "");
      const completed = activeDeliveries.find((delivery) => delivery.order.id === orderId);
      setActiveDeliveries((previous) => previous.filter((delivery) => delivery.order.id !== orderId));
      setOtpInputs((previous) => ({ ...previous, [orderId]: "" }));
      if (completed) {
        setCompletedCount((previous) => previous + 1);
        setTotalEarnings((previous) => previous + (completed.order.reward_points || 10));
      }
      showToast("Delivery completed");
    } catch (err: any) {
      showToast(err.message || "Invalid OTP");
    }
  };

  const stats = useMemo(
    () => [
      { label: "Completed Today", value: completedCount, color: "from-orange-500 to-red-500", icon: Bike },
      { label: "Points Earned", value: totalEarnings, color: "from-green-500 to-emerald-600", icon: DollarSign },
      { label: "Active Deliveries", value: activeCount, color: "from-blue-500 to-indigo-600", icon: TrendingUp },
      { label: "Open Orders", value: availableOrders.length, color: "from-purple-500 to-fuchsia-600", icon: Bell },
    ],
    [activeCount, availableOrders.length, completedCount, totalEarnings],
  );

  if (!isLoggedIn) {
    return null;
  }

  return (
    <div className="min-h-screen bg-[var(--bg)]">
      {toastMessage && (
        <div className="fixed top-5 right-5 z-50 rounded-xl bg-orange-500 px-5 py-3 text-sm font-semibold text-white shadow-xl animate-in slide-in-from-right-8">
          {toastMessage}
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900">Runner Dashboard</h1>
            <p className="text-gray-600 mt-2">Claim nearby orders, deliver fast, and keep the queue moving.</p>
          </div>
          <button
            type="button"
            onClick={toggleOnline}
            disabled={isTogglingOnline}
            className={`inline-flex items-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold shadow-lg transition-all ${
              isOnline
                ? "bg-gradient-to-r from-emerald-500 to-green-600 text-white"
                : "bg-white text-gray-800 border border-orange-200"
            }`}
          >
            <Power className="w-4 h-4" />
            {isTogglingOnline ? "Updating..." : isOnline ? "Go Offline" : "Go Online"}
          </button>
        </div>

        {error && (
          <div className="mb-6 flex items-center gap-3 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-red-700">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          {stats.map(({ label, value, color, icon: Icon }) => (
            <div key={label} className={`rounded-2xl bg-gradient-to-br ${color} p-6 text-white shadow-lg`}>
              <div className="flex items-center justify-between">
                <Icon className="w-8 h-8 opacity-80" />
                <span className="text-3xl font-bold">{value}</span>
              </div>
              <p className="mt-3 text-sm text-white/85">{label}</p>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-[1.15fr_0.85fr] gap-8">
          <section>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Available Orders</h2>
                <p className="text-sm text-gray-600 mt-1">Real-time cards slide in here as soon as confirmed orders drop.</p>
              </div>
              <div className="rounded-full bg-orange-50 px-3 py-1 text-sm font-semibold text-orange-700">
                {availableOrders.length} open
              </div>
            </div>

            {isLoading ? (
              <div className="rounded-2xl border border-orange-100 bg-white p-8 text-gray-500">Loading runner queue...</div>
            ) : availableOrders.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-orange-200 bg-white p-10 text-center">
                <CheckCircle className="w-12 h-12 text-emerald-500 mx-auto mb-4" />
                <p className="font-semibold text-gray-900">No open orders right now</p>
                <p className="text-sm text-gray-500 mt-2">Stay online and we’ll push the next confirmed order here instantly.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {availableOrders.map((order) => (
                  <RunnerOrderCard
                    key={order.id || order.order_id}
                    order={order}
                    onAccept={acceptOrder}
                    acceptingOrderId={acceptingOrderId}
                    isTaken={takenOrderIds.includes(order.id || order.order_id || "")}
                  />
                ))}
              </div>
            )}
          </section>

          <section>
            <div className="mb-4">
              <h2 className="text-2xl font-bold text-gray-900">My Active Deliveries</h2>
              <p className="text-sm text-gray-600 mt-1">Accepted orders move here so you can run pickup, transit, and OTP confirmation.</p>
            </div>

            <div className="space-y-4">
              {activeDeliveries.length === 0 && (
                <div className="rounded-2xl border border-orange-100 bg-white p-8 text-center text-gray-500">
                  Your accepted orders will appear here.
                </div>
              )}

              {activeDeliveries.map((delivery) => (
                <div key={delivery.order.id} className="rounded-2xl border border-orange-100 bg-white p-5 shadow-md">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-xs uppercase tracking-[0.2em] text-orange-500 font-semibold">Assigned Order</p>
                      <h3 className="text-xl font-bold text-gray-900 mt-2">{delivery.order.order_number}</h3>
                      <p className="text-sm text-gray-500 mt-1">{delivery.order.customer_name || user?.name}</p>
                    </div>
                    <div className="rounded-full bg-orange-50 px-3 py-1 text-xs font-semibold text-orange-700">
                      {delivery.currentStatus.replace("_", " ")}
                    </div>
                  </div>

                  <div className="mt-4 space-y-3 text-sm">
                    <p className="text-gray-700"><span className="font-semibold text-gray-900">Address:</span> {delivery.order.delivery_address}</p>
                    {delivery.order.customer_phone && (
                      <a href={`tel:${delivery.order.customer_phone}`} className="flex items-center gap-2 text-blue-600">
                        <PhoneCall className="w-4 h-4" />
                        {delivery.order.customer_phone}
                      </a>
                    )}
                  </div>

                  <div className="mt-5 grid grid-cols-1 gap-3">
                    <button type="button" onClick={() => navigate(`/runner/delivery/${delivery.deliveryId || delivery.order.id}`, { state: { order_id: delivery.order.id } })} className="rounded-xl bg-gray-900 px-4 py-3 text-white font-semibold">
                      Open Delivery Dashboard
                    </button>
                    {delivery.currentStatus === "assigned" && (
                      <button type="button" onClick={() => pickupOrder(delivery.order.id)} className="rounded-xl bg-gradient-to-r from-orange-500 to-red-500 px-4 py-3 text-white font-semibold">
                        Mark Picked Up
                      </button>
                    )}
                    {delivery.currentStatus === "picked_up" && (
                      <button type="button" onClick={() => markInTransit(delivery.order.id)} className="rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 px-4 py-3 text-white font-semibold">
                        Mark In Transit
                      </button>
                    )}
                    {delivery.currentStatus === "in_transit" && (
                      <button type="button" onClick={() => requestOtp(delivery.order.id)} className="rounded-xl bg-gradient-to-r from-amber-500 to-orange-600 px-4 py-3 text-white font-semibold">
                        Request Delivery OTP
                      </button>
                    )}
                    {delivery.currentStatus === "awaiting_otp" && (
                      <div className="space-y-3">
                        <input
                          type="text"
                          maxLength={6}
                          value={otpInputs[delivery.order.id] || ""}
                          onChange={(event) => setOtpInputs((previous) => ({ ...previous, [delivery.order.id]: event.target.value }))}
                          placeholder="Enter 6-digit OTP"
                          className="w-full rounded-xl border border-orange-200 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-orange-300"
                        />
                        <button type="button" onClick={() => confirmOtp(delivery.order.id)} className="w-full rounded-xl bg-gradient-to-r from-emerald-500 to-green-600 px-4 py-3 text-white font-semibold">
                          Confirm Delivery
                        </button>
                        {delivery.otp && (
                          <p className="text-xs text-gray-500">Demo OTP: {delivery.otp}</p>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
