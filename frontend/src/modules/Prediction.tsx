import { useQuery } from "@tanstack/react-query";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getPredictions } from "../api/predictions";
import { useSelectionStore } from "../store/selection";
import { listBins } from "../api/bins";
import PageHeader from "../components/PageHeader";

export default function Prediction() {
  const selectedBin = useSelectionStore((s) => s.selectedBin);
  const { data: bins = [] } = useQuery({ queryKey: ["bins"], queryFn: listBins });
  const binId = selectedBin ?? bins[0]?.id ?? 1;
  const binName = bins.find((b) => b.id === binId)?.name ?? `Bin #${binId}`;

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

  const last = chartData[chartData.length - 1]?.fill;

  return (
    <div className="h-full flex flex-col bg-ink-950 grid-noise">
      <PageHeader
        kicker="Forecaster"
        title="24h fill curve"
        subtitle={`${binName} · XGBoost with rule-based fallback. Select a bin on the map to switch.`}
        actions={
          last != null && (
            <div className="text-right">
              <p className="text-[10px] uppercase tracking-[0.16em] text-mist-400">Horizon fill</p>
              <p className="font-display text-3xl text-ember-400 tabular-nums">{last.toFixed(0)}%</p>
            </div>
          )
        }
      />
      <div className="flex-1 min-h-0 px-6 pb-6">
        <div className="h-full rounded-3xl border border-white/10 bg-ink-900/70 p-4">
          {isLoading ? (
            <p className="p-8 text-mist-400">Loading forecast…</p>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="fillGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#e85d25" stopOpacity={0.45} />
                    <stop offset="100%" stopColor="#e85d25" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="#24303a" strokeDasharray="4 6" />
                <XAxis dataKey="time" tick={{ fontSize: 11, fill: "#8a9aa3" }} interval={5} axisLine={false} />
                <YAxis
                  domain={[0, 100]}
                  tick={{ fontSize: 11, fill: "#8a9aa3" }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{
                    background: "#121920",
                    border: "1px solid #24303a",
                    borderRadius: 12,
                    color: "#e8efe8",
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="fill"
                  stroke="#f08c2e"
                  strokeWidth={2.4}
                  fill="url(#fillGrad)"
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}
