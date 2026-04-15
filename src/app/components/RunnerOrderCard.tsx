import { useEffect, useMemo, useState } from "react";
import { Clock3, MapPin, ShoppingBag, Sparkles, CheckCircle2 } from "lucide-react";

interface RunnerOrderCardProps {
  order: any;
  onAccept: (orderId: string) => Promise<void>;
  acceptingOrderId?: string | null;
  isTaken?: boolean;
}

export function RunnerOrderCard({ order, onAccept, acceptingOrderId, isTaken = false }: RunnerOrderCardProps) {
  const orderId = order.id || order.order_id;
  const expiresAt = useMemo(() => {
    const created = new Date(order.placed_at || Date.now()).getTime();
    return created + 5 * 60 * 1000;
  }, [order.placed_at]);
  const [timeLeft, setTimeLeft] = useState(Math.max(0, expiresAt - Date.now()));

  useEffect(() => {
    const interval = window.setInterval(() => {
      setTimeLeft(Math.max(0, expiresAt - Date.now()));
    }, 1000);
    return () => window.clearInterval(interval);
  }, [expiresAt]);

  const countdownWidth = `${Math.max(0, Math.min(100, (timeLeft / (5 * 60 * 1000)) * 100))}%`;
  const isAccepting = acceptingOrderId === orderId;
  const canAccept = !!orderId && !isAccepting && !isTaken && timeLeft > 0;

  const handleCardClick = () => {
    if (canAccept) onAccept(orderId);
  };

  return (
    <div
      role="button"
      tabIndex={canAccept ? 0 : -1}
      onKeyDown={(e) => e.key === "Enter" && handleCardClick()}
      onClick={handleCardClick}
      className={`overflow-hidden rounded-2xl border bg-white shadow-sm transition-all duration-300 select-none ${
        isTaken
          ? "opacity-40 translate-x-6 border-gray-100 cursor-not-allowed"
          : isAccepting
          ? "border-emerald-300 shadow-emerald-100 cursor-wait"
          : canAccept
          ? "border-orange-100 hover:border-orange-300 hover:shadow-md cursor-pointer active:scale-[0.99]"
          : "border-gray-100 cursor-not-allowed opacity-60"
      }`}
    >
      <div className="p-5">
        <div className="flex items-start justify-between gap-3 mb-4">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-orange-50 px-3 py-1 text-xs font-semibold text-orange-700">
              <span className="inline-flex h-2 w-2 rounded-full bg-orange-500 animate-pulse" />
              NEW ORDER
            </div>
            <h3 className="mt-3 text-lg font-bold text-gray-900">Order #{order.token_number || order.order_number}</h3>
            <p className="mt-1 text-sm text-gray-500">
              {(order.item_count || 0)} item{order.item_count === 1 ? "" : "s"} · {order.customer_name || "Campus User"}
            </p>
          </div>
          <div className="flex flex-col items-end gap-1 flex-shrink-0">
            <span className="text-xs text-gray-400">{Math.max(1, Math.ceil(timeLeft / 60000))}m left</span>
            {isAccepting && (
              <span className="text-xs font-semibold text-emerald-600 animate-pulse">Accepting…</span>
            )}
          </div>
        </div>

        <div className="space-y-3 text-sm text-gray-700">
          <div className="flex items-start gap-3">
            <MapPin className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-semibold text-gray-900">Pickup</p>
              <p className="text-gray-500">{order.pickup_location || "Campus kitchen"}</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <MapPin className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-semibold text-gray-900">Deliver</p>
              <p className="text-gray-500">{order.delivery_location || order.delivery_address}</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <ShoppingBag className="w-4 h-4 text-sky-500 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-semibold text-gray-900">Items</p>
              <p className="text-gray-500">
                {(order.items_preview || order.items_summary || []).join(", ") || `${order.item_count || 0} item(s)`}
              </p>
            </div>
          </div>
        </div>

        {/* Stats row */}
        <div className="mt-4 flex items-center justify-between rounded-xl bg-gray-50 px-4 py-3 text-sm">
          <div className="flex items-center gap-2 text-gray-600">
            <Clock3 className="w-4 h-4 text-orange-500" />
            <span>~{order.estimated_prep_time || 15} mins</span>
          </div>
          <div className="flex items-center gap-2 font-semibold text-orange-600">
            <Sparkles className="w-4 h-4" />
            <span>{order.reward_points || 10} pts</span>
          </div>
        </div>

        {/* Amount + tap hint */}
        <div className="mt-3 flex items-center justify-between rounded-xl border border-gray-100 px-4 py-3 text-sm">
          <div>
            <p className="font-bold text-gray-900">₹{Number(order.total_amount || 0).toFixed(2)}</p>
            <p className="text-xs text-gray-400 mt-0.5">
              {order.payment_status === "paid" ? "Paid" : "Pay on Delivery"} · {String(order.payment_method || "COD").toUpperCase()}
            </p>
          </div>
          {!isTaken && !isAccepting && canAccept && (
            <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-600 bg-emerald-50 px-3 py-1.5 rounded-lg">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Tap to accept
            </div>
          )}
          {isAccepting && (
            <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-600 bg-emerald-50 px-3 py-1.5 rounded-lg animate-pulse">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Accepting…
            </div>
          )}
          {isTaken && (
            <span className="text-xs text-gray-400 font-medium">Already taken</span>
          )}
        </div>
      </div>

      {/* Countdown bar */}
      <div className="h-1 bg-gray-100">
        <div
          className="h-full bg-gradient-to-r from-orange-400 to-amber-300 transition-all duration-1000"
          style={{ width: countdownWidth }}
        />
      </div>
    </div>
  );
}
