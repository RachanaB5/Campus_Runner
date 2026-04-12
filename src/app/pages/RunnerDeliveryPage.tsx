import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router";
import { api } from "../services/api";

function OtpBoxes({ value }: { value: string }) {
  const digits = (value || "").split("").slice(0, 4);
  while (digits.length < 4) digits.push("");
  return (
    <div className="flex gap-3">
      {digits.map((digit, index) => (
        <div key={index} className="h-14 w-14 rounded-2xl border border-orange-200 bg-white flex items-center justify-center text-2xl font-bold text-orange-600">
          {digit}
        </div>
      ))}
    </div>
  );
}

export function RunnerDeliveryPage() {
  const { deliveryId = "" } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [details, setDetails] = useState<any>((location.state as any)?.details || null);
  const [deliveryOtp, setDeliveryOtp] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [pointsEarned, setPointsEarned] = useState(0);

  useEffect(() => {
    const orderId = (location.state as any)?.order?.id || (location.state as any)?.order_id;
    const load = async () => {
      try {
        const nextDetails = orderId
          ? await api.getRunnerOrderDetails(orderId)
          : await api.getRunnerDeliveryDetails(deliveryId);
        setDetails(nextDetails);
      } catch {
        setError("Could not load delivery details");
      }
    };
    if (deliveryId || orderId) {
      load();
    }
  }, [deliveryId, location.state]);

  const phase = useMemo(() => {
    if (!details) return "assigned";
    if (details.delivery_status === "delivered") return "delivered";
    if (details.delivery_status === "picked_up" || details.delivery_status === "on_the_way") return "picked_up";
    return "assigned";
  }, [details]);

  const handlePickedUp = async () => {
    if (!details) return;
    setIsSubmitting(true);
    setError("");
    try {
      await api.updateRunnerDeliveryStatus(details.delivery_id || deliveryId, "picked_up");
      const refreshed = await api.getRunnerDeliveryDetails(details.delivery_id || deliveryId);
      setDetails(refreshed);
    } catch (err: any) {
      setError(err.message || "Could not mark order as picked up");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelivered = async () => {
    if (!details) return;
    setIsSubmitting(true);
    setError("");
    try {
      await api.updateRunnerDeliveryStatus(details.delivery_id || deliveryId, "on_the_way");
      const response = await api.updateRunnerDeliveryStatus(details.delivery_id || deliveryId, "delivered", deliveryOtp);
      setPointsEarned(response.points_earned || 0);
      setDetails((previous: any) => ({
        ...(previous || {}),
        delivery_status: "delivered",
        runner_stats: {
          ...(previous?.runner_stats || {}),
          deliveries_made: Number(previous?.runner_stats?.deliveries_made || 0) + 1,
        },
      }));
    } catch (err: any) {
      setError(err.message || "Incorrect OTP. Ask customer to check their order screen.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!details) {
    return <div className="max-w-4xl mx-auto px-4 py-12 text-gray-500">Loading active delivery...</div>;
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <button type="button" onClick={() => navigate("/runner")} className="mb-4 text-orange-600 font-semibold">← Back to Runner Home</button>
      <div className="overflow-hidden rounded-3xl border border-orange-100 bg-white shadow-xl">
        <div className={`p-6 text-white ${phase === "delivered" ? "bg-gradient-to-r from-green-500 to-emerald-500" : "bg-gradient-to-r from-orange-500 to-amber-500"}`}>
          <h1 className="text-3xl font-bold">Active Delivery</h1>
          <p className="mt-2 text-white/90">Order {details.token_number} • Delivery {details.delivery_id || deliveryId}</p>
        </div>

        {phase === "assigned" && (
          <div className="p-6 space-y-6">
            <div>
              <p className="text-sm font-semibold text-gray-500">STEP 1 OF 3</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">Go to Counter</p>
            </div>
            <div className="rounded-2xl border border-orange-100 bg-orange-50 p-5">
              <p className="text-sm font-semibold text-gray-500">PICKUP LOCATION</p>
              <p className="mt-2 text-xl font-bold text-gray-900">Counter {details.counter_number} — {details.counter_name}</p>
              <p className="mt-4 text-sm font-semibold text-gray-500">SHOW THIS OTP TO STAFF</p>
              <div className="mt-3"><OtpBoxes value={details.pickup_otp || ""} /></div>
            </div>
            <div className="rounded-2xl border border-gray-100 p-5">
              <p className="font-semibold text-gray-900 mb-3">Order Items To Collect</p>
              <div className="space-y-3">
                {details.items?.map((item: any) => (
                  <div key={`${item.food_id}-${item.name}`} className="flex items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <img src={item.image_url} alt={item.name} className="h-14 w-14 rounded-xl object-cover" />
                      <div>
                        <p className="font-semibold text-gray-900">{item.name}</p>
                        <p className="text-sm text-gray-500">× {item.quantity} {item.customizations ? `• ${item.customizations}` : ""}</p>
                      </div>
                    </div>
                    <p className="font-semibold text-gray-900">₹{item.subtotal}</p>
                  </div>
                ))}
              </div>
              <div className="mt-4 border-t pt-4 text-sm text-gray-600">
                <p>Total: <span className="font-semibold text-gray-900">₹{details.total_amount}</span> • {String(details.payment_method || "").toUpperCase()} {details.payment_status === "paid" ? "Paid" : details.payment_status}</p>
                {details.special_instructions && <p className="mt-2">Special: {details.special_instructions}</p>}
                <p className="mt-2">You earn {details.runner_reward_points} pts on delivery.</p>
              </div>
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <button type="button" disabled={isSubmitting} onClick={handlePickedUp} className="w-full rounded-2xl bg-green-500 px-5 py-4 text-white font-bold disabled:opacity-60">
              {isSubmitting ? "Updating..." : "I've Picked Up the Order"}
            </button>
          </div>
        )}

        {phase === "picked_up" && (
          <div className="p-6 space-y-6">
            <div>
              <p className="text-sm font-semibold text-gray-500">STEP 2 OF 3</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">Deliver to Customer</p>
            </div>
            <div className="rounded-2xl border border-blue-100 bg-blue-50 p-5">
              <p className="text-sm font-semibold text-gray-500">DELIVER TO</p>
              <p className="mt-2 text-xl font-bold text-gray-900">{details.delivery_address?.full_address}</p>
              <p className="mt-4 text-gray-700">Customer: {details.customer_name}</p>
              {details.customer_phone && (
                <a href={`tel:${details.customer_phone}`} className="mt-3 inline-flex rounded-xl bg-green-500 px-4 py-2 text-white font-semibold">
                  Call: {details.customer_phone}
                </a>
              )}
            </div>
            <div className="rounded-2xl border border-gray-100 p-5">
              <p className="font-semibold text-gray-900 mb-3">Enter Delivery OTP From Customer</p>
              <input
                value={deliveryOtp}
                onChange={(event) => setDeliveryOtp(event.target.value.replace(/\D/g, "").slice(0, 4))}
                className="w-full rounded-2xl border border-gray-300 px-4 py-4 text-center text-3xl tracking-[0.8em] focus:outline-none focus:border-orange-400"
                placeholder="0000"
              />
              <p className="mt-3 text-sm text-gray-500">Ask the customer to show the OTP on their order tracking screen.</p>
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <button type="button" disabled={isSubmitting || deliveryOtp.length !== 4} onClick={handleDelivered} className="w-full rounded-2xl bg-orange-500 px-5 py-4 text-white font-bold disabled:opacity-60">
              {isSubmitting ? "Confirming..." : "Confirm Delivery"}
            </button>
          </div>
        )}

        {phase === "delivered" && (
          <div className="p-10 text-center">
            <div className="mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-green-100 text-5xl">🎉</div>
            <h2 className="mt-6 text-3xl font-bold text-gray-900">Delivery Complete!</h2>
            <p className="mt-2 text-gray-600">Order {details.token_number} was delivered successfully.</p>
            <div className="mx-auto mt-6 max-w-md rounded-3xl border border-green-100 bg-green-50 p-6 text-left">
              <p className="text-2xl font-bold text-green-700">+{pointsEarned || details.runner_reward_points} Points Earned</p>
              <p className="mt-2 text-gray-600">All-time deliveries: {details.runner_stats?.deliveries_made || "Updated in profile"}</p>
            </div>
            <button type="button" onClick={() => navigate("/runner")} className="mt-8 rounded-2xl bg-orange-500 px-6 py-4 text-white font-bold">
              Back to Runner Home
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
