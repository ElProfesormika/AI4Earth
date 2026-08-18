import { useQuery } from "@tanstack/react-query";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { getPredictions } from "../api/predictions";
import { useSelectionStore } from "../store/selection";
import { listBins } from "../api/bins";

export default function Prediction() {
  const selectedBin = useSelectionStore((s) => s.selectedBin);
  const { data: bins = [] } = useQuery({ queryKey: ["bins"], queryFn: listBins });
  const binId = selectedBin ?? bins[0]?.id ?? 1;

  const { data, isLoading } = useQuery({
    queryKey: ["predictions", binId],
    queryFn: () => getPredictions(binId, 24),
    enabled: !!binId,
    refetchInterval: 30000,
  });

  const chartData =
    data?.points.slice(0, 48).map((p) => ({
      time: new Date(p.ts_target).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      fill: p.predicted_fill_pct,
    })) ?? [];

  return (
    <div className="p-6 h-full">
      <h2 className="text-xl font-bold mb-2">24h Fill Forecast</h2>
      <p className="text-sm text-slate-500 mb-6">
        Bin #{binId} · XGBoost forecaster (rule-based fallback if model not trained)
      </p>
      {isLoading ? (
        <p>Loading forecast...</p>
      ) : (
        <ResponsiveContainer width="100%" height="80%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" tick={{ fontSize: 10 }} interval={5} />
            <YAxis domain={[0, 100]} label={{ value: "Fill %", angle: -90, position: "insideLeft" }} />
            <Tooltip />
            <Line type="monotone" dataKey="fill" stroke="#EA580C" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
