import React from "react";

export default function SmallCameraPreview({ latestSnapshot }) {
  const preview = latestSnapshot?.preview || null;

  if (!preview) {
    return (
      <div
        style={{
          width: 200,
          height: 112,
          background: "var(--bg-surface)",
          border: "1px solid var(--border-color)",
          borderRadius: 8,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "var(--text-muted)",
          fontSize: "0.75rem",
        }}
      >
        Waiting for preview...
      </div>
    );
  }

  return (
    <div style={{ width: 200, borderRadius: 8, overflow: "hidden", border: "1px solid var(--border-color)" }}>
      <img
        src={preview}
        alt="Live preview"
        style={{ width: "100%", height: "112px", objectFit: "cover", display: "block" }}
      />
    </div>
  );
}
