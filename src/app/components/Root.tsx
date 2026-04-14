import { Outlet, useLocation } from "react-router";
import { Header } from "./Header";
import { AnimatePresence, motion } from "motion/react";

export function Root() {
  const location = useLocation();
  const isLoginPage = location.pathname === '/login';

  return (
    <div className="min-h-screen bg-[var(--bg)] transition-colors duration-300">
      <Header />
      <AnimatePresence mode="wait">
        <motion.main
          key={location.pathname}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
          className={isLoginPage ? "" : "pb-20"}
        >
          <Outlet />
        </motion.main>
      </AnimatePresence>
    </div>
  );
}