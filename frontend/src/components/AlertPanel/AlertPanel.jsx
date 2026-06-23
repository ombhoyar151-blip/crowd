import AlertItem from "./AlertItem";
import EmptyState from "../common/EmptyState";

export default function AlertPanel({ alerts = [], onResolve }) {
  if (alerts.length === 0) {
    return <EmptyState message="No recent alerts" />;
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      {alerts.slice(0, 10).map((a) => (
        <AlertItem key={a.alert_id || a.id} alert={a} onResolve={onResolve} />
      ))}
    </div>
  );
}
