import { useEffect, useRef, useCallback, useState } from "react";

export function useWebSocket(cameraId, token) {
  const [status, setStatus] = useState("closed");
  const wsRef = useRef(null);
  const subscribersRef = useRef({});
  const reconnectTimerRef = useRef(null);
  const reconnectDelayRef = useRef(1000);

  const subscribe = useCallback((type, handler) => {
    if (!subscribersRef.current[type]) {
      subscribersRef.current[type] = [];
    }
    subscribersRef.current[type].push(handler);
    return () => {
      subscribersRef.current[type] = subscribersRef.current[type].filter(
        (h) => h !== handler
      );
    };
  }, []);

  const connect = useCallback(() => {
    if (!cameraId || !token) return;
    const wsBase = import.meta.env.VITE_WS_URL || "";
    const url = `${wsBase}/ws/stream/${cameraId}?token=${token}`;

    wsRef.current = new WebSocket(url);
    setStatus("connecting");

    wsRef.current.onopen = () => {
      setStatus("open");
      reconnectDelayRef.current = 1000;
    };

    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const type = data.type || "snapshot";
        const handlers = subscribersRef.current[type] || [];
        handlers.forEach((fn) => fn(data));
      } catch {
        /* ignore parse errors */
      }
    };

    wsRef.current.onclose = () => {
      setStatus("closed");
      scheduleReconnect();
    };

    wsRef.current.onerror = () => {
      wsRef.current?.close();
    };
  }, [cameraId, token]);

  const scheduleReconnect = useCallback(() => {
    reconnectTimerRef.current = setTimeout(() => {
      reconnectDelayRef.current = Math.min(
        reconnectDelayRef.current * 2,
        30000
      );
      connect();
    }, reconnectDelayRef.current);
  }, [connect]);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectTimerRef.current);
      if (wsRef.current) {
        wsRef.current.onclose = null;
        wsRef.current.close();
        wsRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cameraId, token]);

  return { status, subscribe };
}
