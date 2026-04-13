import { Award, Gift, Lock, Star, TrendingUp } from "lucide-react";
import { useEffect, useState } from "react";
import { ImageWithFallback } from "../components/figma/ImageWithFallback";
import { api } from "../services/api";

export function Rewards() {
  const [currentPoints, setCurrentPoints] = useState(0);
  const [totalOrders, setTotalOrders] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [redeemingId, setRedeemingId] = useState<string | null>(null);
  const [rewardItems, setRewardItems] = useState<any[]>([]);
  const [redeemedCoupons, setRedeemedCoupons] = useState<any[]>([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const refresh = () => {
      fetchRewardData();
    };
    fetchRewardData();
    window.addEventListener("rewards:refresh", refresh);
    window.addEventListener("focus", refresh);
    return () => {
      window.removeEventListener("rewards:refresh", refresh);
      window.removeEventListener("focus", refresh);
    };
  }, []);

  const fetchRewardData = async () => {
    try {
      setIsLoading(true);
      const [pointsRes, ordersRes, rewardsRes, redeemedRes] = await Promise.all([
        api.getMyPoints().catch(() => null),
        api.getMyOrders().catch(() => null),
        api.getAvailableRewards().catch(() => null),
        api.getRedeemedVouchers().catch(() => null),
      ]);

      setCurrentPoints(pointsRes?.points_balance ?? 0);
      setTotalOrders((ordersRes?.orders || []).filter((order: any) => order.status === "delivered").length);
      setRewardItems(rewardsRes?.vouchers || rewardsRes?.rewards || []);
      setRedeemedCoupons((redeemedRes?.vouchers || []).filter((voucher: any) => !voucher.is_used));
    } catch (error) {
      console.error("Error fetching reward data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRedeem = async (reward: any) => {
    try {
      setRedeemingId(reward.id);
      const response = await api.redeemPoints(reward.points_required ?? reward.pointsRequired, reward.id);
      if (response?.message) {
        setMessage(
          response.voucher_code
            ? `${reward.name} redeemed. Use coupon ${response.voucher_code} at checkout.`
            : `Successfully redeemed: ${reward.name}`,
        );
        await fetchRewardData();
      }
    } catch (error) {
      console.error("Error redeeming reward:", error);
      setMessage("Failed to redeem reward. Please try again.");
    } finally {
      setRedeemingId(null);
      window.setTimeout(() => setMessage(""), 4000);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div className="mb-8">
        <h1 className="text-3xl text-gray-900 mb-2">Rewards</h1>
        <p className="text-gray-600">Redeem your live points balance for usable checkout coupons.</p>
      </div>

      <div className="bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl p-8 mb-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-purple-100 mb-2">Your Points Balance</p>
            <div className="flex items-baseline gap-3">
              <span className="text-5xl">{isLoading ? "..." : currentPoints}</span>
              <span className="text-2xl text-purple-100">points</span>
            </div>
          </div>
          <Award className="w-16 h-16 text-purple-100" />
        </div>

        <div className="mt-6 pt-6 border-t border-purple-400/30">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-purple-100">Delivered Orders</p>
              <p className="text-xl">{totalOrders}</p>
            </div>
            <div>
              <p className="text-sm text-purple-100">Points Source</p>
              <p className="text-xl">Live DB</p>
            </div>
            <div>
              <p className="text-sm text-purple-100">Rewards Status</p>
              <p className="text-xl">{currentPoints > 0 ? "Ready" : "Locked"}</p>
            </div>
          </div>
        </div>
      </div>

      {message && (
        <div className="mb-6 rounded-xl border border-orange-200 bg-orange-50 px-4 py-3 text-sm text-orange-700">
          {message}
        </div>
      )}

      <div className="bg-purple-50 border border-purple-200 rounded-xl p-6 mb-8">
        <h3 className="text-lg text-gray-900 mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-purple-600" />
          How Rewards Work
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mb-3">
              <Gift className="w-5 h-5 text-purple-600" />
            </div>
            <h4 className="text-gray-900 mb-1">Earn Points</h4>
            <p className="text-sm text-gray-600">Points update from the real backend ledger as your orders and deliveries finish.</p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mb-3">
              <Star className="w-5 h-5 text-purple-600" />
            </div>
            <h4 className="text-gray-900 mb-1">Redeem Rewards</h4>
            <p className="text-sm text-gray-600">Redeeming creates a real coupon code you can apply on the checkout page.</p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mb-3">
              <Award className="w-5 h-5 text-purple-600" />
            </div>
            <h4 className="text-gray-900 mb-1">Use Coupons</h4>
            <p className="text-sm text-gray-600">Unused redeemed coupons automatically appear in checkout until they are consumed.</p>
          </div>
        </div>
      </div>

      <div>
        {redeemedCoupons.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl text-gray-900 mb-4">Ready To Use At Checkout</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {redeemedCoupons.map((coupon) => (
                <div key={coupon.code} className="rounded-2xl border border-green-100 bg-green-50 p-5">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-lg font-bold text-gray-900">{coupon.name}</p>
                      <p className="mt-1 text-sm text-gray-600">
                        {coupon.discount_type === "delivery"
                          ? `Free delivery up to ₹${coupon.discount_value}`
                          : `₹${coupon.discount_value} off your next eligible order`}
                      </p>
                    </div>
                    <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-green-700">
                      Active
                    </span>
                  </div>
                  <div className="mt-4 rounded-xl border border-green-200 bg-white px-4 py-3">
                    <p className="text-xs uppercase tracking-[0.2em] text-gray-500">Coupon Code</p>
                    <p className="mt-1 font-mono text-lg font-bold text-gray-900">{coupon.code}</p>
                  </div>
                  <p className="mt-3 text-xs text-green-700">This coupon will appear in checkout until you use it.</p>
                </div>
              ))}
            </div>
          </div>
        )}

        <h2 className="text-2xl text-gray-900 mb-6">Available Rewards</h2>
        {totalOrders === 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-8">
            <div className="flex items-center gap-3">
              <Lock className="w-5 h-5 text-blue-600" />
              <div>
                <p className="text-blue-900 font-semibold">Rewards Locked</p>
                <p className="text-sm text-blue-700">Complete your first delivered order to start earning and redeeming points.</p>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {rewardItems.map((reward) => {
            const isLocked = totalOrders === 0;
            const pointsRequired = reward.points_required ?? reward.pointsRequired ?? 0;
            const canRedeem = !isLocked && currentPoints >= pointsRequired;

            return (
              <div
                key={reward.id}
                className={`bg-white rounded-xl shadow-md overflow-hidden transition-all ${
                  isLocked ? "opacity-40 grayscale" : canRedeem ? "hover:shadow-xl" : ""
                }`}
              >
                <div className="relative h-48 overflow-hidden">
                  {isLocked && (
                    <div className="absolute inset-0 bg-black/30 flex items-center justify-center z-10">
                      <Lock className="w-12 h-12 text-white" />
                    </div>
                  )}
                  <ImageWithFallback
                    src={reward.image || "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop"}
                    alt={reward.name}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-3 right-3 bg-white rounded-full px-3 py-1 shadow-lg">
                    <span className="text-sm text-orange-600">{pointsRequired} pts</span>
                  </div>
                  {!isLocked && !canRedeem && (
                    <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
                      <div className="bg-white rounded-lg px-4 py-2">
                        <p className="text-sm">Need {pointsRequired - currentPoints} more points</p>
                      </div>
                    </div>
                  )}
                </div>

                <div className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-lg text-gray-900">{reward.name}</h3>
                    <span className="bg-orange-100 text-orange-700 text-xs px-2 py-1 rounded-full">
                      {reward.category || "Reward"}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-4">{reward.description}</p>

                  {isLocked ? (
                    <button
                      disabled
                      className="w-full bg-gray-200 text-gray-500 cursor-not-allowed py-3 rounded-lg transition-colors"
                    >
                      Locked - Complete 1st Order
                    </button>
                  ) : (
                    <button
                      onClick={() => handleRedeem(reward)}
                      disabled={!canRedeem || redeemingId === reward.id}
                      className={`w-full py-3 rounded-lg transition-colors ${
                        canRedeem
                          ? redeemingId === reward.id
                            ? "bg-gray-400 text-white cursor-wait"
                            : "bg-orange-500 hover:bg-orange-600 text-white"
                          : "bg-gray-200 text-gray-500 cursor-not-allowed"
                      }`}
                    >
                      {redeemingId === reward.id ? "Redeeming..." : canRedeem ? "Redeem Now" : "Not Enough Points"}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
