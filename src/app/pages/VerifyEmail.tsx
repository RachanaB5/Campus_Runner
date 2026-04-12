import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router";
import { AlertCircle, Loader, Mail, ShoppingBag } from "lucide-react";
import { authAPI } from "../services/api";
import { useAuth } from "../context/AuthContext";

const COOLDOWN_DEFAULT = 60;

export function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { verifySignupOtp, isLoggedIn } = useAuth();
  const emailParam = (searchParams.get("email") || "").trim().toLowerCase();

  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [cooldown, setCooldown] = useState(0);

  useEffect(() => {
    if (isLoggedIn) {
      navigate("/", { replace: true });
    }
  }, [isLoggedIn, navigate]);

  useEffect(() => {
    if (cooldown <= 0) return;
    const t = window.setInterval(() => {
      setCooldown((c) => (c <= 1 ? 0 : c - 1));
    }, 1000);
    return () => window.clearInterval(t);
  }, [cooldown]);

  const startCooldown = useCallback((seconds: number) => {
    setCooldown(Math.max(0, seconds));
  }, []);

  const handleResend = async () => {
    if (!emailParam || cooldown > 0) return;
    setError("");
    setIsResending(true);
    try {
      await authAPI.resendOtp({ email: emailParam, purpose: "signup" });
      startCooldown(COOLDOWN_DEFAULT);
    } catch (err: any) {
      if (err.code === "COOLDOWN" && typeof err.retry_after === "number") {
        startCooldown(err.retry_after);
      }
      setError(err?.message || "Could not resend code");
    } finally {
      setIsResending(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!emailParam) {
      setError("Missing email. Go back to sign up and try again.");
      return;
    }
    const code = otp.trim();
    if (code.length < 6) {
      setError("Enter the 6-digit code from your email");
      return;
    }
    setIsSubmitting(true);
    try {
      await verifySignupOtp(emailParam, code);
      navigate("/", { replace: true });
    } catch (err: any) {
      setError(err?.message || "Verification failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  useEffect(() => {
    if (emailParam) {
      startCooldown(COOLDOWN_DEFAULT);
    }
  }, [emailParam, startCooldown]);

  if (!emailParam) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
          <p className="text-gray-700 mb-4">No email provided for verification.</p>
          <Link to="/login" className="text-orange-600 font-semibold">Back to login</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-gradient-to-br from-orange-500 to-red-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
            <ShoppingBag className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl text-gray-900 mb-2">Verify your email</h1>
          <p className="text-gray-600 text-sm">
            We sent a 6-digit code to <span className="font-medium text-gray-800">{emailParam}</span>
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-700 mb-2">Verification code</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  maxLength={6}
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
                  placeholder="000000"
                  className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500 tracking-[0.35em] text-center text-lg font-semibold"
                />
              </div>
              <p className="text-xs text-gray-500 mt-2">Code expires in 10 minutes.</p>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start gap-2">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-orange-500 hover:bg-orange-600 disabled:bg-orange-400 text-white py-3 rounded-lg transition-colors flex items-center justify-center gap-2 font-medium"
            >
              {isSubmitting && <Loader className="w-4 h-4 animate-spin" />}
              Verify and continue
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-gray-600">
            <button
              type="button"
              disabled={cooldown > 0 || isResending}
              onClick={handleResend}
              className="text-orange-600 hover:text-orange-700 font-medium disabled:text-gray-400 disabled:cursor-not-allowed"
            >
              {isResending ? "Sending…" : cooldown > 0 ? `Resend code in ${cooldown}s` : "Resend code"}
            </button>
          </div>

          <p className="text-center text-gray-600 mt-6 text-sm">
            <Link to="/login" className="text-orange-500 hover:text-orange-600 font-medium">Back to login</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
