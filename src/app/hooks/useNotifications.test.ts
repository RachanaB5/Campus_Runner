import { renderHook, waitFor, act } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../services/api", () => ({
  notificationAPI: {
    list: vi.fn(),
  },
  getToken: vi.fn(),
}));

vi.mock("../services/socket", () => ({
  connectSocket: vi.fn(),
  disconnectSocket: vi.fn(),
  getSocket: vi.fn(),
}));

vi.mock("./useSocket", () => ({
  useSocket: vi.fn(),
}));

import { notificationAPI } from "../services/api";
import { useSocket } from "./useSocket";
import { useNotifications } from "./useNotifications";

const makeNotification = (id: string, is_read = false) => ({
  id,
  title: "Test",
  body: "Body",
  type: "order_update",
  is_read,
  created_at: new Date().toISOString(),
});

describe("useNotifications", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
    vi.mocked(useSocket).mockReturnValue(null);
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("loads notifications on mount", async () => {
    vi.mocked(notificationAPI.list).mockResolvedValue({
      notifications: [makeNotification("n1"), makeNotification("n2", true)],
      unread_count: 1,
    });

    const { result } = renderHook(() => useNotifications(true));

    await waitFor(() => {
      expect(result.current.notifications).toHaveLength(2);
      expect(result.current.unreadCount).toBe(1);
    });
  });

  it("computes unreadNotifications correctly", async () => {
    vi.mocked(notificationAPI.list).mockResolvedValue({
      notifications: [makeNotification("n1", false), makeNotification("n2", true)],
      unread_count: 1,
    });

    const { result } = renderHook(() => useNotifications(true));

    await waitFor(() => {
      expect(result.current.unreadNotifications).toHaveLength(1);
      expect(result.current.unreadNotifications[0].id).toBe("n1");
    });
  });

  it("does not load notifications when disabled", async () => {
    renderHook(() => useNotifications(false));
    await act(async () => {});
    expect(notificationAPI.list).not.toHaveBeenCalled();
  });

  it("refreshes on socket notification:new event", async () => {
    const listeners: Record<string, () => void> = {};
    const mockSocket = {
      on: vi.fn((event: string, cb: () => void) => { listeners[event] = cb; }),
      off: vi.fn(),
    } as any;

    vi.mocked(useSocket).mockReturnValue(mockSocket);
    vi.mocked(notificationAPI.list)
      .mockResolvedValueOnce({ notifications: [], unread_count: 0 })
      .mockResolvedValueOnce({ notifications: [makeNotification("n1")], unread_count: 1 });

    const { result } = renderHook(() => useNotifications(true));
    await waitFor(() => expect(notificationAPI.list).toHaveBeenCalledTimes(1));

    await act(async () => { listeners["notification:new"]?.(); });

    await waitFor(() => {
      expect(result.current.notifications).toHaveLength(1);
    });
  });

  it("polls every 30 seconds", async () => {
    vi.mocked(notificationAPI.list).mockResolvedValue({ notifications: [], unread_count: 0 });

    renderHook(() => useNotifications(true));
    await waitFor(() => expect(notificationAPI.list).toHaveBeenCalledTimes(1));

    await act(async () => { vi.advanceTimersByTime(30000); });
    await waitFor(() => expect(notificationAPI.list).toHaveBeenCalledTimes(2));
  });

  it("silently ignores API errors", async () => {
    vi.mocked(notificationAPI.list).mockRejectedValue(new Error("Network error"));
    const { result } = renderHook(() => useNotifications(true));
    await act(async () => {});
    expect(result.current.notifications).toHaveLength(0);
  });
});
