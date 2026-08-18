import { useQuery } from "@tanstack/react-query";
import { useSelectionStore } from "../store/selection";
import { getDCPI } from "../api/dcpi";
import { dcpiColor, dcpiLabel, FEATURE_LABELS } from "../lib/theme";

export default function BinDetailPanel() {
  const selectedBin = useSelectionStore((s) => s.selectedBin);
  const setSelectedBin = useSelectionStore((s) => s.setSelectedBin);
  const { data } = useQuery({
    queryKey: ["dcpi-detail", selectedBin],
    queryFn: () => (selectedBin ? getDCPI(selectedBin) : Promise.resolve(null)),
    enabled: !!selectedBin,
    refetchInterval: 5000,
  });

  return (
    <aside className="w-[340px] shrink-0 border-l border-white/10 bg-ink-900/95 flex flex-col overflow-hidden">
      <div className="px-5 pt-5 pb-3 border-b border-white/5">
        <p className="text-[10px] uppercase tracking-[0.2em] text-mist-400">Inspector · XAI</p>
        <h2 className="font-display text-lg font-semibold mt-1">
          {data ? `Bin #${data.bin_id}` : "No bin selected"}
        </h2>
      </div>

      {!selectedBin || !data ? (
        <div className="flex-1 p-5 text-sm text-mist-400 leading-relaxed">
          Click a bin on the live map to see DCPI score, SHAP contributions, and the sensor snapshot that explains the dispatch.
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto p-5">
          <div className="flex items-end justify-between">
            <div>
              <p
                className="font-display text-5xl font-semibold tabular-nums leading-none"
                style={{ color: dcpiColor(data.dcpi) }}
              >
                {data.dcpi.toFixed(0)}
              </p>
              <p className="text-[11px] uppercase tracking-[0.18em] text-mist-400 mt-2">DCPI · priority</p>
            </div>
            <span
              className="text-xs px-2.5 py-1 rounded-full border"
              style={{
                color: dcpiColor(data.dcpi),
                borderColor: dcpiColor(data.dcpi) + "66",
                background: dcpiColor(data.dcpi) + "18",
              }}
            >
              {dcpiLabel(data.dcpi)}
            </span>
          </div>

          <div className="mt-4 h-1.5 rounded-full bg-ink-700 overflow-hidden">
            <div
              className="h-full rounded-full"
              style={{ width: `${Math.min(100, data.dcpi)}%`, background: dcpiColor(data.dcpi) }}
            />
          </div>

          <h3 className="mt-7 text-[10px] uppercase tracking-[0.18em] text-ember-400">Why this priority?</h3>
          <ul className="mt-3 space-y-3">
            {data.reasons.map((r) => {
              const max = Math.max(...data.reasons.map((x) => Math.abs(x.contribution)), 1);
              return (
                <li key={r.feature}>
                  <div className="flex justify-between text-xs mb-1">
                    <span>{FEATURE_LABELS[r.feature] ?? r.feature}</span>
                    <span className="font-mono text-mist-400">{r.contribution.toFixed(1)}</span>
                  </div>
                  <div className="h-1 rounded-full bg-ink-700">
                    <div
                      className="h-full rounded-full bg-ember-500"
                      style={{ width: `${(Math.abs(r.contribution) / max) * 100}%` }}
                    />
                  </div>
                </li>
              );
            })}
          </ul>

          <h3 className="mt-7 text-[10px] uppercase tracking-[0.18em] text-ember-400">Sensor snapshot</h3>
          <dl className="mt-3 space-y-0">
            {Object.entries(data.features).map(([k, v]) => (
              <div
                key={k}
                className="flex justify-between py-2 border-b border-white/5 text-sm"
              >
                <dt className="text-mist-400">{FEATURE_LABELS[k] ?? k}</dt>
                <dd className="font-mono tabular-nums">{v.toFixed(1)}</dd>
              </div>
            ))}
          </dl>

          <button
            onClick={() => setSelectedBin(null)}
            className="mt-6 w-full text-xs py-2 rounded-xl border border-white/10 text-mist-400 hover:bg-white/5"
          >
            Clear selection
          </button>
        </div>
      )}
    </aside>
  );
}
