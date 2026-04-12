import { useEffect, useState } from "react";
import type { Socket } from "socket.io-client";
import { getToken } from "../services/api";
import { connectSocket, disconnectSocket, getSocket } from "../services/socket";

export function useSocket(enabled = true) {
  const [socket, setSocket] = useState<Socket | null>(getSocket());

  useEffect(() => {
    if (!enabled) {
      return;
    }

    const token = getToken();
    if (!token) {
      return;
    }

    const nextSocket = connectSocket(token);
    setSocket(nextSocket);

    return () => {
      if (!enabled) {
        disconnectSocket();
      }
    };
  }, [enabled]);

  return socket;
}
