import { useState } from "react";
import { CreditCard, Wallet, Building2, Smartphone, Plus, Check, ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router";

export function Payment() {
  const navigate = useNavigate();
  const [selectedMethod, setSelectedMethod] = useState<string>("upi");

  const paymentMethods = [
    {
      id: "upi",
      name: "UPI",
      icon: <Smartphone className="w-6 h-6" />,
      description: "Pay via Google Pay, PhonePe, Paytm",
      saved: ["student@oksbi", "9876543210@paytm"]
    },
    {
      id: "card",
      name: "Credit/Debit Card",
      icon: <CreditCard className="w-6 h-6" />,
      description: "Visa, Mastercard, RuPay",
      saved: ["**** **** **** 4532", "**** **** **** 8901"]
    },
    {
      id: "netbanking",
      name: "Net Banking",
      icon: <Building2 className="w-6 h-6" />,
      description: "All major banks supported",
      saved: []
    },
    {
      id: "wallet",
      name: "Wallet",
      icon: <Wallet className="w-6 h-6" />,
      description: "Paytm, PhonePe, Amazon Pay",
      saved: ["Paytm Wallet (₹1,250)"]
    }
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back</span>
        </button>
        <h1 className="text-3xl text-gray-900 mb-2">Payment Methods</h1>
        <p className="text-gray-600">Manage your payment options for quick checkout</p>
      </div>

      {/* Payment Methods */}
      <div className="space-y-4">
        {paymentMethods.map((method) => (
          <div key={method.id} className="bg-white rounded-xl shadow-md overflow-hidden">
            <div
              className={`p-6 cursor-pointer transition-colors ${
                selectedMethod === method.id ? "bg-orange-50 border-2 border-orange-500" : "border-2 border-transparent"
              }`}
              onClick={() => setSelectedMethod(method.id)}
            >
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-lg ${
                  selectedMethod === method.id ? "bg-orange-500 text-white" : "bg-gray-100 text-gray-600"
                }`}>
                  {method.icon}
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="text-lg text-gray-900">{method.name}</h3>
                    {selectedMethod === method.id && (
                      <div className="w-6 h-6 bg-orange-500 rounded-full flex items-center justify-center">
                        <Check className="w-4 h-4 text-white" />
                      </div>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mb-3">{method.description}</p>

                  {/* Saved Payment Methods */}
                  {method.saved.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-xs text-gray-500">Saved {method.name}s:</p>
                      {method.saved.map((saved, idx) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between bg-gray-50 rounded-lg px-3 py-2"
                        >
                          <span className="text-sm text-gray-700">{saved}</span>
                          <button className="text-xs text-orange-600 hover:text-orange-700">
                            Use
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Add New Button */}
                  <button className="mt-3 flex items-center gap-2 text-sm text-orange-600 hover:text-orange-700">
                    <Plus className="w-4 h-4" />
                    <span>Add New {method.name}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Default Payment Method */}
      <div className="mt-8 bg-orange-50 border border-orange-200 rounded-xl p-6">
        <h3 className="text-lg text-gray-900 mb-4">Default Payment Method</h3>
        <p className="text-sm text-gray-600 mb-4">
          Set a default payment method for faster checkout. You can always change it during order placement.
        </p>
        <button className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-3 rounded-lg transition-colors">
          Set Default: {paymentMethods.find(m => m.id === selectedMethod)?.name}
        </button>
      </div>

      {/* Payment Security Info */}
      <div className="mt-6 bg-white rounded-xl shadow-md p-6">
        <h3 className="text-lg text-gray-900 mb-4">Payment Security</h3>
        <div className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
            <div>
              <p className="text-gray-900">Secure Transactions</p>
              <p className="text-sm text-gray-600">All payments are encrypted and secure</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
            <div>
              <p className="text-gray-900">No Card Details Stored</p>
              <p className="text-sm text-gray-600">We use secure payment gateways</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
            <div>
              <p className="text-gray-900">PCI DSS Compliant</p>
              <p className="text-sm text-gray-600">Industry standard security measures</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
