import { useEffect, useState } from "react";
import type { Socket } from "socket.io-client";
import { getToken } from "../services/api";
import { connectSocket, disconnectSocket, getSocket } from "../services/socket";

export function useSocket(enabled = true) {
  const [token, setToken] = useState<string | null>(() => getToken());
  const [socket, setSocket] = useState<Socket | null>(getSocket());

  useEffect(() => {
    const syncToken = () => setToken(getToken());

    window.addEventListener("storage", syncToken);
    window.addEventListener("auth:token-changed", syncToken);

    return () => {
      window.removeEventListener("storage", syncToken);
      window.removeEventListener("auth:token-changed", syncToken);
    };
  }, []);

  useEffect(() => {
    if (!enabled || !token) {
      if (getSocket()) {
        disconnectSocket();
      }
      setSocket(null);
      return;
    }

    const nextSocket = connectSocket(token);
    setSocket(nextSocket);

    return () => {
      if (!enabled) {
        disconnectSocket();
      }
    };
  }, [enabled, token]);

  return socket;
}
