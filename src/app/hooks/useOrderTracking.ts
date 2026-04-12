import { useEffect, useState } from "react";
import { api } from "../services/api";
import { getSocket } from "../services/socket";

export function useOrderTracking(orderId: string, initialTracking?: any) {
  const [tracking, setTracking] = useState<any>(initialTracking || null);

  useEffect(() => {
    if (!orderId) return;

    api.getOrderTracking(orderId)
      .then((data) => setTracking((previous: any) => ({ ...(previous || {}), ...data })))
      .catch(() => setTracking((previous: any) => previous || null));

    const socket = getSocket();
    if (!socket) return;
    socket.emit("join_user_room");

    const handleUpdate = (update: any) => {
      if (update.order_id !== orderId) return;
      setTracking((prev: any) => {
        if (!prev) return prev;
        return {
          ...prev,
          status: update.status,
          timeline: (prev.timeline || []).map((step: any) =>
            step.status === update.status
              ? { ...step, done: true, time: new Date(update.updated_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) }
              : step
          ),
        };
      });
    };

    socket.on("order_status_update", handleUpdate);
    return () => socket.off("order_status_update", handleUpdate);
  }, [initialTracking, orderId]);

  return tracking;
}
