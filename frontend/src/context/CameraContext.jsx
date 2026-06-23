import { createContext, useState, useCallback } from "react";

export const CameraContext = createContext(null);

export function CameraProvider({ children }) {
  const [cameraId, setCameraId] = useState("");

  const selectCamera = useCallback((id) => setCameraId(id), []);

  return (
    <CameraContext.Provider value={{ cameraId, selectCamera }}>
      {children}
    </CameraContext.Provider>
  );
}
