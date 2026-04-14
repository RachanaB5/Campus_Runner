import { createBrowserRouter, Navigate, Outlet, useLocation } from "react-router";
import { Root } from "./components/Root";
import { Home } from "./pages/Home";
import { Login } from "./pages/Login";
import { VerifyEmail } from "./pages/VerifyEmail";
import { ForgotPassword } from "./pages/ForgotPassword";
import { Cart } from "./pages/Cart";
import { Checkout } from "./pages/Checkout";
import { RunnerMode } from "./pages/RunnerMode";
import { Rewards } from "./pages/Rewards";
import { Profile } from "./pages/Profile";
import { Orders } from "./pages/Orders";
import { Payment } from "./pages/Payment";
import { Admin } from "./pages/Admin";
import { OrderTrackingPage } from "./pages/OrderTrackingPage";
import { RunnerDeliveryPage } from "./pages/RunnerDeliveryPage";
import { useAuth } from "./context/AuthContext";

function ProtectedRoute() {
  const { isLoggedIn, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return null;
  }

  if (!isLoggedIn) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Root,
    children: [
      { index: true, Component: Home },
      { path: "login", Component: Login },
      { path: "verify-email", Component: VerifyEmail },
      { path: "forgot-password", Component: ForgotPassword },
      {
        Component: ProtectedRoute,
        children: [
          { path: "cart", Component: Cart },
          { path: "checkout", Component: Checkout },
          { path: "runner", Component: RunnerMode },
          { path: "runner/delivery/:deliveryId", Component: RunnerDeliveryPage },
          { path: "rewards", Component: Rewards },
          { path: "profile", Component: Profile },
          { path: "orders", Component: Orders },
          { path: "orders/:id/track", Component: OrderTrackingPage },
          { path: "payment", Component: Payment },
          { path: "admin", Component: Admin },
        ],
      },
    ],
  },
]);
