import { Award, Gift, TrendingUp, Star, Lock } from "lucide-react";
import { useState, useEffect } from "react";
import { rewards } from "../data/mockData";
import { ImageWithFallback } from "../components/figma/ImageWithFallback";
import { api } from "../services/api";

export function Rewards() {
  const [currentPoints, setCurrentPoints] = useState(0);
  const [totalOrders, setTotalOrders] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [redeemingId, setRedeemingId] = useState<number | null>(null);
  useEffect(() => {
    fetchRewardData();
  }, []);

  const fetchRewardData = async () => {
    try {
      setIsLoading(true);
      const [pointsRes, ordersRes] = await Promise.all([
        api.getMyPoints().catch(() => null),
        api.getMyOrders().catch(() => null),
      ]);

      if (pointsRes?.points_balance !== undefined) {
        setCurrentPoints(pointsRes.points_balance);
      }

      if (ordersRes?.orders) {
        const orderCount = ordersRes.orders.length;
        setTotalOrders(orderCount);
        
        // Give 1 point per order + 5 bonus points on first order
        const calculatedPoints = (orderCount * 1) + (orderCount > 0 ? 5 : 0);
        
        // Only update if we need to sync (backend might already have it)
        if (pointsRes?.points_balance === 0 && orderCount > 0) {
          setCurrentPoints(calculatedPoints);
        }
      }
    } catch (error) {
      console.error("Error fetching reward data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRedeem = async (reward: any) => {
    try {
      setRedeemingId(reward.id);
      const response = await api.redeemPoints(reward.pointsRequired);
      
      if (response && response.message) {
        // Update points after successful redemption
        setCurrentPoints(prev => Math.max(0, prev - reward.pointsRequired));
        alert(`Successfully redeemed: ${reward.name}`);
      }
    } catch (error) {
      console.error("Error redeeming reward:", error);
      alert("Failed to redeem reward. Please try again.");
    } finally {
      setRedeemingId(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl text-gray-900 mb-2">Rewards</h1>
        <p className="text-gray-600">Redeem your points for exclusive rewards</p>
      </div>

      {/* Points Card */}
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
              <p className="text-sm text-purple-100">Orders</p>
              <p className="text-xl">{totalOrders}</p>
            </div>
            <div>
              <p className="text-sm text-purple-100">Points/Order</p>
              <p className="text-xl">1 pt</p>
            </div>
            <div>
              <p className="text-sm text-purple-100">Bonus</p>
              <p className="text-xl">{totalOrders > 0 ? "5 pts" : "0 pts"}</p>
            </div>
          </div>
        </div>
      </div>

      {/* How to Earn Points */}
      <div className="bg-purple-50 border border-purple-200 rounded-xl p-6 mb-8">
        <h3 className="text-lg text-gray-900 mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-purple-600" />
          How to Earn Points
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mb-3">
              <Gift className="w-5 h-5 text-purple-600" />
            </div>
            <h4 className="text-gray-900 mb-1">Place Orders</h4>
            <p className="text-sm text-gray-600">Get 1 point per order + 5 bonus on first order</p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mb-3">
              <Star className="w-5 h-5 text-purple-600" />
            </div>
            <h4 className="text-gray-900 mb-1">Deliver Orders</h4>
            <p className="text-sm text-gray-600">Get 10% of order value + bonus on first delivery</p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mb-3">
              <Award className="w-5 h-5 text-purple-600" />
            </div>
            <h4 className="text-gray-900 mb-1">Unlock Rewards</h4>
            <p className="text-sm text-gray-600">Complete your 1st order to unlock all rewards</p>
          </div>
        </div>
      </div>

      {/* Rewards Grid */}
      <div>
        <h2 className="text-2xl text-gray-900 mb-6">Available Rewards</h2>
        {totalOrders === 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-8">
            <div className="flex items-center gap-3">
              <Lock className="w-5 h-5 text-blue-600" />
              <div>
                <p className="text-blue-900 font-semibold">Rewards Locked</p>
                <p className="text-sm text-blue-700">Complete your first order to unlock all rewards!</p>
              </div>
            </div>
          </div>
        )}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {rewards.map((reward) => {
            const isLocked = totalOrders === 0;
            const canRedeem = !isLocked && currentPoints >= reward.pointsRequired;
            
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
                    src={reward.image}
                    alt={reward.name}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-3 right-3 bg-white rounded-full px-3 py-1 shadow-lg">
                    <span className="text-sm text-orange-600">
                      {reward.pointsRequired} pts
                    </span>
                  </div>
                  {!isLocked && !canRedeem && (
                    <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
                      <div className="bg-white rounded-lg px-4 py-2">
                        <p className="text-sm">
                          Need {reward.pointsRequired - currentPoints} more points
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                <div className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-lg text-gray-900">{reward.name}</h3>
                    <span className="bg-orange-100 text-orange-700 text-xs px-2 py-1 rounded-full">
                      {reward.category}
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
