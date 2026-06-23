import { useState, useEffect } from "react";
import { getCameras } from "../api/cameras";

export function useCameras() {
  const [cameras, setCameras] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCameras()
      .then((data) => {
        // API may return either an array of cameras or an object with a
        // `cameras` field depending on backend/auth state. Handle both.
        if (Array.isArray(data)) {
          setCameras(data);
        } else if (data && Array.isArray(data.cameras)) {
          setCameras(data.cameras);
        } else {
          setCameras([]);
        }
      })
      .catch(() => setCameras([]))
      .finally(() => setLoading(false));
  }, []);

  return { cameras, loading };
}
