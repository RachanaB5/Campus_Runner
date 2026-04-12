import { useEffect, useState } from "react";
import { PhoneCall, X } from "lucide-react";
import { api } from "../services/api";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import { getFoodImageUrl } from "../utils/foodImages";

interface RunnerOrderDetailModalProps {
  orderId: string | null;
  open: boolean;
  previewOnly?: boolean;
  onClose: () => void;
  onAccepted?: (payload: any) => void;
  onDelivered?: (points: number) => void;
}

export function RunnerOrderDetailModal({ orderId, open, previewOnly = false, onClose, onAccepted, onDelivered }: RunnerOrderDetailModalProps) {
  const [details, setDetails] = useState<any>(null);
  const [deliveryOtp, setDeliveryOtp] = useState("");
  const [pickupOtp, setPickupOtp] = useState("");
  const [celebrating, setCelebrating] = useState(false);

  useEffect(() => {
    if (!open || !orderId) return;
    api.getRunnerOrderDetails(orderId).then(setDetails).catch(() => setDetails(null));
  }, [open, orderId]);

  if (!open || !orderId || !details) return null;

  const status = details.delivery_status || "pending";

  return (
    <div className="fixed inset-0 z-50 bg-black/55 flex items-end md:items-center justify-center">
      <div className="w-full max-w-3xl max-h-[95vh] overflow-y-auto rounded-t-3xl md:rounded-3xl bg-white shadow-2xl">
        <div className={`sticky top-0 z-10 flex items-center justify-between px-6 py-4 text-white ${celebrating ? "bg-gradient-to-r from-emerald-500 to-green-600" : previewOnly ? "bg-gradient-to-r from-orange-500 to-red-500" : "bg-gradient-to-r from-green-500 to-emerald-600"}`}>
          <div>
            <h3 className="text-2xl font-bold">{celebrating ? "Delivery Complete!" : previewOnly ? `Order ${details.token_number} Details` : `Active Delivery — ${details.token_number}`}</h3>
            {!celebrating && <p className="text-sm text-white/85 mt-1">Placed {new Date(details.placed_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</p>}
          </div>
          <button type="button" onClick={onClose} className="rounded-full bg-white/15 p-2">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6">
          {celebrating ? (
            <div className="py-12 text-center">
              <div className="text-6xl mb-4">🎉</div>
              <p className="text-3xl font-bold text-gray-900">Order delivered successfully</p>
              <p className="mt-3 text-lg text-green-600 font-semibold">You earned +{details.runner_reward_points} points</p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="rounded-2xl border border-orange-100 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-orange-500 font-semibold">Pickup</p>
                  <p className="mt-2 text-lg font-bold text-gray-900">Counter {details.counter_number}</p>
                  <p className="text-sm text-gray-500">{details.counter_name}</p>
                </div>
                <div className="rounded-2xl border border-orange-100 p-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-orange-500 font-semibold">Deliver To</p>
                  <p className="mt-2 text-lg font-bold text-gray-900">{details.delivery_address?.full_address}</p>
                  <p className="text-sm text-gray-500">{details.customer_name}</p>
                </div>
              </div>

              <div className="mt-5 rounded-2xl border border-gray-100 p-4">
                <p className="font-semibold text-gray-900 mb-3">Order Items</p>
                <div className="space-y-3">
                  {details.items?.map((item: any) => (
                    <div key={`${item.food_id}-${item.name}`} className="flex items-center gap-3">
                      <ImageWithFallback src={getFoodImageUrl(item.image_url, item.category)} alt={item.name} className="h-14 w-14 rounded-xl object-cover" />
                      <div className="flex-1">
                        <p className="font-semibold text-gray-900">{item.name} × {item.quantity}</p>
                        {item.customizations && <p className="text-sm text-gray-500">{item.customizations}</p>}
                      </div>
                      <span className="font-semibold text-gray-900">₹{item.subtotal}</span>
                    </div>
                  ))}
                </div>
                {details.special_instructions && (
                  <div className="mt-4 rounded-xl bg-amber-50 px-4 py-3 text-amber-800 text-sm">
                    {details.special_instructions}
                  </div>
                )}
              </div>

              <div className="mt-5 rounded-2xl border border-gray-100 p-4">
                <p className="font-semibold text-gray-900 mb-3">Payment</p>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between"><span>Subtotal</span><span>₹{details.subtotal}</span></div>
                  <div className="flex justify-between"><span>Delivery Fee</span><span>₹{details.delivery_fee}</span></div>
                  <div className="flex justify-between"><span>Tax</span><span>₹{details.tax}</span></div>
                  <div className="flex justify-between font-bold text-gray-900 pt-2 border-t"><span>Total</span><span>₹{details.total_amount}</span></div>
                  <div className="flex justify-between"><span>Payment</span><span>{details.payment_method} • {details.payment_status}</span></div>
                </div>
              </div>

              {previewOnly && (
                <button
                  type="button"
                  onClick={async () => {
                    const response = await api.acceptOrder(orderId);
                    const refreshed = await api.getRunnerOrderDetails(orderId);
                    setDetails(refreshed);
                    onAccepted?.(response);
                  }}
                  className="mt-6 w-full rounded-2xl bg-gradient-to-r from-orange-500 to-red-500 px-5 py-4 text-white font-semibold"
                >
                  Accept & Deliver
                </button>
              )}

              {!previewOnly && (
                <div className="mt-6 space-y-4">
                  <div className="rounded-2xl border border-green-100 bg-green-50 p-4">
                    <p className="text-sm font-semibold text-green-800">Pickup OTP</p>
                    <p className="mt-2 text-4xl font-bold tracking-[0.5em] text-green-700">{details.pickup_otp}</p>
                  </div>

                  {status === "assigned" && (
                    <div className="space-y-3">
                      <input value={pickupOtp} onChange={(e) => setPickupOtp(e.target.value)} maxLength={4} placeholder="Enter pickup OTP" className="w-full rounded-xl border border-gray-200 px-4 py-3" />
                      <button type="button" onClick={async () => {
                        await api.updateRunnerDeliveryStatus(details.delivery_id, "picked_up", pickupOtp);
                        setDetails(await api.getRunnerOrderDetails(orderId));
                      }} className="w-full rounded-2xl bg-gradient-to-r from-green-500 to-emerald-600 px-4 py-3 text-white font-semibold">
                        I've Picked Up the Order
                      </button>
                    </div>
                  )}

                  {(status === "picked_up" || status === "on_the_way") && (
                    <div className="space-y-3">
                      <div className="rounded-2xl border border-blue-100 p-4">
                        <p className="font-semibold text-gray-900">{details.delivery_address?.full_address}</p>
                        {details.customer_phone && (
                          <a href={`tel:${details.customer_phone}`} className="mt-2 inline-flex items-center gap-2 text-blue-600">
                            <PhoneCall className="w-4 h-4" />
                            {details.customer_phone}
                          </a>
                        )}
                      </div>
                      {status === "picked_up" && (
                        <button type="button" onClick={async () => {
                          await api.updateRunnerDeliveryStatus(details.delivery_id, "on_the_way");
                          setDetails(await api.getRunnerOrderDetails(orderId));
                        }} className="w-full rounded-2xl bg-gradient-to-r from-sky-500 to-indigo-600 px-4 py-3 text-white font-semibold">
                          Mark On The Way
                        </button>
                      )}
                      <input value={deliveryOtp} onChange={(e) => setDeliveryOtp(e.target.value)} maxLength={4} placeholder="Enter delivery OTP" className="w-full rounded-xl border border-gray-200 px-4 py-3" />
                      <button type="button" onClick={async () => {
                        await api.updateRunnerDeliveryStatus(details.delivery_id, "delivered", deliveryOtp);
                        setCelebrating(true);
                        onDelivered?.(details.runner_reward_points);
                      }} className="w-full rounded-2xl bg-gradient-to-r from-orange-500 to-amber-500 px-4 py-3 text-white font-semibold">
                        Confirm Delivery
                      </button>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
