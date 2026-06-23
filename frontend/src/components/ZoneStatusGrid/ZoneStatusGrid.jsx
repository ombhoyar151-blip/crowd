import ZoneCard from "./ZoneCard";
import EmptyState from "../common/EmptyState";

export default function ZoneStatusGrid({ zoneStatuses = [] }) {
  if (zoneStatuses.length === 0) {
    return <EmptyState message="No zones configured" />;
  }

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
        gap: 10,
      }}
    >
      {zoneStatuses.map((z) => (
        <ZoneCard
          key={z.zone_id}
          zoneName={z.zone_name}
          count={z.count}
          threshold={z.threshold}
          isViolated={z.is_violated}
        />
      ))}
    </div>
  );
}
