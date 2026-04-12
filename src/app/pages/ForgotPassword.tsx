import { useEffect, useState } from "react";
import { Link } from "react-router";
import { AlertCircle, Loader, Lock, Mail, ShoppingBag } from "lucide-react";
import { authAPI } from "../services/api";

type Step = "email" | "otp" | "password";

const COOLDOWN_DEFAULT = 60;

export function ForgotPassword() {
  const [step, setStep] = useState<Step>("email");
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [cooldown, setCooldown] = useState(0);
  const [message, setMessage] = useState("");
  const [devOtp, setDevOtp] = useState("");

  useEffect(() => {
    if (cooldown <= 0) return;
    const t = window.setInterval(() => {
      setCooldown((c) => (c <= 1 ? 0 : c - 1));
    }, 1000);
    return () => window.clearInterval(t);
  }, [cooldown]);

  const validateEmail = (value: string) => value.trim().toLowerCase().endsWith("@rvu.edu.in");

  const sendResetEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setMessage("");
    const normalized = email.trim().toLowerCase();
    if (!validateEmail(normalized)) {
      setError("Please use your RV University email (@rvu.edu.in)");
      return;
    }
    setIsLoading(true);
    try {
      const response = await authAPI.forgotPassword(normalized) as { email_sent?: boolean; dev_otp?: string; message?: string };
      setEmail(normalized);
      setDevOtp(response.dev_otp || "");
      setMessage(response.email_sent ? "Reset code sent to your email." : (response.message || "Reset code generated, but email could not be sent."));
      setCooldown(COOLDOWN_DEFAULT);
      setStep("otp");
    } catch (err: any) {
      if (err.code === "COOLDOWN" && typeof err.retry_after === "number") {
        setCooldown(err.retry_after);
      }
      setError(err?.message || "Could not send reset email");
    } finally {
      setIsLoading(false);
    }
  };

  const resendOtp = async () => {
    if (cooldown > 0 || !email) return;
    setError("");
    setMessage("");
    setIsLoading(true);
    try {
      const response = await authAPI.resendOtp({ email, purpose: "password_reset" }) as { email_sent?: boolean; dev_otp?: string; message?: string };
      setDevOtp(response.dev_otp || "");
      setMessage(response.email_sent ? "Reset code resent to your email." : (response.message || "Reset code regenerated, but email could not be sent."));
      setCooldown(COOLDOWN_DEFAULT);
    } catch (err: any) {
      if (err.code === "COOLDOWN" && typeof err.retry_after === "number") {
        setCooldown(err.retry_after);
      }
      setError(err?.message || "Could not resend code");
    } finally {
      setIsLoading(false);
    }
  };

  const goToPasswordStep = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (otp.trim().length < 6) {
      setError("Enter the 6-digit code from your email");
      return;
    }
    setStep("password");
  };

  const submitNewPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    setIsLoading(true);
    try {
      await authAPI.resetPassword({ email, otp: otp.trim(), password });
      window.location.href = "/login?reset=1";
    } catch (err: any) {
      setError(err?.message || "Could not reset password");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-gradient-to-br from-orange-500 to-red-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg">
            <ShoppingBag className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl text-gray-900 mb-2">Reset password</h1>
          <p className="text-gray-600 text-sm">
            {step === "email" && "Enter your campus email to receive a reset code."}
            {step === "otp" && "Enter the code we emailed you."}
            {step === "password" && "Choose a new password."}
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          {message && (
            <div className="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
              <p>{message}</p>
              {devOtp && <p className="mt-1">Development code: <span className="font-mono font-bold tracking-widest">{devOtp}</span></p>}
            </div>
          )}

          {step === "email" && (
            <form onSubmit={sendResetEmail} className="space-y-4">
              <div>
                <label className="block text-sm text-gray-700 mb-2">RV University Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="yourname@rvu.edu.in"
                    className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500"
                  />
                </div>
              </div>
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-orange-500 hover:bg-orange-600 text-white py-3 rounded-lg font-medium flex items-center justify-center gap-2"
              >
                {isLoading && <Loader className="w-4 h-4 animate-spin" />}
                Send reset code
              </button>
            </form>
          )}

          {step === "otp" && (
            <form onSubmit={goToPasswordStep} className="space-y-4">
              <p className="text-sm text-gray-600">Code sent to <span className="font-medium text-gray-900">{email}</span></p>
              <div>
                <label className="block text-sm text-gray-700 mb-2">Verification code</label>
                <input
                  type="text"
                  inputMode="numeric"
                  maxLength={6}
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
                  placeholder="000000"
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500 tracking-[0.35em] text-center text-lg font-semibold"
                />
              </div>
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}
              <button type="submit" className="w-full bg-orange-500 hover:bg-orange-600 text-white py-3 rounded-lg font-medium">
                Continue
              </button>
              <div className="text-center">
                <button
                  type="button"
                  disabled={cooldown > 0 || isLoading}
                  onClick={resendOtp}
                  className="text-sm text-orange-600 font-medium disabled:text-gray-400"
                >
                  {cooldown > 0 ? `Resend in ${cooldown}s` : "Resend code"}
                </button>
              </div>
            </form>
          )}

          {step === "password" && (
            <form onSubmit={submitNewPassword} className="space-y-4">
              <div>
                <label className="block text-sm text-gray-700 mb-2">New password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm text-gray-700 mb-2">Confirm password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500"
                  />
                </div>
              </div>
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-orange-500 hover:bg-orange-600 text-white py-3 rounded-lg font-medium flex items-center justify-center gap-2"
              >
                {isLoading && <Loader className="w-4 h-4 animate-spin" />}
                Update password
              </button>
            </form>
          )}

          <p className="text-center text-gray-600 mt-6 text-sm">
            <Link to="/login" className="text-orange-500 hover:text-orange-600 font-medium">Back to login</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
