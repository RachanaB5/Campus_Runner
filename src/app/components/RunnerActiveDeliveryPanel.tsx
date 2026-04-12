import { useEffect, useMemo, useRef, useState } from "react";
import type { ClipboardEvent, KeyboardEvent } from "react";
import { X } from "lucide-react";
import { api } from "../services/api";

interface RunnerActiveDeliveryPanelProps {
  delivery: any;
  open: boolean;
  onClose: () => void;
  onStatusUpdate?: (delivery: any | null) => void;
}

export function RunnerActiveDeliveryPanel({ delivery, open, onClose, onStatusUpdate }: RunnerActiveDeliveryPanelProps) {
  const [otpDigits, setOtpDigits] = useState(["", "", "", ""]);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState("");
  const [shake, setShake] = useState(false);
  const [celebrationPoints, setCelebrationPoints] = useState(0);
  const refs = [useRef<HTMLInputElement>(null), useRef<HTMLInputElement>(null), useRef<HTMLInputElement>(null), useRef<HTMLInputElement>(null)];

  useEffect(() => {
    setOtpDigits(["", "", "", ""]);
    setError("");
    setShake(false);
  }, [delivery?.delivery_id, delivery?.delivery_status]);

  const phase = useMemo(() => {
    if (!delivery) return "pickup";
    if (delivery.delivery_status === "delivered") return "delivered";
    if (delivery.delivery_status === "picked_up" || delivery.delivery_status === "on_the_way") return "on_way";
    return "pickup";
  }, [delivery]);

  if (!open || !delivery) return null;

  const details = delivery.details || {};
  const enteredOtp = otpDigits.join("");

  const handlePickedUp = async () => {
    setUpdating(true);
    setError("");
    try {
      await api.updateRunnerDeliveryStatus(delivery.delivery_id, "picked_up");
      const refreshed = await api.getRunnerActiveDelivery();
      onStatusUpdate?.(refreshed.active ? refreshed : null);
    } catch (err: any) {
      setError(err.message || "Could not mark order as picked up");
    } finally {
      setUpdating(false);
    }
  };

  const handleConfirmDelivery = async () => {
    if (enteredOtp.length !== 4) return;
    setUpdating(true);
    setError("");
    try {
      await api.updateRunnerDeliveryStatus(delivery.delivery_id, "on_the_way");
      const response = await api.updateRunnerDeliveryStatus(delivery.delivery_id, "delivered", enteredOtp);
      setCelebrationPoints(response.points_earned || delivery.reward_points || 0);
      onStatusUpdate?.({
        ...delivery,
        delivery_status: "delivered",
        details: {
          ...details,
          delivery_status: "delivered",
        },
      });
    } catch (err: any) {
      setShake(true);
      setError(err.message || "Incorrect OTP. Please check with the customer.");
      window.setTimeout(() => setShake(false), 500);
    } finally {
      setUpdating(false);
    }
  };

  const handleOtpChange = (index: number, value: string) => {
    const digit = value.replace(/\D/g, "").slice(-1);
    const next = [...otpDigits];
    next[index] = digit;
    setOtpDigits(next);
    if (digit && index < refs.length - 1) {
      refs[index + 1].current?.focus();
    }
  };

  const handleOtpKeyDown = (index: number, event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Backspace" && !otpDigits[index] && index > 0) {
      refs[index - 1].current?.focus();
    }
  };

  const handleOtpPaste = (event: ClipboardEvent<HTMLInputElement>) => {
    const digits = event.clipboardData.getData("text").replace(/\D/g, "").slice(0, 4).split("");
    if (!digits.length) return;
    event.preventDefault();
    setOtpDigits([digits[0] || "", digits[1] || "", digits[2] || "", digits[3] || ""]);
    refs[Math.min(digits.length, 4) - 1].current?.focus();
  };

  return (
    <div className="fixed inset-0 z-[70] bg-black/40">
      <div className="absolute inset-0 h-full w-full bg-[var(--bg)] shadow-2xl overflow-y-auto">
        <div className="sticky top-0 z-10 border-b bg-white/95 backdrop-blur">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
          <div>
            <p className="text-sm font-semibold text-green-600">Active Delivery</p>
            <h2 className="text-2xl font-bold text-gray-900">Order {details.token_number || delivery.order?.token_number}</h2>
          </div>
          <button type="button" onClick={onClose} className="rounded-full p-2 hover:bg-gray-100">
            <X className="w-5 h-5" />
          </button>
        </div>
        </div>

        {phase === "pickup" && (
          <div className="mx-auto max-w-6xl p-6 space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-[0.9fr_1.1fr] gap-6">
            <div className="space-y-6">
            <div className="rounded-3xl bg-orange-50 border border-orange-100 p-6">
              <p className="text-sm font-semibold text-gray-500">SHOW THIS TO STAFF</p>
              <p className="mt-3 text-center text-5xl font-bold tracking-[0.6em] text-orange-600">{delivery.pickup_otp || details.pickup_otp}</p>
            </div>
            <div className="rounded-3xl border border-blue-100 bg-blue-50 p-6">
              <p className="text-sm font-semibold text-gray-500">DELIVER TO</p>
              <p className="mt-2 text-xl font-bold text-gray-900">{details.delivery_address?.full_address || delivery.order?.delivery_address}</p>
              <p className="mt-3 text-gray-600">Customer: {delivery.customer_name || details.customer_name}</p>
              <p className="mt-4 text-sm font-semibold text-green-700">Earn {delivery.reward_points || details.runner_reward_points || 0} pts on completion</p>
            </div>
            </div>
            <div className="rounded-3xl border border-gray-100 bg-white p-6">
              <p className="font-semibold text-gray-900 mb-4">Items to collect</p>
              <div className="space-y-3">
                {(details.items || delivery.order?.items || []).map((item: any) => (
                  <div key={`${item.food_id}-${item.name}`} className="flex items-start justify-between gap-4 rounded-2xl bg-gray-50 px-4 py-3">
                    <div className="flex-1">
                      <p className="font-semibold text-gray-900">{item.name}</p>
                      <p className="text-sm text-gray-500">× {item.quantity} {item.customizations ? `• ${item.customizations}` : ""}</p>
                    </div>
                    <p className="font-semibold text-gray-900">₹{item.subtotal ?? item.unit_price}</p>
                  </div>
                ))}
              </div>
              <div className="mt-4 border-t pt-4 text-sm text-gray-600 space-y-1">
                <p>Total: <span className="font-semibold text-gray-900">₹{details.total_amount || delivery.order?.total_amount}</span></p>
                <p>Payment: {String(details.payment_method || delivery.order?.payment_method || "").toUpperCase()} {details.payment_status || delivery.order?.payment_status}</p>
                {details.special_instructions && <p>Special: {details.special_instructions}</p>}
              </div>
            </div>
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <button type="button" disabled={updating} onClick={handlePickedUp} className="w-full rounded-2xl bg-green-500 px-5 py-4 text-white font-bold disabled:opacity-60">
              {updating ? "Updating..." : "I've Picked Up"}
            </button>
          </div>
        )}

        {phase === "on_way" && (
          <div className="mx-auto max-w-6xl p-6 space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-[1fr_0.9fr] gap-6">
            <div className="space-y-6">
            <div className="rounded-3xl border border-blue-100 bg-blue-50 p-6">
              <p className="text-sm font-semibold text-gray-500">DELIVERING TO</p>
              <p className="mt-2 text-xl font-bold text-gray-900">{details.delivery_address?.full_address || delivery.order?.delivery_address}</p>
              <p className="mt-4 text-gray-700">{delivery.customer_name || details.customer_name}</p>
              {delivery.customer_phone && (
                <a href={`tel:${delivery.customer_phone}`} className="mt-3 inline-flex rounded-xl bg-green-500 px-4 py-2 text-white font-semibold">
                  Call: {delivery.customer_phone}
                </a>
              )}
            </div>
            <div className="rounded-3xl border border-gray-100 bg-white p-6">
              <p className="font-semibold text-gray-900 mb-4">Carrying</p>
              <div className="space-y-3">
                {(details.items || delivery.order?.items || []).map((item: any) => (
                  <div key={`${item.food_id}-${item.name}`} className="flex items-start justify-between gap-4 rounded-2xl bg-gray-50 px-4 py-3">
                    <div>
                      <p className="font-semibold text-gray-900">{item.name}</p>
                      <p className="text-sm text-gray-500">× {item.quantity} {item.customizations ? `• ${item.customizations}` : ""}</p>
                    </div>
                    <p className="font-semibold text-gray-900">₹{item.subtotal ?? item.unit_price}</p>
                  </div>
                ))}
              </div>
            </div>
            </div>
            <div className="rounded-3xl border border-gray-100 bg-white p-6">
              <p className="font-semibold text-gray-900 mb-3">Enter Delivery OTP From Customer</p>
              <div className={`flex gap-3 ${shake ? "animate-pulse" : ""}`}>
                {otpDigits.map((digit, index) => (
                  <input
                    key={index}
                    ref={refs[index]}
                    value={digit}
                    onChange={(event) => handleOtpChange(index, event.target.value)}
                    onKeyDown={(event) => handleOtpKeyDown(index, event)}
                    onPaste={handleOtpPaste}
                    inputMode="numeric"
                    maxLength={1}
                    className={`h-16 w-16 rounded-2xl border text-center text-2xl font-bold focus:outline-none ${error ? "border-red-400" : "border-gray-300 focus:border-orange-400"}`}
                  />
                ))}
              </div>
              {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
            </div>
            </div>
            <button type="button" disabled={updating || enteredOtp.length !== 4} onClick={handleConfirmDelivery} className="w-full rounded-2xl bg-orange-500 px-5 py-4 text-white font-bold disabled:opacity-60">
              {updating ? "Confirming..." : "Confirm Delivery"}
            </button>
          </div>
        )}

        {phase === "delivered" && (
          <div className="mx-auto max-w-4xl p-10 text-center">
            <div className="text-6xl">🎉</div>
            <h3 className="mt-4 text-3xl font-bold text-gray-900">Delivered!</h3>
            <div className="mx-auto mt-6 max-w-md rounded-3xl border border-green-100 bg-green-50 p-6 text-left">
              <p className="text-2xl font-bold text-green-700">+{celebrationPoints || delivery.reward_points || 0} Points Earned</p>
              <p className="mt-2 text-gray-600">Delivery completed successfully.</p>
            </div>
            <button type="button" onClick={onClose} className="mt-8 rounded-2xl bg-gray-900 px-6 py-4 text-white font-bold">
              Close Panel
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
