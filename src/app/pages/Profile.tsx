import { useEffect, useMemo, useState } from "react";
import { Award, Bike, CreditCard, LogOut, Mail, Phone, ShoppingBag, User } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { api, API_BASE_URL, getToken } from "../services/api";
import { useNavigate } from "react-router";

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
    <div className={`rounded-xl bg-gradient-to-br ${color} p-6 text-white`}>
      <Icon className="w-8 h-8 mb-3" />
      <p className="text-3xl mb-1">{value}</p>
      <p className="text-white/85">{label}</p>
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
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
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

  const showMessage = (text: string) => {
    setError("");
    setMessage(text);
    window.setTimeout(() => setMessage(""), 2000);
  };

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const handleProfileSave = async () => {
    setSavingProfile(true);
    setError("");
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
      if (!response.ok) {
        throw new Error(data.error || "Failed to save profile");
      }
      updateUser(data.user);
      await loadProfile();
      showMessage("Profile updated!");
      setEditOpen(false);
    } catch (err: any) {
      setError(err?.message || "Failed to save profile");
    } finally {
      setSavingProfile(false);
    }
  };

  const handlePasswordSave = async () => {
    await api.changePassword(passwordForm);
    setPasswordForm({ current_password: "", new_password: "", confirm_password: "" });
    showMessage("Password changed successfully");
    setPasswordOpen(false);
  };

  const handlePreferenceToggle = async (key: string, value: boolean) => {
    const nextPrefs = { ...preferences, [key]: value };
    setPreferences(nextPrefs);
    await api.updateNotificationPreferences({ [key]: value });
    showMessage("Saved ✓");
  };

  const handleAddMethod = async () => {
    await api.createSavedPaymentMethod({ type: addMethodType, ...newMethod });
    setNewMethod({ upi_id: "", upi_nickname: "", card_number: "", card_holder_name: "", card_expiry: "", card_pin: "" });
    setAddMethodType("");
    await loadPaymentMethods();
    showMessage("Payment method saved");
  };

  const memberSince = useMemo(() => profile?.member_since || "Recently", [profile?.member_since]);

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      <div className="mb-8">
        <h1 className="text-3xl text-gray-900 mb-2">Profile</h1>
        <p className="text-gray-600">Manage your account, delivery preferences, and saved payments.</p>
      </div>

      {message && <div className="mb-4 rounded-xl bg-green-50 border border-green-200 px-4 py-3 text-green-700">{message}</div>}
      {error && <div className="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-red-700">{error}</div>}

      <div className="bg-white rounded-xl shadow-md overflow-hidden mb-8">
        <div className="bg-gradient-to-r from-orange-500 to-red-500 h-32" />
        <div className="px-6 pb-6">
          <div className="flex items-end gap-4 -mt-16 mb-6">
            <div className="w-32 h-32 bg-white rounded-full border-4 border-white shadow-lg overflow-hidden flex items-center justify-center">
              {profile?.avatar_url || profile?.profile_image ? (
                <img src={profile.avatar_url || profile.profile_image} alt={profile?.name} className="h-full w-full object-cover" />
              ) : (
                <User className="w-16 h-16 text-gray-400" />
              )}
            </div>
            <div className="pb-4">
              <h2 className="text-2xl text-gray-900">{profile?.name || user?.name}</h2>
              <p className="text-gray-600">{profile?.role || user?.role || "Customer"}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <Mail className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-xs text-gray-500">Email</p>
                <p className="text-gray-900">{profile?.email}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <Phone className="w-5 h-5 text-gray-400" />
              <div>
                <p className="text-xs text-gray-500">Phone</p>
                <p className="text-gray-900">{profile?.phone || "Add your mobile number"}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <StatCard value={profile?.stats?.total_points || 0} label="Total Points" color="from-orange-500 to-red-500" icon={Award} />
        <StatCard value={profile?.stats?.total_orders || 0} label="Total Orders" color="from-blue-500 to-indigo-600" icon={ShoppingBag} />
        <StatCard value={profile?.stats?.deliveries_made || 0} label="Deliveries Made" color="from-green-500 to-emerald-600" icon={Bike} />
      </div>

      <div className="space-y-4">
        <section className="bg-white rounded-xl shadow-md p-6">
          <button type="button" onClick={() => setEditOpen((value) => !value)} className="w-full flex items-center justify-between text-left">
            <span className="text-xl text-gray-900">Edit Profile</span>
            <span>{editOpen ? "∧" : "∨"}</span>
          </button>
          {editOpen && (
            <div className="mt-5 space-y-4">
              <input className="w-full rounded-xl border px-4 py-3" placeholder="Full Name" value={editForm.name} onChange={(e) => setEditForm((prev) => ({ ...prev, name: e.target.value }))} />
              <input className="w-full rounded-xl border px-4 py-3" placeholder="Phone Number" value={editForm.phone} onChange={(e) => setEditForm((prev) => ({ ...prev, phone: e.target.value }))} />
              <input className="w-full rounded-xl border px-4 py-3" placeholder="Avatar URL" value={editForm.avatar_url} onChange={(e) => setEditForm((prev) => ({ ...prev, avatar_url: e.target.value }))} />
              <input className="w-full rounded-xl border bg-gray-50 px-4 py-3 text-gray-500" value={profile?.email || ""} disabled />
              <div className="flex gap-3">
                <button type="button" onClick={handleProfileSave} disabled={savingProfile} className="rounded-xl bg-orange-500 px-5 py-3 text-white font-semibold disabled:cursor-not-allowed disabled:opacity-60">
                  {savingProfile ? "Saving..." : "Save Changes"}
                </button>
                <button type="button" onClick={() => { setError(""); setEditOpen(false); }} className="rounded-xl border px-5 py-3 font-semibold">Cancel</button>
              </div>
            </div>
          )}
        </section>

        <section className="bg-white rounded-xl shadow-md p-6">
          <button type="button" onClick={() => setPasswordOpen((value) => !value)} className="w-full flex items-center justify-between text-left">
            <span className="text-xl text-gray-900">Change Password</span>
            <span>{passwordOpen ? "∧" : "∨"}</span>
          </button>
          {passwordOpen && (
            <div className="mt-5 space-y-4">
              <input type="password" className="w-full rounded-xl border px-4 py-3" placeholder="Current Password" value={passwordForm.current_password} onChange={(e) => setPasswordForm((prev) => ({ ...prev, current_password: e.target.value }))} />
              <input type="password" className="w-full rounded-xl border px-4 py-3" placeholder="New Password" value={passwordForm.new_password} onChange={(e) => setPasswordForm((prev) => ({ ...prev, new_password: e.target.value }))} />
              <input type="password" className="w-full rounded-xl border px-4 py-3" placeholder="Confirm New Password" value={passwordForm.confirm_password} onChange={(e) => setPasswordForm((prev) => ({ ...prev, confirm_password: e.target.value }))} />
              <button type="button" onClick={handlePasswordSave} className="rounded-xl bg-gray-900 px-5 py-3 text-white font-semibold">Update Password</button>
            </div>
          )}
        </section>

        <section className="bg-white rounded-xl shadow-md p-6">
          <button type="button" onClick={() => setPrefsOpen((value) => !value)} className="w-full flex items-center justify-between text-left">
            <span className="text-xl text-gray-900">Notification Preferences</span>
            <span>{prefsOpen ? "∧" : "∨"}</span>
          </button>
          {prefsOpen && (
            <div className="mt-5 space-y-4">
              {[
                ["order_updates", "Order status updates"],
                ["runner_assigned", "Runner assigned alerts"],
                ["order_delivered", "Delivery confirmations"],
                ["new_orders_available", "New orders (Runner mode)"],
                ["reward_points", "Reward points earned"],
                ["promotions", "Promotions & offers"],
              ].map(([key, label]) => (
                <label key={key} className="flex items-center justify-between rounded-xl bg-gray-50 px-4 py-3">
                  <span className="text-gray-700">{label}</span>
                  <input type="checkbox" checked={Boolean((preferences as any)[key])} onChange={(e) => handlePreferenceToggle(key, e.target.checked)} />
                </label>
              ))}
            </div>
          )}
        </section>

        <section className="bg-white rounded-xl shadow-md p-6">
          <button type="button" onClick={() => setPaymentsOpen((value) => !value)} className="w-full flex items-center justify-between text-left">
            <span className="text-xl text-gray-900">Payment Methods</span>
            <span>{paymentsOpen ? "∧" : "∨"}</span>
          </button>
          {paymentsOpen && (
            <div className="mt-5 space-y-4">
              {savedMethods.map((method) => (
                <div key={method.id} className="rounded-xl border border-gray-100 p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3">
                      <CreditCard className="w-5 h-5 text-orange-500 mt-1" />
                      <div>
                        <p className="font-semibold text-gray-900">
                          {method.type === "card" ? `${method.card_brand || "Card"} ending in ${method.card_last4}` : method.upi_id}
                          {method.is_default ? " [Default]" : ""}
                        </p>
                        <p className="text-sm text-gray-500">
                          {method.type === "card" ? `${method.card_holder_name} • Exp ${method.card_expiry}` : method.upi_nickname || "Saved UPI"}
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-2 text-sm">
                      {!method.is_default && <button type="button" onClick={async () => { await api.setDefaultPaymentMethod(method.id); await loadPaymentMethods(); showMessage("Default payment updated"); }} className="text-orange-600 font-semibold">Set Default</button>}
                      <button type="button" onClick={async () => { await api.removeSavedPaymentMethod(method.id); await loadPaymentMethods(); showMessage("Payment method removed"); }} className="text-red-600 font-semibold">Remove</button>
                    </div>
                  </div>
                </div>
              ))}

              <div className="rounded-xl border border-dashed border-orange-200 p-4">
                <div className="flex gap-3 mb-4">
                  <button type="button" onClick={() => setAddMethodType("upi")} className="rounded-xl bg-orange-50 px-4 py-2 text-orange-700 font-semibold">Add UPI</button>
                  <button type="button" onClick={() => setAddMethodType("card")} className="rounded-xl bg-orange-50 px-4 py-2 text-orange-700 font-semibold">Add Card</button>
                </div>
                {addMethodType === "upi" && (
                  <div className="space-y-3">
                    <input className="w-full rounded-xl border px-4 py-3" placeholder="rahul@okaxis" value={newMethod.upi_id} onChange={(e) => setNewMethod((prev: any) => ({ ...prev, upi_id: e.target.value }))} />
                    <input className="w-full rounded-xl border px-4 py-3" placeholder="My GPay" value={newMethod.upi_nickname} onChange={(e) => setNewMethod((prev: any) => ({ ...prev, upi_nickname: e.target.value }))} />
                    <button type="button" onClick={handleAddMethod} className="rounded-xl bg-orange-500 px-5 py-3 text-white font-semibold">Save UPI</button>
                  </div>
                )}
                {addMethodType === "card" && (
                  <div className="space-y-3">
                    <input className="w-full rounded-xl border px-4 py-3" placeholder="Card Number" value={newMethod.card_number} onChange={(e) => setNewMethod((prev: any) => ({ ...prev, card_number: e.target.value }))} />
                    <input className="w-full rounded-xl border px-4 py-3" placeholder="Cardholder Name" value={newMethod.card_holder_name} onChange={(e) => setNewMethod((prev: any) => ({ ...prev, card_holder_name: e.target.value }))} />
                    <input className="w-full rounded-xl border px-4 py-3" placeholder="MM/YYYY" value={newMethod.card_expiry} onChange={(e) => setNewMethod((prev: any) => ({ ...prev, card_expiry: e.target.value }))} />
                    <input type="password" className="w-full rounded-xl border px-4 py-3" placeholder="PIN" value={newMethod.card_pin} onChange={(e) => setNewMethod((prev: any) => ({ ...prev, card_pin: e.target.value }))} />
                    <button type="button" onClick={handleAddMethod} className="rounded-xl bg-orange-500 px-5 py-3 text-white font-semibold">Save Card</button>
                  </div>
                )}
              </div>
            </div>
          )}
        </section>
      </div>

      <button onClick={handleLogout} className="mt-8 w-full bg-red-500 hover:bg-red-600 text-white py-3 rounded-lg flex items-center justify-center gap-2 transition-colors">
        <LogOut className="w-5 h-5" />
        <span>Logout</span>
      </button>

      <p className="text-center text-sm text-gray-500 mt-6">Member since {memberSince}</p>
    </div>
  );
}
