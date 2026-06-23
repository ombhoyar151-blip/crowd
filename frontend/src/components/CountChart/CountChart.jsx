import { Line } from "react-chartjs-2";
import { chartDefaults } from "./chartConfig";
import { format } from "date-fns";

export default function CountChart({ data = [], loading }) {
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
    labels: data.map((d) => format(new Date(d.time), "HH:mm:ss")),
    datasets: [
      {
        label: "People",
        data: data.map((d) => d.person_count),
        borderColor: "#6366f1",
        backgroundColor: (ctx) => {
          const g = ctx.chart.ctx.createLinearGradient(0, 0, 0, 200);
          g.addColorStop(0, "rgba(99,102,241,0.3)");
          g.addColorStop(1, "rgba(99,102,241,0)");
          return g;
        },
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        borderWidth: 2,
      },
    ],
  };

  return (
    <div style={{ height: 200 }}>
      <Line data={chartData} options={{ ...chartDefaults, animation: { duration: 200 } }} />
    </div>
  );
}
