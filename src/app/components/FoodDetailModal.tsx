import { useEffect, useMemo, useState } from "react";
import { Flame, Minus, Plus, X } from "lucide-react";
import { api } from "../services/api";
import { useCart } from "../context/CartContext";
import { StarRating } from "./StarRating";

interface FoodDetailModalProps {
  foodId: string | null;
  open: boolean;
  onClose: () => void;
}

export function FoodDetailModal({ foodId, open, onClose }: FoodDetailModalProps) {
  const { addToCart, cart } = useCart();
  const [food, setFood] = useState<any>(null);
  const [quantity, setQuantity] = useState(1);
  const [spiceLevel, setSpiceLevel] = useState("Medium");

  useEffect(() => {
    if (!open || !foodId) return;
    api.getFoodDetail(foodId).then(setFood).catch(() => setFood(null));
  }, [foodId, open]);

  const existingCartItem = useMemo(
    () => cart?.items.find((item) => item.food_id === foodId),
    [cart?.items, foodId],
  );

  if (!open || !foodId || !food) return null;

  const totalRatings = Object.values(food.rating_distribution || {}).reduce((sum: number, count: any) => sum + Number(count || 0), 0) || 1;

  return (
    <div className="fixed inset-0 z-50 flex items-end md:items-center justify-center bg-black/50">
      <div className="w-full max-w-4xl max-h-[92vh] overflow-y-auto rounded-t-3xl md:rounded-3xl bg-white shadow-2xl">
        <div className="relative">
          <img src={food.image_url} alt={food.name} className="h-64 w-full object-cover" />
          <button type="button" onClick={onClose} className="absolute top-4 right-4 rounded-full bg-white/90 p-2">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
            <div>
              <div className="inline-flex rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-700">
                {food.is_veg ? "VEG" : "NON VEG"}
              </div>
              <h2 className="mt-3 text-3xl font-bold text-gray-900">{food.name}</h2>
              <p className="mt-2 text-gray-600">{food.description}</p>
              <div className="mt-3 flex flex-wrap gap-4 text-sm text-gray-500">
                <span>⭐ {food.rating} ({food.rating_count} reviews)</span>
                <span>⏱️ {food.prep_time_mins || food.prep_time} min</span>
                <span>{food.counter_name || "Main Counter"}</span>
              </div>
            </div>
            <div className="text-3xl font-bold text-orange-600">₹{food.price}</div>
          </div>

          <div className="mt-6">
            <p className="text-sm font-semibold text-gray-900 mb-3">Ingredients</p>
            <div className="flex flex-wrap gap-2">
              {(food.ingredients || []).map((ingredient: string) => (
                <span key={ingredient} className="rounded-full bg-orange-50 px-3 py-1 text-sm text-orange-700">
                  {ingredient}
                </span>
              ))}
            </div>
          </div>

          <div className="mt-6 flex items-center gap-2 rounded-2xl bg-amber-50 px-4 py-3 text-amber-700">
            <Flame className="w-5 h-5" />
            <span>{food.calories || 0} kcal</span>
          </div>

          <div className="mt-6">
            <p className="text-sm font-semibold text-gray-900 mb-3">Customise Spice Level</p>
            <div className="inline-flex rounded-2xl bg-gray-100 p-1">
              {["Mild", "Medium", "Spicy"].map((level) => (
                <button
                  key={level}
                  type="button"
                  onClick={() => setSpiceLevel(level)}
                  className={`rounded-xl px-4 py-2 text-sm font-semibold ${spiceLevel === level ? "bg-white text-orange-600 shadow-sm" : "text-gray-500"}`}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>

          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p className="text-sm font-semibold text-gray-900 mb-3">Ratings Breakdown</p>
              <div className="space-y-2">
                {[5, 4, 3, 2, 1].map((star) => {
                  const count = Number(food.rating_distribution?.[String(star)] || 0);
                  return (
                    <div key={star} className="flex items-center gap-3 text-sm">
                      <span className="w-6">{star}★</span>
                      <div className="h-2 flex-1 rounded-full bg-gray-100 overflow-hidden">
                        <div className="h-full bg-orange-500 transition-all duration-700" style={{ width: `${(count / totalRatings) * 100}%` }} />
                      </div>
                      <span className="w-8 text-right text-gray-500">{count}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div>
              <p className="text-sm font-semibold text-gray-900 mb-3">Reviews</p>
              <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
                {(food.reviews || []).map((review: any) => (
                  <div key={review.review_id} className="rounded-2xl border border-gray-100 p-3">
                    <div className="flex items-center gap-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-orange-100 font-semibold text-orange-700">
                        {review.user_initial}
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900">{review.user_name}</p>
                        <StarRating value={review.rating} readonly size={16} />
                      </div>
                    </div>
                    {review.comment && <p className="mt-2 text-sm text-gray-600">{review.comment}</p>}
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-8 flex items-center justify-between rounded-2xl border border-orange-100 px-4 py-4">
            <div className="flex items-center gap-3">
              <button type="button" onClick={() => setQuantity((q) => Math.max(1, q - 1))} className="rounded-xl bg-gray-100 p-2"><Minus className="w-4 h-4" /></button>
              <span className="w-8 text-center font-semibold">{quantity}</span>
              <button type="button" onClick={() => setQuantity((q) => q + 1)} className="rounded-xl bg-gray-100 p-2"><Plus className="w-4 h-4" /></button>
            </div>
            <button
              type="button"
              onClick={async () => {
                await addToCart(food.id, quantity, `Spice level: ${spiceLevel}`);
                onClose();
              }}
              className="rounded-2xl bg-gradient-to-r from-orange-500 to-amber-500 px-5 py-3 text-white font-semibold"
            >
              {existingCartItem ? `Add More ₹${(food.price * quantity).toFixed(0)}` : `Add to Cart ₹${(food.price * quantity).toFixed(0)}`}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
