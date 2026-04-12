import { useMemo, useRef, useState } from "react";
import { CheckCircle2, CreditCard, Lock, Smartphone, Truck } from "lucide-react";

type PaymentMethod = "cod" | "upi" | "card";

interface PaymentMethodSelectorProps {
  amount: number;
  isLoading: boolean;
  disabled?: boolean;
  savedMethods?: Array<any>;
  onSubmit: (
    method: PaymentMethod,
    payload: {
      saved_method_id?: string;
      upi_id?: string;
      card_number?: string;
      card_holder_name?: string;
      card_expiry?: string;
      card_pin?: string;
    },
  ) => Promise<void>;
}

const UPI_REGEX = /^[\w.-]{3,}@[\w]{3,}$/;

function formatCardNumber(value: string) {
  return value
    .replace(/\D/g, "")
    .slice(0, 16)
    .replace(/(.{4})/g, "$1 ")
    .trim();
}

function detectCardBrand(cardNumber: string) {
  const digits = cardNumber.replace(/\s/g, "");
  if (digits.startsWith("4")) return "Visa";
  if (/^5[1-5]/.test(digits)) return "Mastercard";
  if (digits.startsWith("6")) return "RuPay";
  return "Card";
}

function luhnCheck(cardNumber: string) {
  const digits = cardNumber.replace(/\D/g, "");
  let sum = 0;
  let shouldDouble = false;
  for (let i = digits.length - 1; i >= 0; i -= 1) {
    let digit = Number(digits[i]);
    if (shouldDouble) {
      digit *= 2;
      if (digit > 9) digit -= 9;
    }
    sum += digit;
    shouldDouble = !shouldDouble;
  }
  return digits.length >= 12 && sum % 10 === 0;
}

export function PaymentMethodSelector({ amount, isLoading, disabled, savedMethods = [], onSubmit }: PaymentMethodSelectorProps) {
  const savedCardMeta = (() => {
    try {
      return JSON.parse(localStorage.getItem("saved_card_meta") || "null");
    } catch {
      return null;
    }
  })();
  const [method, setMethod] = useState<PaymentMethod>("cod");
  const [selectedSavedMethodId, setSelectedSavedMethodId] = useState("");
  const [upiId, setUpiId] = useState("");
  const [cardNumber, setCardNumber] = useState("");
  const [cardHolderName, setCardHolderName] = useState(savedCardMeta?.card_holder_name || "");
  const [cardExpiry, setCardExpiry] = useState(savedCardMeta?.card_expiry || "");
  const [isCardBackVisible, setIsCardBackVisible] = useState(false);
  const [localError, setLocalError] = useState("");
  const cardPinRef = useRef<HTMLInputElement | null>(null);

  const cardBrand = useMemo(() => detectCardBrand(cardNumber), [cardNumber]);
  const upiValid = !upiId || UPI_REGEX.test(upiId);
  const cardValid = !cardNumber || luhnCheck(cardNumber);

  const submit = async () => {
    setLocalError("");

    if (selectedSavedMethodId) {
      await onSubmit(method, { saved_method_id: selectedSavedMethodId });
      return;
    }

    if (method === "upi" && !UPI_REGEX.test(upiId.trim())) {
      setLocalError("Enter a valid UPI ID");
      return;
    }

    if (method === "card") {
      const pin = cardPinRef.current?.value || "";
      if (!luhnCheck(cardNumber)) {
        setLocalError("Enter a valid card number");
        return;
      }
      if (!cardHolderName.trim()) {
        setLocalError("Cardholder name is required");
        return;
      }
      if (!/^\d{2}\/\d{4}$/.test(cardExpiry)) {
        setLocalError("Expiry must be in MM/YYYY format");
        return;
      }
      if (!/^\d{4,6}$/.test(pin)) {
        setLocalError("PIN must be 4 to 6 digits");
        return;
      }

      try {
        await onSubmit("card", {
          card_number: cardNumber.replace(/\s/g, ""),
          card_holder_name: cardHolderName.trim(),
          card_expiry: cardExpiry,
          card_pin: pin,
        });
      } finally {
        if (cardPinRef.current) {
          cardPinRef.current.value = "";
        }
      }
      return;
    }

    await onSubmit(method, method === "upi" ? { upi_id: upiId.trim() } : {});
  };

  return (
    <div className="rounded-xl shadow-sm hover:shadow-md transition-shadow p-8 border border-gray-100 bg-white">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
          <CreditCard className="w-6 h-6 text-orange-600" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">Payment</h2>
          <p className="text-sm text-gray-500">Choose how you want to complete this order.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {[
          { id: "cod", label: "Cash on Delivery", icon: Truck },
          { id: "upi", label: "UPI via Razorpay", icon: Smartphone },
          { id: "card", label: "Card Payment", icon: CreditCard },
        ].map(({ id, label, icon: Icon }) => (
          <button
            type="button"
            key={id}
            onClick={() => setMethod(id as PaymentMethod)}
            className={`rounded-2xl border px-4 py-4 text-left transition-all ${
              method === id
                ? "border-orange-500 bg-orange-50 shadow-sm"
                : "border-gray-200 hover:border-orange-200"
            }`}
          >
            <Icon className={`w-5 h-5 mb-2 ${method === id ? "text-orange-600" : "text-gray-400"}`} />
            <p className="font-semibold text-gray-900">{label}</p>
          </button>
        ))}
      </div>

      {savedMethods.filter((savedMethod) => savedMethod.type === method).length > 0 && (
        <div className="mt-6 rounded-2xl border border-orange-100 bg-orange-50 p-4">
          <p className="text-sm font-semibold text-gray-900 mb-3">Saved Payment Methods</p>
          <div className="space-y-2">
            {savedMethods
              .filter((savedMethod) => savedMethod.type === method)
              .map((savedMethod) => (
                <label key={savedMethod.id} className="flex items-center gap-3 rounded-xl bg-white px-4 py-3 border border-orange-100">
                  <input
                    type="radio"
                    name={`saved-${method}`}
                    checked={selectedSavedMethodId === savedMethod.id}
                    onChange={() => setSelectedSavedMethodId(savedMethod.id)}
                  />
                  <div className="text-sm">
                    <p className="font-semibold text-gray-900">
                      {savedMethod.type === "card"
                        ? `${savedMethod.card_brand || "Card"} ending in ${savedMethod.card_last4}`
                        : savedMethod.upi_id}
                      {savedMethod.is_default ? " (Default)" : ""}
                    </p>
                    <p className="text-gray-500">
                      {savedMethod.type === "card"
                        ? `${savedMethod.card_holder_name} • Exp ${savedMethod.card_expiry}`
                        : savedMethod.upi_nickname || "Saved UPI"}
                    </p>
                  </div>
                </label>
              ))}
            <button
              type="button"
              onClick={() => setSelectedSavedMethodId("")}
              className="text-sm font-semibold text-orange-600"
            >
              + Use a different method
            </button>
          </div>
        </div>
      )}

      {!selectedSavedMethodId && (
      <div className="mt-6 overflow-hidden rounded-2xl bg-gradient-to-br from-orange-500 via-orange-400 to-amber-300 p-5 text-white perspective-1000">
        <div className={`relative min-h-44 transition-transform duration-500 [transform-style:preserve-3d] ${isCardBackVisible ? "[transform:rotateY(180deg)]" : ""}`}>
          <div className="absolute inset-0 [backface-visibility:hidden]">
            <div className="flex items-start justify-between">
              <p className="text-xs uppercase tracking-[0.3em] text-orange-100">{method === "card" ? cardBrand : "CampusRunner Pay"}</p>
              <Lock className="w-5 h-5 text-orange-50" />
            </div>
            <div className="mt-10 text-2xl font-semibold tracking-[0.2em]">
              {formatCardNumber(cardNumber || "4242424242424242")}
            </div>
            <div className="mt-8 flex items-end justify-between">
              <div>
                <p className="text-[10px] uppercase tracking-[0.3em] text-orange-100">Card Holder</p>
                <p className="mt-1 font-semibold">{cardHolderName || "Campus Runner"}</p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-[0.3em] text-orange-100">Expiry</p>
                <p className="mt-1 font-semibold">{cardExpiry || "08/2027"}</p>
              </div>
            </div>
          </div>
          <div className="absolute inset-0 [backface-visibility:hidden] [transform:rotateY(180deg)]">
            <div className="h-10 bg-slate-900/80 -mx-5 mt-4" />
            <div className="mt-6 rounded-lg bg-white/90 px-4 py-3 text-right text-slate-800">
              {(cardPinRef.current?.value || "").replace(/./g, "•") || "••••"}
            </div>
            <p className="mt-5 text-xs text-orange-50">PIN is only used for this submit action and is never stored.</p>
          </div>
        </div>
      </div>
      )}

      {method === "cod" && !selectedSavedMethodId && (
        <div className="mt-6 rounded-2xl bg-orange-50 border border-orange-100 p-5">
          <p className="font-semibold text-gray-900">Pay ₹{amount.toFixed(2)} when your order arrives.</p>
          <p className="text-sm text-gray-600 mt-2">Our runner will collect cash at your door. Please keep exact change ready.</p>
        </div>
      )}

      {method === "upi" && !selectedSavedMethodId && (
        <div className="mt-6 space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Your UPI ID</label>
            <input
              type="text"
              value={upiId}
              onChange={(event) => setUpiId(event.target.value)}
              placeholder="yourname@upi"
              className={`w-full rounded-xl border px-4 py-3 focus:outline-none ${
                upiValid ? "border-gray-300 focus:border-orange-400" : "border-red-300 focus:border-red-400"
              }`}
            />
            {upiId && (
              <p className={`mt-2 text-sm ${upiValid ? "text-green-600" : "text-red-600"}`}>
                {upiValid ? "UPI ID looks good." : "Please enter a valid UPI ID."}
              </p>
            )}
          </div>
          <div className="rounded-2xl bg-blue-50 border border-blue-100 p-4 text-sm text-blue-700">
            You’ll complete payment in Razorpay. Supported apps: GPay, PhonePe, Paytm, BHIM.
          </div>
          <div className="flex flex-wrap gap-2">
            {["GPay", "PhonePe", "Paytm", "BHIM"].map((logo) => (
              <span key={logo} className="rounded-full bg-white border border-gray-200 px-3 py-1 text-sm text-gray-700">{logo}</span>
            ))}
          </div>
        </div>
      )}

      {method === "card" && !selectedSavedMethodId && (
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          {savedCardMeta?.card_last4 && (
            <div className="md:col-span-2 rounded-2xl border border-green-100 bg-green-50 px-4 py-3 text-sm text-green-700">
              Saved card available: ending in {savedCardMeta.card_last4}. Enter the card number and PIN to pay again safely.
            </div>
          )}
          <div className="md:col-span-2">
            <label className="block text-sm font-semibold text-gray-700 mb-2">Card Number</label>
            <input
              type="text"
              value={cardNumber}
              onChange={(event) => setCardNumber(formatCardNumber(event.target.value))}
              placeholder="4242 4242 4242 4242"
              className={`w-full rounded-xl border px-4 py-3 focus:outline-none ${
                cardValid ? "border-gray-300 focus:border-orange-400" : "border-red-300 focus:border-red-400"
              }`}
            />
            {cardNumber && (
              <p className={`mt-2 text-sm ${cardValid ? "text-green-600" : "text-red-600"}`}>
                {cardValid ? "Card number passed Luhn check." : "Card number failed Luhn validation."}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Cardholder Name</label>
            <input
              type="text"
              value={cardHolderName}
              onChange={(event) => setCardHolderName(event.target.value)}
              placeholder="Rahul Sharma"
              className="w-full rounded-xl border border-gray-300 px-4 py-3 focus:outline-none focus:border-orange-400"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Expiry</label>
            <input
              type="text"
              value={cardExpiry}
              onChange={(event) => setCardExpiry(event.target.value.replace(/[^\d/]/g, "").slice(0, 7))}
              placeholder="08/2027"
              className="w-full rounded-xl border border-gray-300 px-4 py-3 focus:outline-none focus:border-orange-400"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-semibold text-gray-700 mb-2">PIN</label>
            <input
              ref={cardPinRef}
              type="password"
              inputMode="numeric"
              maxLength={6}
              onFocus={() => setIsCardBackVisible(true)}
              onBlur={() => setIsCardBackVisible(false)}
              placeholder="4 to 6 digits"
              className="w-full rounded-xl border border-gray-300 px-4 py-3 focus:outline-none focus:border-orange-400"
            />
          </div>
        </div>
      )}

      {localError && <p className="mt-4 text-sm text-red-600">{localError}</p>}

      <button
        type="button"
        disabled={disabled || isLoading}
        onClick={submit}
        className="mt-6 w-full rounded-xl bg-gradient-to-r from-orange-500 to-orange-600 px-5 py-4 text-white font-bold shadow-lg hover:from-orange-600 hover:to-orange-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isLoading ? "Processing payment..." : method === "cod" ? `Place Order ₹${amount.toFixed(2)}` : method === "upi" ? `Pay ₹${amount.toFixed(2)}` : `Pay Securely ₹${amount.toFixed(2)}`}
      </button>

      <div className="mt-4 flex items-center gap-2 text-sm text-gray-500">
        <CheckCircle2 className="w-4 h-4 text-green-600" />
        <span>Your card number is encrypted. PIN is never stored.</span>
      </div>
    </div>
  );
}
