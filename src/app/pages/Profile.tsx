import { User, Mail, Phone, MapPin, Award, Bike, ShoppingBag, LogOut } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router";

export function Profile() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const userData = {
    name: user?.name || "Rahul Sharma",
    email: user?.email || "rahul.sharma@rvu.edu.in",
    phone: "+91 98765 43210",
    hostel: "Block A, Room 204",
    totalPoints: 245,
    totalOrders: 23,
    totalDeliveries: 15,
    memberSince: "January 2026"
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div className="mb-8">
        <h1 className="text-3xl text-gray-900 mb-2">Profile</h1>
        <p className="text-gray-600">Manage your account and view your activity</p>
      </div>

      {/* Profile Card */}
      <div className="bg-white rounded-xl shadow-md overflow-hidden mb-8">
        <div className="bg-gradient-to-r from-orange-500 to-red-500 h-32"></div>
        <div className="px-6 pb-6">
          <div className="flex items-end gap-4 -mt-16 mb-6">
            <div className="w-32 h-32 bg-white rounded-full border-4 border-white shadow-lg flex items-center justify-center">
              <User className="w-16 h-16 text-gray-400" />
            </div>
            <div className="pb-4">
              <h2 className="text-2xl text-gray-900">{userData.name}</h2>
              <p className="text-gray-600">RV University Student</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <Mail className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-xs text-gray-500">Email</p>
                <p className="text-gray-900">{userData.email}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <Phone className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-xs text-gray-500">Phone</p>
                <p className="text-gray-900">{userData.phone}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg md:col-span-2">
              <MapPin className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-xs text-gray-500">Hostel Address</p>
                <p className="text-gray-900">{userData.hostel}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-gradient-to-br from-orange-500 to-red-500 rounded-xl p-6 text-white">
          <Award className="w-8 h-8 mb-3" />
          <p className="text-3xl mb-1">{userData.totalPoints}</p>
          <p className="text-orange-100">Total Points</p>
        </div>
        <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl p-6 text-white">
          <ShoppingBag className="w-8 h-8 mb-3" />
          <p className="text-3xl mb-1">{userData.totalOrders}</p>
          <p className="text-blue-100">Total Orders</p>
        </div>
        <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl p-6 text-white">
          <Bike className="w-8 h-8 mb-3" />
          <p className="text-3xl mb-1">{userData.totalDeliveries}</p>
          <p className="text-green-100">Deliveries Made</p>
        </div>
      </div>

      {/* Settings */}
      <div className="bg-white rounded-xl shadow-md p-6 mb-8">
        <h3 className="text-xl text-gray-900 mb-4">Account Settings</h3>
        <div className="space-y-3">
          <button className="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-between">
            <span className="text-gray-700">Edit Profile</span>
            <span className="text-gray-400">›</span>
          </button>
          <button className="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-between">
            <span className="text-gray-700">Change Password</span>
            <span className="text-gray-400">›</span>
          </button>
          <button className="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-between">
            <span className="text-gray-700">Notification Preferences</span>
            <span className="text-gray-400">›</span>
          </button>
          <button 
            onClick={() => navigate("/payment")}
            className="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-between"
          >
            <span className="text-gray-700">Payment Methods</span>
            <span className="text-gray-400">›</span>
          </button>
        </div>
      </div>

      {/* Logout */}
      <button 
        onClick={handleLogout}
        className="w-full bg-red-500 hover:bg-red-600 text-white py-3 rounded-lg flex items-center justify-center gap-2 transition-colors"
      >
        <LogOut className="w-5 h-5" />
        <span>Logout</span>
      </button>

      <p className="text-center text-sm text-gray-500 mt-6">
        Member since {userData.memberSince}
      </p>
    </div>
  );
}