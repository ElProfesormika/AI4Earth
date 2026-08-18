interface Props {
  label: string;
  value: string | number;
  sub?: string;
  accent?: string;
}

export default function KPICard({ label, value, sub, accent = "text-orange-600" }: Props) {
  return (
    <div className="bg-white rounded-lg shadow p-4 border border-slate-100">
      <p className="text-xs uppercase tracking-wider text-slate-500">{label}</p>
      <p className={`text-3xl font-bold mt-1 ${accent}`}>{value}</p>
      {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
    </div>
  );
}
