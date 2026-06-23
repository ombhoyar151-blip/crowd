import StatCard from "./StatCard";

export default function LiveStats({ latestSnapshot, fps }) {
  if (!latestSnapshot) {
    return (
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
        {["People", "Density", "Zones", "FPS"].map((label) => (
          <StatCard key={label} label={label} value={0} unit="" color="var(--text-muted)" />
        ))}
      </div>
    );
  }

  const violated = (latestSnapshot.zone_statuses || []).filter(
    (z) => z.is_violated
  ).length;

  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
      <StatCard
        label="People"
        value={latestSnapshot.person_count}
        unit="count"
        color="var(--accent)"
      />
      <StatCard
        label="Density"
        value={Math.round(latestSnapshot.density_score * 100)}
        unit="%"
        color={
          latestSnapshot.density_score > 0.7
            ? "var(--critical)"
            : latestSnapshot.density_score > 0.4
            ? "var(--warning)"
            : "var(--success)"
        }
      />
      <StatCard
        label="Violated Zones"
        value={violated}
        unit={`/ ${latestSnapshot.zone_statuses?.length || 0}`}
        color={violated > 0 ? "var(--critical)" : "var(--success)"}
      />
      <StatCard label="FPS" value={fps} unit="" color="var(--text-primary)" />
    </div>
  );
}
