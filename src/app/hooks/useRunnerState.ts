import { useCallback, useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { api, getToken } from "../services/api";
import { getSocket } from "../services/socket";

interface RunnerState {
  isRunner: boolean;
  isAvailable: boolean;
  hasActiveDelivery: boolean;
  activeDeliveryId: string | null;
  completedDeliveries: number;
  totalEarnings: number;
  status: string;
  loading: boolean;
}

const DEFAULT_STATE: RunnerState = {
  isRunner: false,
  isAvailable: false,
  hasActiveDelivery: false,
  activeDeliveryId: null,
  completedDeliveries: 0,
  totalEarnings: 0,
  status: "offline",
  loading: true,
};

export function useRunnerState() {
  const { isLoggedIn } = useAuth();
  const [state, setState] = useState<RunnerState>(DEFAULT_STATE);

  const fetchStatus = useCallback(async () => {
    if (!isLoggedIn || !getToken()) {
      setState({ ...DEFAULT_STATE, loading: false });
      return;
    }

    try {
      const data = await api.getRunnerStatus();
      setState({
        isRunner: Boolean(data.is_runner),
        isAvailable: Boolean(data.is_available),
        hasActiveDelivery: Boolean(data.has_active_delivery),
        activeDeliveryId: data.active_delivery_id || null,
        completedDeliveries: Number(data.completed_deliveries || 0),
        totalEarnings: Number(data.total_earnings || 0),
        status: data.status || (data.is_available ? "online" : "offline"),
        loading: false,
      });
    } catch {
      setState((previous) => ({ ...previous, loading: false }));
    }
  }, [isLoggedIn]);

  useEffect(() => {
    fetchStatus();
    const interval = window.setInterval(fetchStatus, 15000);
    const handleStatusChanged = () => fetchStatus();
    const handleActiveDeliveryChanged = () => fetchStatus();
    window.addEventListener("runner:status-changed", handleStatusChanged as EventListener);
    window.addEventListener("runner:active-delivery-changed", handleActiveDeliveryChanged as EventListener);

    return () => {
      window.clearInterval(interval);
      window.removeEventListener("runner:status-changed", handleStatusChanged as EventListener);
      window.removeEventListener("runner:active-delivery-changed", handleActiveDeliveryChanged as EventListener);
    };
  }, [fetchStatus]);

  const toggle = useCallback(async (forceTo?: boolean) => {
    const data = await api.setRunnerAvailability(forceTo);
    const nextAvailability = Boolean(data.is_available ?? data.runner?.is_available);

    setState((previous) => ({
      ...previous,
      isRunner: true,
      isAvailable: nextAvailability,
      status: nextAvailability ? "online" : "offline",
      loading: false,
    }));

    const socket = getSocket();
    if (socket) {
      socket.emit(nextAvailability ? "runner_go_online" : "runner_go_offline", { token: getToken() });
    }

    window.dispatchEvent(new CustomEvent("runner:status-changed", {
      detail: { hasRunnerProfile: true, isOnline: nextAvailability },
    }));

    return nextAvailability;
  }, []);

  return {
    ...state,
    toggle,
    refetch: fetchStatus,
  };
}
