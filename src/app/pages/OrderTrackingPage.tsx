import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router";
import { PhoneCall } from "lucide-react";
import confetti from "canvas-confetti";
import { useOrderTracking } from "../hooks/useOrderTracking";
import { RateOrderSheet } from "../components/RateOrderSheet";
import { StarRating } from "../components/StarRating";
import { api } from "../services/api";

export function OrderTrackingPage() {
  const { id = "" } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const initialTracking = useMemo(() => {
    const state = location.state as any;
    if (!state) return null;
    return {
      order_id: state.order_id,
      token_number: state.token_number,
      delivery_otp: state.delivery_otp,
      pickup_otp: state.pickup_otp,
      total_amount: state.total,
      items: state.items,
      timeline: [],
    };
  }, [location.state]);
  const tracking = useOrderTracking(id, initialTracking);
  const [ratingOpen, setRatingOpen] = useState(false);
  const [runnerRating, setRunnerRating] = useState<number>(0);
  const [runnerReview, setRunnerReview] = useState("");
  const [runnerSubmitting, setRunnerSubmitting] = useState(false);
  const [runnerRated, setRunnerRated] = useState(false);

  useEffect(() => {
    if (tracking?.delivery_review?.rating) {
      setRunnerRating(Number(tracking.delivery_review.rating));
      setRunnerReview(tracking.delivery_review.review || "");
      setRunnerRated(true);
    }
  }, [tracking?.delivery_review?.rating, tracking?.delivery_review?.review]);

  useEffect(() => {
    // If we have items in state, we just arrived from checkout
    if (location.state?.items) {
      setTimeout(() => {
        confetti({
          particleCount: 150,
          spread: 70,
          origin: { y: 0.6 },
          colors: ['#f97316', '#3b82f6', '#10b981', '#fcd34d']
        });
      }, 300);
      
      // Replace state to avoid re-triggering on refresh
      navigate(".", { replace: true, state: {} });
    }
  }, [location.state, navigate]);

  if (!tracking) {
    return <div className="max-w-4xl mx-auto px-4 py-12 text-gray-500">Loading order tracking...</div>;
  }

  const handleRunnerRating = async () => {
    if (!tracking.delivery_id || runnerRating < 1) return;
    try {
      setRunnerSubmitting(true);
      await api.rateDelivery(tracking.delivery_id, runnerRating, runnerReview.trim());
      setRunnerRated(true);
    } finally {
      setRunnerSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <button type="button" onClick={() => navigate("/orders")} className="text-orange-600 font-semibold mb-4">← Back to Orders</button>
      <div className="rounded-3xl bg-white shadow-xl border border-orange-100 overflow-hidden">
        <div className="bg-gradient-to-r from-orange-500 to-amber-500 p-6 text-white">
          <h1 className="text-3xl font-bold">Order {tracking.token_number}</h1>
          <p className="mt-2 text-orange-50">Track your order in real time</p>
        </div>
        <div className="p-6 space-y-6">
          <div>
            <p className="font-semibold text-gray-900 mb-4">Order Status Timeline</p>
            <div className="space-y-4">
              {tracking.timeline?.map((step: any) => (
                <div key={step.status} className="flex gap-4">
                  <div className={`mt-1 h-4 w-4 rounded-full ${step.done ? "bg-green-500" : tracking.status === step.status ? "bg-orange-500 animate-pulse" : "bg-gray-200"}`} />
                  <div>
                    <p className="font-semibold text-gray-900">{step.label}</p>
                    <p className="text-sm text-gray-500">{step.time || (tracking.status === step.status ? "Live..." : "Pending")}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {tracking.runner && (
            <div className="rounded-2xl border border-orange-100 p-4">
              <p className="font-semibold text-gray-900 mb-3">Your Runner</p>
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="font-semibold text-gray-900">{tracking.runner.name}</p>
                  <p className="text-sm text-gray-500">⭐ {tracking.runner.rating} • {tracking.runner.completed_deliveries} deliveries</p>
                </div>
                {tracking.runner.phone && (
                  <a href={`tel:${tracking.runner.phone}`} className="inline-flex items-center gap-2 rounded-xl bg-green-500 px-4 py-2 text-white">
                    <PhoneCall className="w-4 h-4" />
                    Call
                  </a>
                )}
              </div>
            </div>
          )}

          {tracking.delivery_otp && (
            <div className="rounded-2xl border border-blue-100 bg-blue-50 p-4">
              <p className="font-semibold text-blue-900">Your Delivery OTP</p>
              <p className="mt-2 text-4xl font-bold tracking-[0.5em] text-blue-700">{tracking.delivery_otp}</p>
            </div>
          )}

          <div className="rounded-2xl border border-gray-100 p-4">
            <p className="font-semibold text-gray-900 mb-3">Order Summary</p>
            <div className="space-y-2 text-sm">
              {tracking.items?.map((item: any) => (
                <div key={`${item.food_id}-${item.id || item.food_name}`} className="flex justify-between">
                  <span>{item.food_name} × {item.quantity}</span>
                  <span>₹{item.total_price}</span>
                </div>
              ))}
              <div className="flex justify-between pt-2 border-t font-semibold">
                <span>Total</span>
                <span>₹{tracking.total_amount}</span>
              </div>
            </div>
          </div>

          {tracking.status === "delivered" && (
            <div className="space-y-4">
              {tracking.runner && (
                <div className="rounded-2xl border border-green-100 bg-green-50 p-5">
                  <p className="text-lg font-bold text-gray-900">Rate your runner</p>
                  <p className="mt-1 text-sm text-gray-600">
                    {tracking.runner.name} delivered your order. Your feedback helps keep runner quality high.
                  </p>
                  <div className="mt-4">
                    <StarRating value={runnerRating} onChange={runnerRated ? undefined : setRunnerRating} readonly={runnerRated} size={24} />
                  </div>
                  <textarea
                    value={runnerReview}
                    onChange={(event) => setRunnerReview(event.target.value)}
                    disabled={runnerRated}
                    placeholder="Optional note for the runner..."
                    className="mt-4 w-full rounded-2xl border border-green-200 bg-white px-4 py-3 text-sm text-gray-700 focus:outline-none focus:border-green-400 disabled:bg-green-100"
                    rows={3}
                  />
                  {runnerRated ? (
                    <p className="mt-3 text-sm font-semibold text-green-700">Thanks for rating your runner.</p>
                  ) : (
                    <button
                      type="button"
                      onClick={handleRunnerRating}
                      disabled={runnerSubmitting || runnerRating < 1}
                      className="mt-4 rounded-xl bg-green-500 px-4 py-3 text-white font-semibold disabled:opacity-60"
                    >
                      {runnerSubmitting ? "Submitting..." : "Submit Runner Rating"}
                    </button>
                  )}
                </div>
              )}

              <div className="rounded-2xl border border-orange-100 bg-orange-50 p-5">
                <p className="text-xl font-bold text-gray-900">Delivered! How was your order?</p>
                <button type="button" onClick={() => setRatingOpen(true)} className="mt-4 rounded-xl bg-orange-500 px-4 py-3 text-white font-semibold">
                  Rate Food Items
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      <RateOrderSheet orderId={id} open={ratingOpen} onClose={() => setRatingOpen(false)} />
    </div>
  );
}
