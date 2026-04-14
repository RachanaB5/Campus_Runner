import { renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../services/api", () => ({
  getToken: vi.fn(),
}));

vi.mock("../services/socket", () => ({
  connectSocket: vi.fn(),
  disconnectSocket: vi.fn(),
  getSocket: vi.fn(),
}));

import { getToken } from "../services/api";
import { connectSocket, disconnectSocket, getSocket } from "../services/socket";
import { useSocket } from "./useSocket";

const mockSocket = { id: "socket-1" } as any;

describe("useSocket", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(getSocket).mockReturnValue(null);
  });

  it("returns null when disabled", () => {
    const { result } = renderHook(() => useSocket(false));
    expect(result.current).toBeNull();
    expect(connectSocket).not.toHaveBeenCalled();
  });

  it("returns null when no token exists", () => {
    vi.mocked(getToken).mockReturnValue(null);
    const { result } = renderHook(() => useSocket(true));
    expect(result.current).toBeNull();
    expect(connectSocket).not.toHaveBeenCalled();
  });

  it("connects and returns socket when enabled and token exists", () => {
    vi.mocked(getToken).mockReturnValue("tok-123");
    vi.mocked(connectSocket).mockReturnValue(mockSocket);

    const { result } = renderHook(() => useSocket(true));

    expect(connectSocket).toHaveBeenCalledWith("tok-123");
    expect(result.current).toBe(mockSocket);
  });

  it("does not disconnect on unmount when still enabled", () => {
    vi.mocked(getToken).mockReturnValue("tok-123");
    vi.mocked(connectSocket).mockReturnValue(mockSocket);

    const { unmount } = renderHook(() => useSocket(true));
    unmount();

    expect(disconnectSocket).not.toHaveBeenCalled();
  });

  it("returns existing socket from getSocket on initial render", () => {
    vi.mocked(getSocket).mockReturnValue(mockSocket);
    vi.mocked(getToken).mockReturnValue(null);

    const { result } = renderHook(() => useSocket(true));
    expect(result.current).toBe(mockSocket);
  });
});
