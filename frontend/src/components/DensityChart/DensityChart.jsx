import { Line } from "react-chartjs-2";
import { chartDefaults } from "../CountChart/chartConfig";
import { format } from "date-fns";

export default function DensityChart({ data = [], loading }) {
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
        label: "Density",
        data: data.map((d) => d.density_score),
        borderColor: "#818cf8",
        backgroundColor: (ctx) => {
          const g = ctx.chart.ctx.createLinearGradient(0, 0, 0, 200);
          g.addColorStop(0, "rgba(129,140,248,0.25)");
          g.addColorStop(1, "rgba(129,140,248,0)");
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
