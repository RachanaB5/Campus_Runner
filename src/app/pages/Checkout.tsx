import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { 
  AlertCircle, MapPin, Phone, Truck, CheckCircle2, 
  ArrowLeft, Loader, Clock, MapIcon, DollarSign, 
  Shield, Zap, ChevronRight, Info
} from "lucide-react";
import { api, paymentAPI } from "../services/api";
import { PaymentMethodSelector } from "../components/PaymentMethodSelector";

interface ValidationState {
  address: boolean;
  city: boolean;
  pincode: boolean;
  phone: boolean;
  payment: boolean;
}

interface ValidationErrors {
  address?: string;
  city?: string;
  pincode?: string;
  phone?: string;
  payment?: string;
}

export function Checkout() {
  const navigate = useNavigate();
  const { cart, getTotalPrice, clearCart, isLoading: cartLoading } = useCart();
  const { user } = useAuth();
  
  // Form state
  const [address, setAddress] = useState("");
  const [city, setCity] = useState("");
  const [pincode, setPincode] = useState("");
  const [phone, setPhone] = useState(user?.phone || "");
  const [instructions, setInstructions] = useState("");
  const [paymentMethod, setPaymentMethod] = useState<"cod" | "upi" | "card">("cod");
  
  // UI state
  const [isLoading, setIsLoading] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [orderData, setOrderData] = useState<any>(null);
  const [savedMethods, setSavedMethods] = useState<any[]>([]);
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});
  const [validationState, setValidationState] = useState<ValidationState>({
    address: false,
    city: false,
    pincode: false,
    phone: false,
    payment: true,
  });

  const cartItems = cart?.items || [];
  const totalPrice = getTotalPrice();
  const taxes = Math.round(totalPrice * 0.05 * 100) / 100;
  const deliveryFee = totalPrice > 500 ? 0 : 50;
  const finalTotal = totalPrice + taxes + deliveryFee;

  useEffect(() => {
    api.getSavedPaymentMethods().then((response) => {
      setSavedMethods(response.payment_methods || []);
    }).catch(() => setSavedMethods([]));
  }, []);

  // Real-time validation
  const validateAddress = (value: string) => {
    setAddress(value);
    const isValid = value.trim().length >= 10;
    setValidationState(prev => ({ ...prev, address: isValid }));
    if (!isValid && value) {
      setValidationErrors(prev => ({ ...prev, address: "Address must be at least 10 characters" }));
    } else {
      setValidationErrors(prev => ({ ...prev, address: undefined }));
    }
  };

  const validateCity = (value: string) => {
    setCity(value);
    const isValid = value.trim().length >= 2;
    setValidationState(prev => ({ ...prev, city: isValid }));
    if (!isValid && value) {
      setValidationErrors(prev => ({ ...prev, city: "City name must be at least 2 characters" }));
    } else {
      setValidationErrors(prev => ({ ...prev, city: undefined }));
    }
  };

  const validatePincode = (value: string) => {
    setPincode(value);
    const isValid = /^\d{5,6}$/.test(value);
    setValidationState(prev => ({ ...prev, pincode: isValid }));
    if (!isValid && value) {
      setValidationErrors(prev => ({ ...prev, pincode: "Pincode must be 5-6 digits" }));
    } else {
      setValidationErrors(prev => ({ ...prev, pincode: undefined }));
    }
  };

  const validatePhone = (value: string) => {
    setPhone(value);
    const cleaned = value.replace(/[\s\-()]/g, "");
    const isValid = /^\d{10,}$/.test(cleaned);
    setValidationState(prev => ({ ...prev, phone: isValid }));
    if (!isValid && value) {
      setValidationErrors(prev => ({ ...prev, phone: "Phone number must be 10+ digits" }));
    } else {
      setValidationErrors(prev => ({ ...prev, phone: undefined }));
    }
  };

  const isFormValid = () => {
    return (
      validationState.address &&
      validationState.city &&
      validationState.pincode &&
      validationState.phone &&
      Boolean(paymentMethod) &&
      cartItems.length > 0
    );
  };

  const loadRazorpayScript = async () => {
    if ((window as any).Razorpay) {
      return true;
    }

    return new Promise<boolean>((resolve) => {
      const script = document.createElement("script");
      script.src = "https://checkout.razorpay.com/v1/checkout.js";
      script.onload = () => resolve(true);
      script.onerror = () => resolve(false);
      document.body.appendChild(script);
    });
  };

  const createOrderDraft = async () => {
    const items = cartItems.map((item) => ({
      food_id: item.food_id,
      quantity: item.quantity,
      price: item.price,
      customizations: item.customizations,
    }));

    const response = await fetch(`${api.API_BASE_URL}/checkout/confirm`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${api.getToken()}`,
      },
      body: JSON.stringify({
        items,
        delivery_address: address,
        delivery_city: city,
        delivery_pincode: pincode,
        customer_phone: phone,
        delivery_instructions: instructions,
        payment_method: paymentMethod,
        subtotal: totalPrice,
        tax_amount: taxes,
        delivery_fee: deliveryFee,
        final_total: finalTotal,
      }),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.error || data.message || "Failed to create order");
    }

    return response.json();
  };

  const openRazorpayCheckout = async (orderDraft: any, upiSession: any) => {
    if (upiSession.mock_checkout) {
      await paymentAPI.verifyUpi({
        razorpay_order_id: upiSession.razorpay_order_id,
        razorpay_payment_id: upiSession.mock_payment_id,
        razorpay_signature: upiSession.mock_signature,
      });
      return;
    }

    const loaded = await loadRazorpayScript();
    if (!loaded || !(window as any).Razorpay) {
      throw new Error("Razorpay checkout could not be loaded");
    }

    return new Promise<void>((resolve, reject) => {
      const razorpay = new (window as any).Razorpay({
        key: upiSession.razorpay_key_id,
        amount: upiSession.amount,
        currency: upiSession.currency,
        order_id: upiSession.razorpay_order_id,
        name: "CampusRunner",
        description: `Order ${orderDraft.order_number}`,
        image: "/logo.png",
        prefill: {
          name: user?.name || "",
          email: user?.email || "",
          contact: phone,
        },
        theme: { color: "#F97316" },
        method: {
          upi: true,
          card: false,
          netbanking: false,
          wallet: false,
        },
        handler: async (response: any) => {
          try {
            await paymentAPI.verifyUpi({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            });
            resolve();
          } catch (error) {
            reject(error);
          }
        },
        modal: {
          ondismiss: () => reject(new Error("Payment was cancelled")),
        },
      });

      razorpay.open();
    });
  };

  const handlePaymentSubmit = async (
    method: "cod" | "upi" | "card",
    payload: {
      upi_id?: string;
      card_number?: string;
      card_holder_name?: string;
      card_expiry?: string;
      card_pin?: string;
      saved_method_id?: string;
    },
  ) => {
    setSubmitError("");
    setPaymentMethod(method);

    if (!isFormValid()) {
      setSubmitError("Please fill in all required fields correctly");
      return;
    }

    setIsLoading(true);

    try {
      const draft = await createOrderDraft();
      const orderId = draft.order?.id;

      if (!orderId) {
        throw new Error("Order was created without an id");
      }

      if (method === "cod") {
        await paymentAPI.initiate({ order_id: orderId, method: "cod" });
      } else if (method === "card") {
        const cardResponse = await paymentAPI.initiate({
          order_id: orderId,
          method: "card",
          saved_method_id: payload.saved_method_id,
          card_number: payload.card_number,
          card_holder_name: payload.card_holder_name,
          card_expiry: payload.card_expiry,
          card_pin: payload.card_pin,
        });
        localStorage.setItem("saved_card_meta", JSON.stringify({
          card_last4: cardResponse.card_last4,
          card_holder_name: payload.card_holder_name,
          card_expiry: payload.card_expiry,
        }));
      } else {
        const upiSession = await paymentAPI.initiate({
          order_id: orderId,
          method: "upi",
          saved_method_id: payload.saved_method_id,
          upi_id: payload.upi_id,
        });
        await openRazorpayCheckout(draft, upiSession);
      }

      await clearCart();
      navigate(`/orders/${draft.order_id || orderId}/track`, {
        replace: true,
        state: {
          order_id: draft.order_id || orderId,
          token_number: draft.token_number || draft.order_number,
          delivery_otp: draft.delivery_otp,
          pickup_otp: draft.pickup_otp,
          items: cartItems,
          total: finalTotal,
        },
      });
    } catch (err: any) {
      setSubmitError(err.message || "Failed to complete payment. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  if (cartItems.length === 0 && !showConfirmation) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-12 px-4">
        <div className="max-w-2xl mx-auto">
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-2 text-orange-600 hover:text-orange-700 mb-8 font-semibold transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Menu
          </button>
          
          <div className="text-center py-20">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-orange-100 rounded-full mb-6">
              <AlertCircle className="w-10 h-10 text-orange-500" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-3">Your Cart is Empty</h2>
            <p className="text-gray-600 mb-8 text-lg">Add delicious items to get started with your order</p>
            <button
              onClick={() => navigate("/")}
              className="inline-flex items-center gap-2 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white px-8 py-3 rounded-lg font-semibold transition-all hover:shadow-lg"
            >
              Browse Menu
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (showConfirmation && orderData) {
    return <OrderConfirmation orderData={orderData} navigate={navigate} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-12 px-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <button
          onClick={() => navigate("/")}
          className="flex items-center gap-2 text-orange-600 hover:text-orange-700 mb-8 font-semibold transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Menu
        </button>

        {/* Progress Indicator */}
        <div className="mb-10">
          <div className="flex items-center justify-between max-w-md">
            <div className="flex flex-col items-center">
              <div className="w-10 h-10 bg-orange-500 text-white rounded-full flex items-center justify-center font-bold">
                1
              </div>
              <span className="text-sm font-semibold text-gray-900 mt-2">Delivery Info</span>
            </div>
            <div className="flex-1 h-1 bg-orange-300 mx-3"></div>
            <div className="flex flex-col items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                Object.values(validationState).every(v => v) 
                  ? 'bg-orange-500 text-white' 
                  : 'bg-gray-200 text-gray-600'
              }`}>
                2
              </div>
              <span className="text-sm font-semibold text-gray-700 mt-2">Payment</span>
            </div>
            <div className={`flex-1 h-1 mx-3 ${Object.values(validationState).every(v => v) ? 'bg-orange-300' : 'bg-gray-200'}`}></div>
            <div className="flex flex-col items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                isFormValid()
                  ? 'bg-orange-500 text-white' 
                  : 'bg-gray-200 text-gray-600'
              }`}>
                3
              </div>
              <span className="text-sm font-semibold text-gray-700 mt-2">Confirm</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Form */}
          <div className="lg:col-span-2 space-y-6">
            <div className="space-y-6">
              {/* Delivery Address Section */}
              <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-8 border border-gray-100">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                    <MapPin className="w-6 h-6 text-orange-600" />
                  </div>
                  <h2 className="text-xl font-bold text-gray-900">Delivery Address</h2>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Full Address *
                    </label>
                    <input
                      type="text"
                      value={address}
                      onChange={(e) => validateAddress(e.target.value)}
                      onBlur={() => {
                        if (address && !validationState.address) {
                          setValidationErrors(prev => ({ 
                            ...prev, 
                            address: "Address must be at least 10 characters" 
                          }));
                        }
                      }}
                      placeholder="E.g., Block A, Room 302, Hostel Building"
                      className={`w-full px-4 py-3 rounded-lg border-2 transition-colors focus:outline-none ${
                        validationState.address
                          ? 'border-green-400 focus:border-green-500 bg-green-50'
                          : address
                          ? 'border-red-400 focus:border-red-500 bg-red-50'
                          : 'border-gray-300 focus:border-orange-500'
                      }`}
                    />
                    {validationErrors.address && (
                      <p className="text-red-600 text-xs mt-1 flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" />
                        {validationErrors.address}
                      </p>
                    )}
                    {validationState.address && (
                      <p className="text-green-600 text-xs mt-1 flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" />
                        Address looks good!
                      </p>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">City *</label>
                      <input
                        type="text"
                        value={city}
                        onChange={(e) => validateCity(e.target.value)}
                        onBlur={() => {
                          if (city && !validationState.city) {
                            setValidationErrors(prev => ({ 
                              ...prev, 
                              city: "City name must be at least 2 characters" 
                            }));
                          }
                        }}
                        placeholder="E.g., Bangalore"
                        className={`w-full px-4 py-3 rounded-lg border-2 transition-colors focus:outline-none ${
                          validationState.city
                            ? 'border-green-400 focus:border-green-500 bg-green-50'
                            : city
                            ? 'border-red-400 focus:border-red-500 bg-red-50'
                            : 'border-gray-300 focus:border-orange-500'
                        }`}
                      />
                      {validationErrors.city && (
                        <p className="text-red-600 text-xs mt-1">{validationErrors.city}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">Pincode *</label>
                      <input
                        type="text"
                        value={pincode}
                        onChange={(e) => validatePincode(e.target.value.replace(/\D/g, ''))}
                        onBlur={() => {
                          if (pincode && !validationState.pincode) {
                            setValidationErrors(prev => ({ 
                              ...prev, 
                              pincode: "Pincode must be 5-6 digits" 
                            }));
                          }
                        }}
                        placeholder="E.g., 560001"
                        maxLength={6}
                        className={`w-full px-4 py-3 rounded-lg border-2 transition-colors focus:outline-none ${
                          validationState.pincode
                            ? 'border-green-400 focus:border-green-500 bg-green-50'
                            : pincode
                            ? 'border-red-400 focus:border-red-500 bg-red-50'
                            : 'border-gray-300 focus:border-orange-500'
                        }`}
                      />
                      {validationErrors.pincode && (
                        <p className="text-red-600 text-xs mt-1">{validationErrors.pincode}</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Contact Information */}
              <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-8 border border-gray-100">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                    <Phone className="w-6 h-6 text-orange-600" />
                  </div>
                  <h2 className="text-xl font-bold text-gray-900">Contact Information</h2>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Phone Number *
                    </label>
                    <input
                      type="tel"
                      value={phone}
                      onChange={(e) => validatePhone(e.target.value)}
                      onBlur={() => {
                        if (phone && !validationState.phone) {
                          setValidationErrors(prev => ({ 
                            ...prev, 
                            phone: "Phone number must be 10+ digits" 
                          }));
                        }
                      }}
                      placeholder="E.g., +91 98765 43210"
                      className={`w-full px-4 py-3 rounded-lg border-2 transition-colors focus:outline-none ${
                        validationState.phone
                          ? 'border-green-400 focus:border-green-500 bg-green-50'
                          : phone
                          ? 'border-red-400 focus:border-red-500 bg-red-50'
                          : 'border-gray-300 focus:border-orange-500'
                      }`}
                    />
                    {validationErrors.phone && (
                      <p className="text-red-600 text-xs mt-1">{validationErrors.phone}</p>
                    )}
                    {validationState.phone && (
                      <p className="text-green-600 text-xs mt-1 flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" />
                        Number verified!
                      </p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Delivery Instructions (Optional)
                    </label>
                    <textarea
                      value={instructions}
                      onChange={(e) => setInstructions(e.target.value)}
                      placeholder="E.g., Ring bell twice, leave at door, call on arrival, etc."
                      rows={3}
                      className="w-full px-4 py-3 rounded-lg border-2 border-gray-300 focus:outline-none focus:border-orange-500 transition-colors"
                    />
                  </div>
                </div>
              </div>

              <PaymentMethodSelector
                amount={finalTotal}
                isLoading={isLoading}
                disabled={!isFormValid()}
                savedMethods={savedMethods}
                onSubmit={handlePaymentSubmit}
              />

              {/* Error Message */}
              {submitError && (
                <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 flex items-start gap-3">
                  <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-red-900">Order Error</p>
                    <p className="text-sm text-red-700 mt-1">{submitError}</p>
                  </div>
                </div>
              )}

            </div>
          </div>

          {/* Order Summary Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden sticky top-4">
              {/* Header */}
              <div className="bg-gradient-to-r from-orange-500 to-orange-600 p-6 text-white">
                <h3 className="text-xl font-bold flex items-center gap-2">
                  <Truck className="w-5 h-5" />
                  Order Summary
                </h3>
              </div>

              {/* Items */}
              <div className="p-6 space-y-3 max-h-64 overflow-y-auto">
                {cartItems.map((item) => (
                  <div key={item.id} className="flex justify-between items-start pb-3 border-b border-gray-100 last:border-0">
                    <div>
                      <p className="font-medium text-gray-900">{item.food_name}</p>
                      <p className="text-sm text-gray-500">Qty: {item.quantity}</p>
                    </div>
                    <span className="font-semibold text-gray-900">₹{(item.price * item.quantity).toFixed(2)}</span>
                  </div>
                ))}
              </div>

              {/* Pricing Breakdown */}
              <div className="p-6 space-y-3 border-t border-gray-200">
                <div className="flex justify-between text-gray-700">
                  <span>Subtotal</span>
                  <span className="font-semibold">₹{totalPrice.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-gray-700">
                  <span>Taxes (5%)</span>
                  <span className="font-semibold">₹{taxes.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-700">Delivery Fee</span>
                  <span className={`font-semibold ${deliveryFee === 0 ? 'text-green-600' : 'text-gray-900'}`}>
                    {deliveryFee === 0 ? '✓ FREE' : `₹${deliveryFee.toFixed(2)}`}
                  </span>
                </div>
              </div>

              {/* Total */}
              <div className="p-6 bg-gradient-to-r from-orange-50 to-orange-100 border-t-2 border-orange-200">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-gray-900">Total Amount</span>
                  <span className="text-2xl font-bold text-orange-600">₹{finalTotal.toFixed(2)}</span>
                </div>
              </div>

              {/* Info Box */}
              {totalPrice < 500 && (
                <div className="p-4 bg-green-50 border-t border-green-200 flex items-start gap-3">
                  <Info className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-green-700">
                    <span className="font-semibold">Add ₹{(500 - totalPrice).toFixed(0)} more</span> for free delivery!
                  </p>
                </div>
              )}

              {/* Security Badge */}
              <div className="p-4 bg-blue-50 border-t border-blue-200 flex items-center gap-2 justify-center text-blue-700">
                <Shield className="w-4 h-4" />
                <span className="text-sm font-semibold">Secure Payment</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Order Confirmation Component
function OrderConfirmation({ orderData, navigate }: any) {
  const estimatedDelivery = orderData.estimated_delivery 
    ? new Date(orderData.estimated_delivery).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      })
    : 'N/A';

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 py-12 px-4 flex items-center justify-center">
      <div className="max-w-md mx-auto">
        <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
          {/* Success Header */}
          <div className="bg-gradient-to-r from-green-500 to-green-600 p-8 text-center text-white">
            <div className="w-20 h-20 mx-auto mb-4 bg-white rounded-full flex items-center justify-center animate-bounce">
              <CheckCircle2 className="w-12 h-12 text-green-600" />
            </div>
            <h1 className="text-3xl font-bold">Order Confirmed!</h1>
            <p className="text-green-100 mt-2">Your meal is on the way</p>
          </div>

          {/* Order Details */}
          <div className="p-8 space-y-6">
            {/* Order Number */}
            <div className="text-center">
              <p className="text-gray-600 text-sm mb-1">Order Number</p>
              <p className="text-3xl font-bold text-gray-900">{orderData.order_number}</p>
            </div>

            {/* Status */}
            <div className="bg-gradient-to-r from-orange-50 to-amber-50 rounded-lg p-4 text-center border border-orange-200">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Clock className="w-5 h-5 text-orange-600" />
                <span className="font-semibold text-orange-900">Estimated Delivery</span>
              </div>
              <p className="text-2xl font-bold text-orange-600">{estimatedDelivery}</p>
            </div>

            {/* Delivery Address */}
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <div className="flex items-start gap-3">
                <MapPin className="w-5 h-5 text-blue-600 flex-shrink-0 mt-1" />
                <div>
                  <p className="font-semibold text-gray-900">Delivery Address</p>
                  <p className="text-sm text-gray-700 mt-1">{orderData.order.delivery_address}</p>
                </div>
              </div>
            </div>

            {/* Order Items Summary */}
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="font-semibold text-gray-900 mb-3">Items in Your Order</p>
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {orderData.order.items?.map((item: any, idx: number) => (
                  <div key={idx} className="flex justify-between text-sm text-gray-700">
                    <span>{item.quantity}x {item.food_name}</span>
                    <span className="font-medium">₹{item.total_price.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Total */}
            <div className="border-t-2 pt-4">
              <div className="flex justify-between items-center">
                <span className="text-xl font-bold text-gray-900">Total Amount</span>
                <span className="text-2xl font-bold text-green-600">₹{orderData.order.total_amount.toFixed(2)}</span>
              </div>
            </div>

            {/* Confirmation Info */}
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <p className="text-sm text-blue-900">
                ✓ A confirmation email has been sent to your registered email address. You can track your order status anytime.
              </p>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3 pt-4">
              <button
                onClick={() => navigate('/orders')}
                className="w-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-bold py-3 rounded-lg transition-all hover:shadow-lg flex items-center justify-center gap-2"
              >
                <Truck className="w-5 h-5" />
                Track Order
              </button>
              <button
                onClick={() => navigate('/')}
                className="w-full bg-gray-200 hover:bg-gray-300 text-gray-900 font-bold py-3 rounded-lg transition-all"
              >
                Continue Shopping
              </button>
            </div>

            {/* Info Message */}
            <p className="text-center text-sm text-gray-600">
              Choose an option above to continue, or close this page anytime.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
