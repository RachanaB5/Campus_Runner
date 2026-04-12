import { useEffect, useMemo, useState } from "react";
import { Clock3, MapPin, ShoppingBag, Sparkles } from "lucide-react";

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

  return (
    <div className={`overflow-hidden rounded-2xl border border-orange-100 bg-white shadow-lg transition-all duration-500 ${
      isTaken ? "opacity-40 translate-x-6" : "opacity-100 translate-x-0"
    }`}>
      <div className="p-5">
        <div className="flex items-start justify-between gap-3 mb-4">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-orange-50 px-3 py-1 text-xs font-semibold text-orange-700">
              <span className="inline-flex h-2 w-2 rounded-full bg-orange-500 animate-pulse" />
              NEW ORDER
            </div>
            <h3 className="mt-3 text-lg font-bold text-gray-900">Order #{order.token_number || order.order_number}</h3>
            <p className="mt-1 text-sm text-gray-500">
              {(order.item_count || 0)} item{order.item_count === 1 ? "" : "s"} • {order.customer_name || "Campus User"}
            </p>
          </div>
          <span className="text-xs text-gray-400">{Math.max(1, Math.ceil(timeLeft / 60000))}m left</span>
        </div>

        <div className="space-y-3 text-sm text-gray-700">
          <div className="flex items-start gap-3">
            <MapPin className="w-4 h-4 text-orange-500 mt-0.5" />
            <div>
              <p className="font-semibold text-gray-900">Pickup</p>
              <p>{order.pickup_location || "Campus kitchen"}</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <MapPin className="w-4 h-4 text-emerald-500 mt-0.5" />
            <div>
              <p className="font-semibold text-gray-900">Deliver</p>
              <p>{order.delivery_location || order.delivery_address}</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <ShoppingBag className="w-4 h-4 text-sky-500 mt-0.5" />
            <div>
              <p className="font-semibold text-gray-900">Items</p>
              <p>
                {(order.items_preview || order.items_summary || []).join(", ") || `${order.item_count || 0} item(s)`}
                {order.item_count > 2 ? ` +${order.item_count - 2} more` : ""}
              </p>
            </div>
          </div>
        </div>

        <div className="mt-5 flex items-center justify-between rounded-2xl bg-orange-50 px-4 py-3 text-sm">
          <div className="flex items-center gap-2 text-gray-700">
            <Clock3 className="w-4 h-4 text-orange-600" />
            <span>~{order.estimated_prep_time || 15} mins</span>
          </div>
          <div className="flex items-center gap-2 font-semibold text-orange-700">
            <Sparkles className="w-4 h-4" />
            <span>{order.reward_points || 10} pts</span>
          </div>
        </div>

        <div className="mt-3 rounded-2xl border border-gray-100 px-4 py-3 text-sm">
          <p className="font-semibold text-orange-600">₹{Number(order.total_amount || 0).toFixed(2)}</p>
          <p className="mt-1 text-gray-500">
            {order.payment_status === "paid" ? "Paid" : "Pay on Delivery"} via {String(order.payment_method || "N/A").toUpperCase()}
          </p>
        </div>

        <button
          type="button"
          onClick={() => orderId && onAccept(orderId)}
          disabled={!orderId || isAccepting || isTaken || timeLeft <= 0}
          className="mt-5 w-full rounded-xl bg-gradient-to-r from-emerald-500 to-green-600 py-3 text-white font-semibold shadow-md hover:shadow-lg disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isTaken ? "Already taken" : isAccepting ? "Accepting..." : "Accept Order"}
        </button>
      </div>
      <div className="h-1.5 bg-orange-100">
        <div className="h-full bg-gradient-to-r from-orange-500 to-amber-400 transition-all duration-1000" style={{ width: countdownWidth }} />
      </div>
    </div>
  );
}
