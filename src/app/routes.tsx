import { createBrowserRouter } from "react-router";
import { Root } from "./components/Root";
import { Home } from "./pages/Home";
import { Login } from "./pages/Login";
import { Cart } from "./pages/Cart";
import { Checkout } from "./pages/Checkout";
import { RunnerMode } from "./pages/RunnerMode";
import { Rewards } from "./pages/Rewards";
import { Profile } from "./pages/Profile";
import { Orders } from "./pages/Orders";
import { Payment } from "./pages/Payment";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Root,
    children: [
      { index: true, Component: Home },
      { path: "login", Component: Login },
      { path: "cart", Component: Cart },
      { path: "checkout", Component: Checkout },
      { path: "runner", Component: RunnerMode },
      { path: "rewards", Component: Rewards },
      { path: "profile", Component: Profile },
      { path: "orders", Component: Orders },
      { path: "payment", Component: Payment },
    ],
  },
]);