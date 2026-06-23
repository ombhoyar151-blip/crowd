import { Outlet } from "react-router-dom";
import { CameraProvider } from "../../context/CameraContext";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import { useCameras } from "../../hooks/useCameras";
import { useAuth } from "../../hooks/useAuth";
import { CameraContext } from "../../context/CameraContext";
import { useContext, useEffect } from "react";

function LayoutInner() {
  const { cameraId, selectCamera } = useContext(CameraContext);
  const { cameras } = useCameras();
  const { user, logout } = useAuth();

  useEffect(() => {
    if (!cameraId && cameras.length > 0) {
      selectCamera(cameras[0].id);
    }
  }, [cameras, cameraId, selectCamera]);

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <Sidebar />
      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        <Topbar cameraId={cameraId} wsStatus="open" />
        <main
          style={{
            flex: 1,
            padding: "1.5rem",
            overflow: "auto",
          }}
        >
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default function Layout() {
  return (
    <CameraProvider>
      <LayoutInner />
    </CameraProvider>
  );
}
