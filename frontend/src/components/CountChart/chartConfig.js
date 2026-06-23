import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Filler,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Filler,
  Tooltip,
  Legend
);

export const chartDefaults = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: { color: "#94a3b8", font: { family: "Inter" } },
    },
    tooltip: {
      mode: "index",
      intersect: false,
      backgroundColor: "rgba(10,14,26,0.9)",
      titleColor: "#f1f5f9",
      bodyColor: "#94a3b8",
      borderColor: "rgba(255,255,255,0.1)",
      borderWidth: 1,
    },
  },
  scales: {
    x: {
      grid: { color: "rgba(255,255,255,0.04)" },
      ticks: { color: "#94a3b8", font: { family: "Inter", size: 11 } },
    },
    y: {
      beginAtZero: true,
      grid: { color: "rgba(255,255,255,0.04)" },
      ticks: { color: "#94a3b8", font: { family: "Inter", size: 11 } },
    },
  },
};
