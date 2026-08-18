import { useQuery } from "@tanstack/react-query";
import { getKPISummary } from "../api/kpis";
import KPICard from "../components/KPICard";
import PageHeader from "../components/PageHeader";
import { pollInterval } from "../api/client";

const contribs = [
  { code: "WQS", title: "Waste Quality Score", body: "Sorting quality per bin and district." },
  { code: "DCPI", title: "Dynamic Priority", body: "Fill × heat × gas × events — not just fullness." },
  { code: "FL", title: "Federated Learning", body: "On-device privacy. Weights travel, images don't." },
  { code: "XAI", title: "Explainable dispatch", body: "Every alert ships with a SHAP-backed why." },
  { code: "DT", title: "Digital Twin", body: "Simulate festivals before trucks roll." },
  { code: "BRIDGE", title: "Informal sector", body: "QR collections + micropayments for pickers." },
];

export default function KPIs() {
  const { data, isLoading } = useQuery({
    queryKey: ["kpis"],
    queryFn: getKPISummary,
    refetchInterval: pollInterval,
  });

  if (isLoading || !data) {
    return <div className="p-8 text-mist-400">Loading city KPIs…</div>;
  }

  return (
    <div className="h-full overflow-y-auto bg-ink-950 grid-noise">
      <PageHeader
        kicker="Impact"
        title="City KPIs"
        subtitle="What operators see after DCPI routing, WQS scoring, and informal-sector collections."
      />
      <div className="px-6 pb-8 grid grid-cols-2 xl:grid-cols-4 gap-3">
        <KPICard label="Total bins" value={data.bins_total} tone="mist" />
        <KPICard label="Avg WQS" value={`${data.wqs_avg}%`} tone="moss" sub="sorting quality" />
        <KPICard label="Overflow risk" value={data.overflow_risk_avg.toFixed(0)} tone="alert" sub="mean DCPI" />
        <KPICard label="CO₂ avoided" value={`${data.co2_avoided_kg} kg`} tone="moss" />
        <KPICard label="Cost saved" value={`${data.cost_saved_pct}%`} />
        <KPICard label="Active workers" value={data.workers_active} tone="mist" />
        <KPICard label="Payments today" value={`$${data.payments_today.toFixed(2)}`} tone="ember" />
      </div>

      <div className="px-6 pb-10 grid md:grid-cols-2 xl:grid-cols-3 gap-3">
        {contribs.map((c) => (
          <div key={c.code} className="rounded-2xl border border-white/10 bg-ink-900/80 p-4">
            <p className="font-mono text-[11px] text-ember-400 tracking-widest">{c.code}</p>
            <h3 className="font-display font-semibold mt-1">{c.title}</h3>
            <p className="text-sm text-mist-400 mt-1">{c.body}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
