import { useEffect, useState } from "react";
import { X, Star } from "lucide-react";
import { api } from "../services/api";
import { StarRating } from "./StarRating";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import { getFoodImageUrl } from "../utils/foodImages";

interface RateOrderSheetProps {
  orderId: string | null;
  deliveryId?: string | null;
  open: boolean;
  onClose: () => void;
  onSubmitted?: () => void;
}

export function RateOrderSheet({ orderId, deliveryId, open, onClose, onSubmitted }: RateOrderSheetProps) {
  const [items, setItems] = useState<any[]>([]);
  const [ratings, setRatings] = useState<Record<string, number>>({});
  const [comments, setComments] = useState<Record<string, string>>({});
  const [runnerRating, setRunnerRating] = useState(0);
  const [runnerComment, setRunnerComment] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    if (!open || !orderId) return;
    setSubmitError("");
    setSuccessMessage("");
    setRatings({});
    setComments({});
    setRunnerRating(0);
    setRunnerComment("");
    api.getReviewableItems(orderId).then((response) => setItems(response.items || [])).catch(() => setItems([]));
  }, [open, orderId]);

  if (!open || !orderId) return null;

  const submitAll = async () => {
    const selectedItems = items.filter((item) => ratings[item.food_id]);
    if (selectedItems.length === 0 && runnerRating === 0) {
      setSubmitError("Please rate at least one item or the runner before submitting.");
      return;
    }

    setIsSubmitting(true);
    try {
      setSubmitError("");
      // Submit food reviews
      for (const item of selectedItems) {
        await api.submitReview({
          order_id: orderId,
          food_id: item.food_id,
          rating: ratings[item.food_id],
          comment: comments[item.food_id] || "",
        });
      }
      // Submit runner rating if provided
      if (runnerRating > 0 && deliveryId) {
        await api.rateDelivery(deliveryId, runnerRating, runnerComment);
      }
      setSuccessMessage("Thanks for your review! Your ratings were saved.");
      onSubmitted?.();
      window.setTimeout(() => onClose(), 900);
    } catch (error: any) {
      setSubmitError(error.message || "Could not submit your ratings.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end md:items-center justify-center bg-black/45">
      <div className="w-full max-w-2xl rounded-t-3xl md:rounded-3xl bg-white p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-2xl font-bold text-gray-900">Rate Your Order</h3>
            <p className="text-sm text-gray-500 mt-1">Tell us how everything went.</p>
          </div>
          <button type="button" onClick={onClose} className="p-2 rounded-lg hover:bg-gray-100">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Runner Rating Section */}
        {deliveryId && (
          <div className="mb-6 rounded-2xl border border-blue-100 bg-blue-50 p-4">
            <div className="flex items-center gap-2 mb-3">
              <Star className="w-5 h-5 text-blue-600" />
              <p className="font-semibold text-gray-900">Rate Your Runner</p>
            </div>
            <p className="text-sm text-gray-600 mb-3">How was your delivery experience?</p>
            <StarRating
              value={runnerRating}
              onChange={(value) => setRunnerRating(value)}
            />
            {runnerRating > 0 && (
              <textarea
                rows={2}
                placeholder="Any feedback for the runner? (optional)"
                value={runnerComment}
                onChange={(e) => setRunnerComment(e.target.value)}
                className="mt-3 w-full rounded-xl border border-blue-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-200"
              />
            )}
          </div>
        )}

        {/* Food Item Ratings */}
        <div className="space-y-5">
          {items.length > 0 && (
            <p className="text-sm font-semibold text-gray-700 uppercase tracking-wider">Rate Each Item</p>
          )}
          {items.length === 0 && !deliveryId && (
            <div className="rounded-2xl border border-gray-100 bg-gray-50 p-4 text-sm text-gray-500">
              No reviewable items are available for this order yet.
            </div>
          )}
          {items.map((item) => (
            <div key={item.food_id} className="rounded-2xl border border-orange-100 p-4">
              <div className="flex items-center gap-3">
                <ImageWithFallback src={getFoodImageUrl(item.image_url, item.category)} alt={item.food_name} className="w-14 h-14 rounded-xl object-cover" />
                <div>
                  <p className="font-semibold text-gray-900">{item.food_name}</p>
                  <p className="text-sm text-gray-500">Qty {item.quantity}</p>
                </div>
              </div>
              <div className="mt-3">
                <StarRating value={ratings[item.food_id] || 0} onChange={(value) => setRatings((prev) => ({ ...prev, [item.food_id]: value }))} />
              </div>
              <textarea
                rows={2}
                placeholder="Write a review... optional"
                value={comments[item.food_id] || ""}
                onChange={(event) => setComments((prev) => ({ ...prev, [item.food_id]: event.target.value }))}
                className="mt-3 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-200"
              />
            </div>
          ))}
        </div>

        {submitError && <p className="mt-4 text-sm text-red-600">{submitError}</p>}
        {successMessage && <p className="mt-4 text-sm text-green-600">{successMessage}</p>}

        <button
          type="button"
          disabled={isSubmitting}
          onClick={submitAll}
          className="mt-6 w-full rounded-2xl bg-gradient-to-r from-orange-500 to-amber-500 px-4 py-3 text-white font-semibold disabled:opacity-60"
        >
          {isSubmitting ? "Submitting..." : "Submit Ratings"}
        </button>
      </div>
    </div>
  );
}
