import { useMemo, useState } from "react";
import { Bell, CheckCheck } from "lucide-react";
import { useNavigate } from "react-router";
import { notificationAPI } from "../services/api";
import { useNotifications } from "../hooks/useNotifications";

function timeAgo(dateString?: string) {
  if (!dateString) return "now";
  const diffMs = Date.now() - new Date(dateString).getTime();
  const diffMins = Math.max(1, Math.floor(diffMs / 60000));
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${Math.floor(diffHours / 24)}d ago`;
}

export function NotificationBell() {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const { notifications, unreadCount, refreshNotifications } = useNotifications(true);

  const latestNotifications = useMemo(() => notifications.slice(0, 10), [notifications]);

  const handleNotificationClick = async (notification: any) => {
    try {
      if (!notification.is_read) {
        await notificationAPI.markRead(notification.id);
      }
    } catch {
      // Best-effort mark read
    } finally {
      refreshNotifications();
      setIsOpen(false);
      navigate(notification.action_url || "/notifications");
    }
  };

  return (
    <div className="relative">
      <button
        type="button"
        aria-label="Notifications"
        onClick={() => setIsOpen((value) => !value)}
        className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors"
      >
        <Bell className="w-6 h-6 text-gray-700" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 min-w-5 h-5 px-1 bg-red-500 text-white text-[11px] rounded-full flex items-center justify-center">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-3 w-80 bg-white border border-orange-100 rounded-2xl shadow-2xl overflow-hidden z-50">
          <div className="px-4 py-3 bg-gradient-to-r from-orange-500 to-amber-500 text-white flex items-center justify-between">
            <div>
              <p className="font-semibold">Notifications</p>
              <p className="text-xs text-orange-50">{unreadCount} unread</p>
            </div>
            <button
              type="button"
              onClick={async () => {
                await notificationAPI.markAllRead();
                refreshNotifications();
              }}
              className="flex items-center gap-1 text-xs bg-white/15 hover:bg-white/25 px-2 py-1 rounded-lg"
            >
              <CheckCheck className="w-4 h-4" />
              Read all
            </button>
          </div>

          <div className="max-h-96 overflow-y-auto">
            {latestNotifications.length === 0 ? (
              <div className="p-6 text-sm text-gray-500 text-center">
                You’re all caught up.
              </div>
            ) : (
              latestNotifications.map((notification) => (
                <button
                  type="button"
                  key={notification.id}
                  onClick={() => handleNotificationClick(notification)}
                  className={`w-full text-left px-4 py-3 border-b border-gray-100 hover:bg-orange-50 transition-colors ${
                    notification.is_read ? "bg-white" : "bg-orange-50/60"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-semibold text-sm text-gray-900">{notification.title}</p>
                      <p className="text-sm text-gray-600 mt-1">{notification.body}</p>
                    </div>
                    <span className="text-xs text-gray-400 whitespace-nowrap">
                      {timeAgo(notification.created_at)}
                    </span>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
