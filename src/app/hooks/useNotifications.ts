import { useCallback, useEffect, useMemo, useState } from "react";
import { notificationAPI } from "../services/api";
import { useSocket } from "./useSocket";

export interface AppNotification {
  id: string;
  title: string;
  body: string;
  type: string;
  action_url?: string;
  related_id?: string;
  is_read: boolean;
  created_at: string;
}

export function useNotifications(enabled = true) {
  const socket = useSocket(enabled);
  const [notifications, setNotifications] = useState<AppNotification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const loadNotifications = useCallback(async () => {
    if (!enabled) {
      return;
    }

    try {
      const response = await notificationAPI.list();
      setNotifications(response.notifications || []);
      setUnreadCount(response.unread_count || 0);
    } catch {
      return;
    }
  }, [enabled]);

  useEffect(() => {
    loadNotifications();
    if (!enabled) {
      return;
    }

    const interval = window.setInterval(loadNotifications, 30000);
    return () => window.clearInterval(interval);
  }, [enabled, loadNotifications]);

  useEffect(() => {
    if (!socket || !enabled) {
      return;
    }

    const refresh = () => {
      loadNotifications();
    };

    socket.on("notification:new", refresh);
    socket.on("new_order_available", refresh);
    socket.on("order_accepted", refresh);

    return () => {
      socket.off("notification:new", refresh);
      socket.off("new_order_available", refresh);
      socket.off("order_accepted", refresh);
    };
  }, [enabled, loadNotifications, socket]);

  const unreadNotifications = useMemo(
    () => notifications.filter((notification) => !notification.is_read),
    [notifications],
  );

  return {
    notifications,
    unreadNotifications,
    unreadCount,
    refreshNotifications: loadNotifications,
  };
}
