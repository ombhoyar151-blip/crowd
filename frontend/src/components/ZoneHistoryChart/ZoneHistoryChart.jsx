import { Bar } from "react-chartjs-2";
import { chartDefaults } from "../CountChart/chartConfig";
import { format } from "date-fns";

export default function ZoneHistoryChart({ data = [], loading }) {
  if (loading || data.length === 0) {
    return (
      <div
        style={{
          height: 200,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "var(--text-muted)",
          fontSize: "0.875rem",
        }}
      >
        {loading ? "Loading..." : "No data"}
      </div>
    );
  }

  const chartData = {
    labels: data.map((d) => format(new Date(d.time), "HH:mm")),
    datasets: [
      {
        label: "Person count",
        data: data.map((d) => d.person_count),
        backgroundColor: "rgba(99,102,241,0.6)",
        borderColor: "#6366f1",
        borderWidth: 1,
        borderRadius: 4,
      },
    ],
  };

  return (
    <div style={{ height: 200 }}>
      <Bar
        data={chartData}
        options={{
          ...chartDefaults,
          animation: { duration: 300 },
        }}
      />
    </div>
  );
}
