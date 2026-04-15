import { useEffect, useMemo, useState } from "react";
import {
  Award, Bike, CreditCard, LogOut, Mail, Phone, ShoppingBag, User,
  ChevronDown, ChevronUp, Star, Edit2, Lock, Bell,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { api, API_BASE_URL, getToken } from "../services/api";
import { useNavigate } from "react-router";
import { ImageWithFallback } from "../components/figma/ImageWithFallback";
import { toast } from "sonner";

const defaultPreferences = {
  order_updates: true,
  runner_assigned: true,
  order_delivered: true,
  new_orders_available: true,
  reward_points: true,
  promotions: false,
};

function StatCard({ value, label, color, icon: Icon }: any) {
  return (
    <div className={`rounded-2xl bg-gradient-to-br ${color} p-5 text-white flex flex-col gap-3 shadow-lg`}>
      <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
        <Icon className="w-5 h-5" />
      </div>
      <div>
        <p className="text-2xl font-bold">{value}</p>
        <p className="text-white/80 text-sm mt-0.5">{label}</p>
      </div>
    </div>
  );
}

function SectionCard({ title, icon: Icon, open, onToggle, children }: any) {
  return (
    <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800 overflow-hidden">
      <button
        type="button"
        onClick={onToggle}
        className="w-full flex items-center justify-between gap-3 px-6 py-5 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors text-left"
      >
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center">
            <Icon className="w-5 h-5 text-orange-600" />
          </div>
          <span className="text-base font-semibold text-gray-900 dark:text-white">{title}</span>
        </div>
        {open ? (
          <ChevronUp className="w-5 h-5 text-gray-400 flex-shrink-0" />
        ) : (
          <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
        )}
      </button>
      {open && (
        <div className="px-6 pb-6 border-t border-gray-100 dark:border-gray-800 pt-5">
          {children}
        </div>
      )}
    </div>
  );
}

export function Profile() {
  const { user, logout, updateUser } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<any>(user);
  const [savedMethods, setSavedMethods] = useState<any[]>([]);
  const [editOpen, setEditOpen] = useState(false);
  const [passwordOpen, setPasswordOpen] = useState(false);
  const [prefsOpen, setPrefsOpen] = useState(false);
  const [paymentsOpen, setPaymentsOpen] = useState(false);
  const [savingProfile, setSavingProfile] = useState(false);
  const [editForm, setEditForm] = useState({ name: "", phone: "", avatar_url: "" });
  const [passwordForm, setPasswordForm] = useState({ current_password: "", new_password: "", confirm_password: "" });
  const [preferences, setPreferences] = useState(defaultPreferences);
  const [addMethodType, setAddMethodType] = useState<"card" | "upi" | "">("");
  const [newMethod, setNewMethod] = useState<any>({ upi_id: "", upi_nickname: "", card_number: "", card_holder_name: "", card_expiry: "", card_pin: "" });

  const loadProfile = async () => {
    const response = await api.getCurrentUser();
    setProfile(response);
    setEditForm({
      name: response.name || "",
      phone: response.phone || "",
      avatar_url: response.avatar_url || response.profile_image || "",
    });
    setPreferences({ ...defaultPreferences, ...(response.notification_preferences || {}) });
  };

  const loadPaymentMethods = async () => {
    const response = await api.getSavedPaymentMethods();
    setSavedMethods(response.payment_methods || []);
  };

  useEffect(() => {
    loadProfile().catch(() => undefined);
    loadPaymentMethods().catch(() => undefined);
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const handleProfileSave = async () => {
    setSavingProfile(true);
    try {
      const token = getToken();
      const response = await fetch(`${API_BASE_URL}/auth/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: editForm.name.trim(),
          phone: editForm.phone.trim(),
          avatar_url: editForm.avatar_url.trim(),
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Failed to save profile");
      updateUser(data.user);
      await loadProfile();
      toast.success("Profile updated!");
      setEditOpen(false);
    } catch (err: any) {
      toast.error(err?.message || "Failed to save profile");
    } finally {
      setSavingProfile(false);
    }
  };

  const handlePasswordSave = async () => {
    await api.changePassword(passwordForm);
    setPasswordForm({ current_password: "", new_password: "", confirm_password: "" });
    toast.success("Password changed successfully");
    setPasswordOpen(false);
  };

  const handlePreferenceToggle = async (key: string, value: boolean) => {
    const nextPrefs = { ...preferences, [key]: value };
    setPreferences(nextPrefs);
    await api.updateNotificationPreferences({ [key]: value });
    toast.success("Saved ✓");
  };

  const handleAddMethod = async () => {
    await api.createSavedPaymentMethod({ type: addMethodType, ...newMethod });
    setNewMethod({ upi_id: "", upi_nickname: "", card_number: "", card_holder_name: "", card_expiry: "", card_pin: "" });
    setAddMethodType("");
    await loadPaymentMethods();
    toast.success("Payment method saved");
  };

  const memberSince = useMemo(() => profile?.member_since || "Recently", [profile?.member_since]);
  const isRunner = user?.role === "RUNNER" || user?.role === "runner";

  const inputClass =
    "w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-3 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 text-sm";

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-1">My Profile</h1>
        <p className="text-gray-500 dark:text-gray-400 text-sm">Manage your account and preferences.</p>
      </div>

      {/* Hero Card — clean, no color banner */}
      <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm overflow-hidden mb-6 border border-gray-100 dark:border-gray-800">
        <div className="px-6 py-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          {/* Avatar + Name */}
          <div className="flex items-center gap-4">
            <div className="w-20 h-20 rounded-2xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center overflow-hidden flex-shrink-0 border border-gray-200 dark:border-gray-700">
              {profile?.avatar_url || profile?.profile_image ? (
                <ImageWithFallback
                  src={profile.avatar_url || profile.profile_image}
                  alt={profile?.name}
                  className="h-full w-full object-cover"
                />
              ) : (
                <User className="w-10 h-10 text-gray-400" />
              )}
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">{profile?.name || user?.name}</h2>
              <div className="flex items-center gap-2 mt-1">
                <span className="inline-flex items-center gap-1 rounded-full bg-orange-50 dark:bg-orange-900/20 px-2.5 py-0.5 text-xs font-semibold text-orange-600 dark:text-orange-400">
                  {isRunner ? "🏍️ Runner" : "🛍️ Customer"}
                </span>
                {isRunner && profile?.stats?.runner_rating > 0 && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-yellow-50 dark:bg-yellow-900/20 px-2.5 py-0.5 text-xs font-semibold text-yellow-700 dark:text-yellow-400">
                    <Star className="w-3 h-3" />
                    {Number(profile.stats.runner_rating || 0).toFixed(1)}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Contact info */}
          <div className="flex flex-col gap-1.5 text-sm text-gray-500 dark:text-gray-400">
            <span className="flex items-center gap-2"><Mail className="w-4 h-4 text-gray-400" />{profile?.email}</span>
            {profile?.phone && (
              <span className="flex items-center gap-2"><Phone className="w-4 h-4 text-gray-400" />{profile.phone}</span>
            )}
            <span className="text-xs text-gray-400 mt-0.5">Member since {memberSince}</span>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
        <StatCard
          value={profile?.stats?.total_points || 0}
          label="Reward Points"
          color="from-orange-500 to-red-500"
          icon={Award}
        />
        <StatCard
          value={profile?.stats?.total_orders || 0}
          label="Total Orders"
          color="from-blue-500 to-indigo-600"
          icon={ShoppingBag}
        />
        {isRunner ? (
          <StatCard
            value={profile?.stats?.deliveries_made || 0}
            label="Deliveries Made"
            color="from-emerald-500 to-green-600"
            icon={Bike}
          />
        ) : (
          <StatCard
            value={profile?.stats?.deliveries_made || 0}
            label="Deliveries Made"
            color="from-emerald-500 to-green-600"
            icon={Bike}
          />
        )}
      </div>

      {/* Become a Runner Banner — only for non-runners */}
      {!isRunner && (
        <div className="mb-6 rounded-2xl bg-gradient-to-r from-orange-500 via-red-500 to-pink-500 p-6 text-white shadow-lg">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div>
              <h3 className="text-lg font-bold flex items-center gap-2">
                <Bike className="w-5 h-5" /> Become a Delivery Runner!
              </h3>
              <p className="text-orange-100 text-sm mt-1 max-w-sm">
                Earn points, get rewards, and help your campus community by delivering food on campus.
              </p>
            </div>
            <button
              type="button"
              onClick={async () => {
                try {
                  await api.registerAsRunner({ vehicle_type: "bicycle", license_number: "N/A" });
                  toast.success("Welcome aboard! Refresh the page to access Runner Mode.");
                  setTimeout(() => window.location.reload(), 1500);
                } catch (err: any) {
                  toast.error(err.message || "Failed to upgrade account.");
                }
              }}
              className="bg-white text-orange-600 px-6 py-2.5 rounded-xl font-bold shadow hover:bg-orange-50 transition-colors shrink-0 text-sm"
            >
              Join Now →
            </button>
          </div>
        </div>
      )}

      {/* Stacked Sections */}
      <div className="space-y-3">
        {/* Edit Profile */}
        <SectionCard title="Edit Profile" icon={Edit2} open={editOpen} onToggle={() => setEditOpen((v) => !v)}>
          <div className="space-y-3">
            <input
              className={inputClass}
              placeholder="Full Name"
              value={editForm.name}
              onChange={(e) => setEditForm((p) => ({ ...p, name: e.target.value }))}
            />
            <input
              className={inputClass}
              placeholder="Phone Number"
              value={editForm.phone}
              onChange={(e) => setEditForm((p) => ({ ...p, phone: e.target.value }))}
            />
            <input
              className={inputClass}
              placeholder="Avatar URL (optional)"
              value={editForm.avatar_url}
              onChange={(e) => setEditForm((p) => ({ ...p, avatar_url: e.target.value }))}
            />
            <input
              className={`${inputClass} opacity-60 cursor-not-allowed`}
              value={profile?.email || ""}
              disabled
            />
            <div className="flex gap-3 pt-1">
              <button
                type="button"
                onClick={handleProfileSave}
                disabled={savingProfile}
                className="rounded-xl bg-orange-500 hover:bg-orange-600 px-5 py-2.5 text-white text-sm font-semibold disabled:opacity-60 transition-colors"
              >
                {savingProfile ? "Saving..." : "Save Changes"}
              </button>
              <button
                type="button"
                onClick={() => setEditOpen(false)}
                className="rounded-xl border border-gray-200 dark:border-gray-700 px-5 py-2.5 text-sm font-semibold text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </SectionCard>

        {/* Change Password */}
        <SectionCard title="Change Password" icon={Lock} open={passwordOpen} onToggle={() => setPasswordOpen((v) => !v)}>
          <div className="space-y-3">
            <input
              type="password"
              className={inputClass}
              placeholder="Current Password"
              value={passwordForm.current_password}
              onChange={(e) => setPasswordForm((p) => ({ ...p, current_password: e.target.value }))}
            />
            <input
              type="password"
              className={inputClass}
              placeholder="New Password"
              value={passwordForm.new_password}
              onChange={(e) => setPasswordForm((p) => ({ ...p, new_password: e.target.value }))}
            />
            <input
              type="password"
              className={inputClass}
              placeholder="Confirm New Password"
              value={passwordForm.confirm_password}
              onChange={(e) => setPasswordForm((p) => ({ ...p, confirm_password: e.target.value }))}
            />
            <button
              type="button"
              onClick={handlePasswordSave}
              className="rounded-xl bg-gray-900 dark:bg-white dark:text-gray-900 px-5 py-2.5 text-white text-sm font-semibold hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors"
            >
              Update Password
            </button>
          </div>
        </SectionCard>

        {/* Notification Preferences */}
        <SectionCard
          title="Notification Preferences"
          icon={Bell}
          open={prefsOpen}
          onToggle={() => setPrefsOpen((v) => !v)}
        >
          <div className="space-y-2">
            {[
              ["order_updates", "Order status updates"],
              ["runner_assigned", "Runner assigned alerts"],
              ["order_delivered", "Delivery confirmations"],
              ["new_orders_available", "New orders (Runner mode)"],
              ["reward_points", "Reward points earned"],
              ["promotions", "Promotions & offers"],
            ].map(([key, label]) => (
              <label
                key={key}
                className="flex items-center justify-between rounded-xl bg-gray-50 dark:bg-gray-800 px-4 py-3 cursor-pointer hover:bg-orange-50 dark:hover:bg-gray-700 transition-colors"
              >
                <span className="text-sm text-gray-700 dark:text-gray-300 font-medium">{label}</span>
                <input
                  type="checkbox"
                  className="w-4 h-4 text-orange-500 rounded border-gray-300 focus:ring-orange-500"
                  checked={Boolean((preferences as any)[key])}
                  onChange={(e) => handlePreferenceToggle(key, e.target.checked)}
                />
              </label>
            ))}
          </div>
        </SectionCard>

        {/* Payment Methods */}
        <SectionCard
          title="Payment Methods"
          icon={CreditCard}
          open={paymentsOpen}
          onToggle={() => setPaymentsOpen((v) => !v)}
        >
          <div className="space-y-3">
            {savedMethods.map((method) => (
              <div key={method.id} className="rounded-xl border border-gray-100 dark:border-gray-700 p-4 bg-gray-50 dark:bg-gray-800">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <CreditCard className="w-5 h-5 text-orange-500" />
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-white text-sm">
                        {method.type === "card"
                          ? `${method.card_brand || "Card"} ending in ${method.card_last4}`
                          : method.upi_id}
                        {method.is_default && (
                          <span className="ml-2 text-xs bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400 px-2 py-0.5 rounded-full">
                            Default
                          </span>
                        )}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                        {method.type === "card"
                          ? `${method.card_holder_name} · Exp ${method.card_expiry}`
                          : method.upi_nickname || "Saved UPI"}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2 text-xs">
                    {!method.is_default && (
                      <button
                        type="button"
                        onClick={async () => {
                          await api.setDefaultPaymentMethod(method.id);
                          await loadPaymentMethods();
                          toast.success("Default payment updated");
                        }}
                        className="text-orange-600 font-semibold hover:underline"
                      >
                        Set Default
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={async () => {
                        await api.removeSavedPaymentMethod(method.id);
                        await loadPaymentMethods();
                        toast.success("Payment method removed");
                      }}
                      className="text-red-500 font-semibold hover:underline"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              </div>
            ))}

            <div className="rounded-xl border border-dashed border-orange-200 dark:border-orange-800 p-4">
              <div className="flex gap-2 mb-3">
                <button
                  type="button"
                  onClick={() => setAddMethodType("upi")}
                  className="rounded-xl bg-orange-50 dark:bg-orange-900/30 px-4 py-2 text-orange-700 dark:text-orange-400 text-sm font-semibold hover:bg-orange-100 transition-colors"
                >
                  + Add UPI
                </button>
                <button
                  type="button"
                  onClick={() => setAddMethodType("card")}
                  className="rounded-xl bg-orange-50 dark:bg-orange-900/30 px-4 py-2 text-orange-700 dark:text-orange-400 text-sm font-semibold hover:bg-orange-100 transition-colors"
                >
                  + Add Card
                </button>
              </div>
              {addMethodType === "upi" && (
                <div className="space-y-2">
                  <input className={inputClass} placeholder="UPI ID (e.g. rahul@okaxis)" value={newMethod.upi_id} onChange={(e) => setNewMethod((p: any) => ({ ...p, upi_id: e.target.value }))} />
                  <input className={inputClass} placeholder="Nickname (e.g. My GPay)" value={newMethod.upi_nickname} onChange={(e) => setNewMethod((p: any) => ({ ...p, upi_nickname: e.target.value }))} />
                  <button type="button" onClick={handleAddMethod} className="rounded-xl bg-orange-500 px-5 py-2.5 text-white text-sm font-semibold hover:bg-orange-600 transition-colors">Save UPI</button>
                </div>
              )}
              {addMethodType === "card" && (
                <div className="space-y-2">
                  <input className={inputClass} placeholder="Card Number" value={newMethod.card_number} onChange={(e) => setNewMethod((p: any) => ({ ...p, card_number: e.target.value }))} />
                  <input className={inputClass} placeholder="Cardholder Name" value={newMethod.card_holder_name} onChange={(e) => setNewMethod((p: any) => ({ ...p, card_holder_name: e.target.value }))} />
                  <input className={inputClass} placeholder="MM/YYYY" value={newMethod.card_expiry} onChange={(e) => setNewMethod((p: any) => ({ ...p, card_expiry: e.target.value }))} />
                  <input type="password" className={inputClass} placeholder="PIN" value={newMethod.card_pin} onChange={(e) => setNewMethod((p: any) => ({ ...p, card_pin: e.target.value }))} />
                  <button type="button" onClick={handleAddMethod} className="rounded-xl bg-orange-500 px-5 py-2.5 text-white text-sm font-semibold hover:bg-orange-600 transition-colors">Save Card</button>
                </div>
              )}
            </div>
          </div>
        </SectionCard>
      </div>

      {/* Logout */}
      <button
        onClick={handleLogout}
        className="mt-6 w-full flex items-center justify-center gap-2 rounded-2xl border-2 border-red-200 dark:border-red-900 text-red-600 dark:text-red-400 py-3.5 font-semibold hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
      >
        <LogOut className="w-5 h-5" />
        Sign Out
      </button>
    </div>
  );
}
