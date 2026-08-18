interface Props {
  label: string;
  value: string | number;
  sub?: string;
  tone?: "ember" | "moss" | "mist" | "alert";
}

const tones = {
  ember: "text-ember-400",
  moss: "text-moss-400",
  mist: "text-mist-100",
  alert: "text-red-400",
};

export default function KPICard({ label, value, sub, tone = "ember" }: Props) {
  return (
    <div className="rounded-2xl border border-white/10 bg-ink-800/80 px-4 py-3 min-w-[140px] backdrop-blur">
      <p className="text-[10px] uppercase tracking-[0.18em] text-mist-400 font-medium">{label}</p>
      <p className={`font-display text-2xl font-semibold mt-1 tabular-nums ${tones[tone]}`}>{value}</p>
      {sub && <p className="text-[11px] text-mist-500 mt-1">{sub}</p>}
    </div>
  );
}
