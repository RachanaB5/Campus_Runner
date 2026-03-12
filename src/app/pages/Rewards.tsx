import { Award, Gift, TrendingUp, Star } from "lucide-react";
import { rewards } from "../data/mockData";
import { ImageWithFallback } from "../components/figma/ImageWithFallback";

export function Rewards() {
  const currentPoints = 245;

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
              <span className="text-5xl">{currentPoints}</span>
              <span className="text-2xl text-purple-100">points</span>
            </div>
          </div>
          <Award className="w-16 h-16 text-purple-100" />
        </div>

        <div className="mt-6 pt-6 border-t border-purple-400/30">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-purple-100">This Month</p>
              <p className="text-xl">+87 pts</p>
            </div>
            <div>
              <p className="text-sm text-purple-100">All Time</p>
              <p className="text-xl">1,245 pts</p>
            </div>
            <div>
              <p className="text-sm text-purple-100">Redeemed</p>
              <p className="text-xl">8 rewards</p>
            </div>
          </div>
        </div>
      </div>

      {/* How to Earn Points */}
      <div className="bg-orange-50 border border-orange-200 rounded-xl p-6 mb-8">
        <h3 className="text-lg text-gray-900 mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-orange-600" />
          How to Earn Points
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center mb-3">
              <Gift className="w-5 h-5 text-orange-600" />
            </div>
            <h4 className="text-gray-900 mb-1">Place Orders</h4>
            <p className="text-sm text-gray-600">Earn 5% of order value as points</p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center mb-3">
              <Star className="w-5 h-5 text-orange-600" />
            </div>
            <h4 className="text-gray-900 mb-1">Runner Mode</h4>
            <p className="text-sm text-gray-600">Earn 10% of order value by delivering</p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center mb-3">
              <Award className="w-5 h-5 text-orange-600" />
            </div>
            <h4 className="text-gray-900 mb-1">Daily Login</h4>
            <p className="text-sm text-gray-600">Get 5 bonus points every day</p>
          </div>
        </div>
      </div>

      {/* Rewards Grid */}
      <div>
        <h2 className="text-2xl text-gray-900 mb-6">Available Rewards</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {rewards.map((reward) => {
            const canRedeem = currentPoints >= reward.pointsRequired;
            
            return (
              <div
                key={reward.id}
                className={`bg-white rounded-xl shadow-md overflow-hidden transition-all ${
                  canRedeem ? "hover:shadow-xl" : "opacity-60"
                }`}
              >
                <div className="relative h-48 overflow-hidden">
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
                  {!canRedeem && (
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

                  <button
                    disabled={!canRedeem}
                    className={`w-full py-3 rounded-lg transition-colors ${
                      canRedeem
                        ? "bg-orange-500 hover:bg-orange-600 text-white"
                        : "bg-gray-200 text-gray-500 cursor-not-allowed"
                    }`}
                  >
                    {canRedeem ? "Redeem Now" : "Not Enough Points"}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
