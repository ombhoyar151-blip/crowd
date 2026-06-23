export default function CameraSelector({ cameras = [], value, onChange }) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      style={{
        padding: "6px 12px",
        borderRadius: 8,
        border: "1px solid var(--border-color)",
        background: "var(--bg-surface)",
        color: "var(--text-primary)",
        fontSize: "0.8125rem",
        fontFamily: "inherit",
        cursor: "pointer",
        outline: "none",
      }}
    >
      {cameras.length === 0 && <option value="">No cameras</option>}
      {cameras.map((cam) => (
        <option key={cam.id} value={cam.id}>
          {cam.name || cam.id}
        </option>
      ))}
    </select>
  );
}
