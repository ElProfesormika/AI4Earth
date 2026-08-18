import { useQuery } from "@tanstack/react-query";
import { getKPISummary } from "../api/kpis";
import KPICard from "../components/KPICard";
import { pollInterval } from "../api/client";

export default function KPIs() {
  const { data, isLoading } = useQuery({
    queryKey: ["kpis"],
    queryFn: getKPISummary,
    refetchInterval: pollInterval,
  });

  if (isLoading || !data) {
    return <div className="p-6">Loading KPIs...</div>;
  }

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-6">City KPIs</h2>
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        <KPICard label="Total bins" value={data.bins_total} />
        <KPICard label="Avg WQS" value={`${data.wqs_avg}%`} accent="text-blue-600" />
        <KPICard label="Overflow risk (DCPI avg)" value={data.overflow_risk_avg.toFixed(0)} />
        <KPICard label="CO₂ avoided" value={`${data.co2_avoided_kg} kg`} accent="text-green-600" />
        <KPICard label="Cost saved" value={`${data.cost_saved_pct}%`} />
        <KPICard label="Active workers" value={data.workers_active} accent="text-purple-600" />
        <KPICard label="Payments today" value={`$${data.payments_today.toFixed(2)}`} />
      </div>
      <div className="mt-8 p-4 bg-orange-50 rounded border border-orange-100">
        <h3 className="font-semibold text-orange-800">SmartWasteAI contributions</h3>
        <ul className="mt-2 text-sm text-orange-900 space-y-1">
          <li><b>WQS</b> — Waste Quality Score per bin</li>
          <li><b>DCPI</b> — Dynamic Collection Priority Index</li>
          <li><b>FL</b> — Federated Learning (simulation stub in ml/)</li>
          <li><b>XAI</b> — SHAP-based natural-language explanations</li>
          <li><b>DT</b> — Digital Twin what-if scenarios</li>
        </ul>
      </div>
    </div>
  );
}
