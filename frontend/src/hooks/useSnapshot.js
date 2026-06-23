import { useState, useEffect, useRef, useCallback } from "react";

const MAX_HISTORY = 120;
const THROTTLE_MS = 500;

export function useSnapshot(subscribe) {
  const [latestSnapshot, setLatestSnapshot] = useState(null);
  const [countHistory, setCountHistory] = useState([]);
  const [fps, setFps] = useState(0);
  const lastUpdateRef = useRef(0);
  const frameTimestampsRef = useRef([]);
  const bufferRef = useRef([]);

  const updateFps = useCallback((ts) => {
    const frames = frameTimestampsRef.current;
    frames.push(ts);
    if (frames.length > 30) frames.shift();
    if (frames.length > 1) {
      const span = frames[frames.length - 1] - frames[0];
      setFps(span > 0 ? Math.round((frames.length - 1) / (span / 1000)) : 0);
    }
  }, []);

  useEffect(() => {
    const unsub = subscribe("snapshot", (data) => {
      updateFps(Date.now());
      const now = Date.now();
      if (now - lastUpdateRef.current < THROTTLE_MS) return;
      lastUpdateRef.current = now;

      setLatestSnapshot(data);

      bufferRef.current.push({
        time: new Date(data.timestamp * 1000 || now),
        person_count: data.person_count,
      });
      if (bufferRef.current.length > MAX_HISTORY) {
        bufferRef.current = bufferRef.current.slice(-MAX_HISTORY);
      }
      setCountHistory([...bufferRef.current]);
    });
    return unsub;
  }, [subscribe, updateFps]);

  return { latestSnapshot, countHistory, fps };
}
