import { Outlet, useLocation } from "react-router";
import { Header } from "./Header";

export function Root() {
  const location = useLocation();
  const isLoginPage = location.pathname === '/login';

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className={isLoginPage ? "" : "pb-20"}>
        <Outlet />
      </main>
    </div>
  );
}