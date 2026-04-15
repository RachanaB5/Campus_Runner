import { useEffect, useMemo, useState } from "react";
import { AlertCircle, Bike, CheckCircle, DollarSign, PhoneCall, Power, Star, TrendingUp } from "lucide-react";
import { useNavigate } from "react-router";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { useSocket } from "../hooks/useSocket";
import { RunnerOrderCard } from "../components/RunnerOrderCard";
import { useRunnerState } from "../hooks/useRunnerState";

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
  const runner = useRunnerState();

  const [availableOrders, setAvailableOrders] = useState<RunnerOrder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isTogglingOnline, setIsTogglingOnline] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState("");
  const [acceptingOrderId, setAcceptingOrderId] = useState<string | null>(null);
  const [takenOrderIds, setTakenOrderIds] = useState<string[]>([]);
  const [activeDeliveryId, setActiveDeliveryId] = useState<string | null>(null);
  const [activeDeliveryLabel, setActiveDeliveryLabel] = useState<string>("");
  const [activeCustomerPhone, setActiveCustomerPhone] = useState<string | null>(null);
  const [activeAddress, setActiveAddress] = useState<string>("");
  const [activeCustomerName, setActiveCustomerName] = useState<string>("");
  const [runnerDeliveries, setRunnerDeliveries] = useState(0);
  const [runnerEarnings, setRunnerEarnings] = useState(0);
  const [runnerQueueMessage, setRunnerQueueMessage] = useState("");

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
      setRunnerQueueMessage(response.message || "");
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to load runner orders");
    } finally {
      setIsLoading(false);
    }
  };

  const refreshRunnerContext = async () => {
    try {
      const active = await api.getRunnerActiveDelivery();
      if (active.active && active.delivery_id) {
        setActiveDeliveryId(active.delivery_id);
        setActiveDeliveryLabel(
          active.order?.token_number || active.details?.token_number || active.delivery_id,
        );
        setActiveCustomerName(active.customer_name || active.details?.customer_name || "");
        setActiveCustomerPhone(active.customer_phone || active.details?.customer_phone || null);
        setActiveAddress(active.order?.delivery_address || active.details?.delivery_address || "");
      } else {
        setActiveDeliveryId(null);
        setActiveDeliveryLabel("");
        setActiveCustomerName("");
        setActiveCustomerPhone(null);
        setActiveAddress("");
      }
    } catch {
      setActiveDeliveryId(null);
      setActiveDeliveryLabel("");
      setActiveCustomerName("");
      setActiveCustomerPhone(null);
      setActiveAddress("");
    }

    try {
      const profile = await api.getRunnerProfile();
      setRunnerDeliveries(profile.total_deliveries ?? 0);
      setRunnerEarnings(profile.total_earnings ?? 0);
    } catch {
      setRunnerDeliveries(0);
      setRunnerEarnings(0);
    }
  };

  useEffect(() => {
    if (!isLoggedIn) return;
    fetchAvailableOrders();
    refreshRunnerContext();
    const interval = window.setInterval(() => {
      fetchAvailableOrders();
      refreshRunnerContext();
    }, 15000);
    return () => window.clearInterval(interval);
  }, [isLoggedIn]);

  useEffect(() => {
    const handleRunnerStatusChanged = async (event: Event) => {
      const detail = (event as CustomEvent<{ isOnline?: boolean }>).detail || {};
      if (typeof detail.isOnline === "boolean") {
        if (detail.isOnline) {
          await fetchAvailableOrders();
        } else {
          setAvailableOrders([]);
          setRunnerQueueMessage("Turn Runner Mode on to start receiving live delivery requests.");
        }
        await refreshRunnerContext();
      }
    };

    window.addEventListener("runner:status-changed", handleRunnerStatusChanged as EventListener);
    return () => window.removeEventListener("runner:status-changed", handleRunnerStatusChanged as EventListener);
  }, []);

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

    if (runner.isAvailable) {
      socket.emit("runner_go_online", { token: localStorage.getItem("access_token") });
    }

    return () => {
      socket.off("new_order_available", handleNewOrder);
      socket.off("order_taken", handleOrderTaken);
      if (runner.isAvailable) {
        socket.emit("runner_go_offline", { token: localStorage.getItem("access_token") });
      }
    };
  }, [isLoggedIn, runner.isAvailable, socket]);

  const toggleOnline = async () => {
    setIsTogglingOnline(true);
    try {
      const nextOnline = await runner.toggle();
      if (nextOnline) {
        await fetchAvailableOrders();
      } else {
        setAvailableOrders([]);
        setRunnerQueueMessage("Turn Runner Mode on to start receiving live delivery requests.");
      }
      await refreshRunnerContext();
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
      if (!runner.isAvailable) {
        const nextOnline = await runner.toggle(true);
        if (nextOnline) {
          await fetchAvailableOrders();
        }
      }
      const response = await api.acceptOrder(orderId);
      setAvailableOrders((previous) => previous.filter((item) => (item.id || item.order_id) !== orderId));
      showToast(response.message || "Order accepted! See Active Delivery below.");
      // Update active delivery state — runner stays on dashboard
      setActiveDeliveryId(response.delivery_id);
      setActiveDeliveryLabel(response.order?.token_number || response.order?.order_number || response.delivery_id);
      setActiveCustomerName(response.order?.customer_name || "");
      setActiveAddress(response.order?.delivery_address || "");
      setActiveCustomerPhone(null);
      localStorage.setItem("runner-open-delivery", response.delivery_id);
      window.dispatchEvent(new CustomEvent("runner:active-delivery-changed", {
        detail: { deliveryId: response.delivery_id },
      }));
      await refreshRunnerContext();
      // Do NOT auto-navigate — let runner click "Open delivery dashboard" manually
    } catch (err: any) {
      const message = err.message || "Could not accept this order";
      showToast(message);

      if (err.status === 409) {
        setTakenOrderIds((previous) => [...new Set([...previous, orderId])]);
        window.setTimeout(() => {
          setAvailableOrders((previous) => previous.filter((item) => (item.id || item.order_id) !== orderId));
          setTakenOrderIds((previous) => previous.filter((id) => id !== orderId));
        }, 900);
      } else {
        await fetchAvailableOrders();
        await refreshRunnerContext();
      }
    } finally {
      setAcceptingOrderId(null);
    }
  };

  const activeCount = activeDeliveryId ? 1 : 0;

  const stats = useMemo(
    () => [
      { label: "Lifetime deliveries", value: runnerDeliveries, color: "from-orange-500 to-red-500", icon: Bike },
      { label: "Total earnings", value: runnerEarnings, color: "from-green-500 to-emerald-600", icon: DollarSign },
      { label: "Active delivery", value: activeCount, color: "from-blue-500 to-indigo-600", icon: TrendingUp },
      { label: "Runner rating", value: runner.averageRating > 0 ? runner.averageRating.toFixed(1) : "New", color: "from-purple-500 to-fuchsia-600", icon: Star },
    ],
    [activeCount, runner.averageRating, runnerDeliveries, runnerEarnings],
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
            <p className="text-gray-600 mt-2">Claim nearby orders, then use the delivery dashboard for pickup and drop-off.</p>
          </div>
          <button
            type="button"
            onClick={toggleOnline}
            disabled={isTogglingOnline}
            className={`inline-flex items-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold shadow-lg transition-all ${
              runner.isAvailable
                ? "bg-gradient-to-r from-emerald-500 to-green-600 text-white"
                : "bg-white text-gray-800 border border-orange-200"
            }`}
          >
            <Power className="w-4 h-4" />
            {isTogglingOnline ? "Updating..." : runner.isAvailable ? "Go Offline" : "Go Online"}
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
                <p className="font-semibold text-gray-900">
                  {runner.isAvailable ? "No open runner orders right now" : "Runner Mode is currently off"}
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  {runnerQueueMessage || (runner.isAvailable
                    ? "Stay online and we’ll push the next confirmed order here instantly."
                    : "Switch on Runner Mode to receive delivery requests.")}
                </p>
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
              <h2 className="text-2xl font-bold text-gray-900">Active delivery</h2>
              <p className="text-sm text-gray-600 mt-1">Pickup, transit, and customer OTP all happen in one place.</p>
            </div>

            {!activeDeliveryId ? (
              <div className="rounded-2xl border border-orange-100 bg-white p-8 text-center text-gray-500">
                When you accept an order, you’ll land in the delivery dashboard. Any in-progress delivery also appears here.
              </div>
            ) : (
              <div className="rounded-2xl border border-orange-100 bg-white p-5 shadow-md space-y-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-orange-500 font-semibold">In progress</p>
                  <h3 className="text-xl font-bold text-gray-900 mt-2">Order {activeDeliveryLabel}</h3>
                  <p className="text-sm text-gray-500 mt-1">{activeCustomerName || user?.name}</p>
                </div>
                {activeAddress && (
                  <p className="text-sm text-gray-700">
                    <span className="font-semibold text-gray-900">Drop-off:</span> {activeAddress}
                  </p>
                )}
                {activeCustomerPhone && (
                  <a href={`tel:${activeCustomerPhone}`} className="inline-flex items-center gap-2 text-sm text-blue-600 font-medium">
                    <PhoneCall className="w-4 h-4" />
                    {activeCustomerPhone}
                  </a>
                )}
                <button
                  type="button"
                  onClick={() => navigate(`/runner/delivery/${activeDeliveryId}`)}
                  className="w-full rounded-xl bg-gray-900 px-4 py-3 text-white font-semibold"
                >
                  Open delivery dashboard
                </button>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
