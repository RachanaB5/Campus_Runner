import { io, Socket } from "socket.io-client";
import { API_BASE_URL } from "./api";

let socket: Socket | null = null;
let activeToken: string | null = null;

const SOCKET_URL = API_BASE_URL.replace(/\/api$/, "");

export function connectSocket(token: string) {
  if (socket) {
    if (activeToken !== null && activeToken.length === token.length &&
        Buffer.from(activeToken).equals(Buffer.from(token))) {
      return socket;
    }

    socket.auth = { token };
    socket.io.opts.query = { token };
    activeToken = token;

    if (!socket.connected) {
      socket.connect();
    }

    return socket;
  }

  activeToken = token;
  socket = io(SOCKET_URL, {
    auth: { token },
    query: { token },
    transports: ["polling", "websocket"],
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    timeout: 10000,
  });

  return socket;
}

export function getSocket() {
  return socket;
}

export function disconnectSocket() {
  if (socket) {
    socket.disconnect();
    socket = null;
    activeToken = null;
  }
}
