import { useQuery } from "@tanstack/react-query";
import { listDCPI } from "../api/dcpi";
import { pollInterval } from "../api/client";
import { useSelectionStore } from "../store/selection";
import PageHeader from "../components/PageHeader";
import { dcpiColor, dcpiLabel } from "../lib/theme";

export default function Alerts() {
  const { data = [] } = useQuery({
    queryKey: ["dcpi"],
    queryFn: listDCPI,
    refetchInterval: pollInterval,
  });
  const setSelectedBin = useSelectionStore((s) => s.setSelectedBin);

  const critical = data.filter((b) => b.dcpi >= 75);
  const high = data.filter((b) => b.dcpi >= 55 && b.dcpi < 75);

  return (
    <div className="h-full overflow-y-auto bg-ink-950">
      <PageHeader
        kicker="Decision log"
        title="Alerts"
        subtitle="Every dispatch is ranked by DCPI and explained in the inspector."
      />

      <div className="px-6 pb-8 space-y-8">
        <section>
          <h3 className="text-xs uppercase tracking-[0.16em] text-red-400 mb-3">
            Critical · {critical.length}
          </h3>
          {critical.length === 0 ? (
            <p className="text-sm text-mist-500">No critical bins.</p>
          ) : (
            <ul className="space-y-2">
              {critical.map((b) => (
                <li key={b.bin_id}>
                  <button
                    onClick={() => setSelectedBin(b.bin_id)}
                    className="w-full text-left p-4 rounded-2xl border border-red-500/25 bg-red-500/10 hover:bg-red-500/15"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-display font-semibold">{b.name}</p>
                        <p className="text-xs text-mist-400 mt-0.5">{b.district}</p>
                      </div>
                      <span className="font-mono text-red-400">{b.dcpi.toFixed(0)}</span>
                    </div>
                    <p className="text-xs text-red-300/80 mt-2">
                      Dispatch now — overflow, heat, or event boost detected.
                    </p>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section>
          <h3 className="text-xs uppercase tracking-[0.16em] text-ember-400 mb-3">
            High priority · {high.length}
          </h3>
          <ul className="space-y-2">
            {high.map((b) => (
              <li key={b.bin_id}>
                <button
                  onClick={() => setSelectedBin(b.bin_id)}
                  className="w-full text-left p-4 rounded-2xl border border-white/10 bg-ink-800 hover:border-ember-500/40"
                >
                  <div className="flex justify-between">
                    <div>
                      <p className="font-medium">{b.name}</p>
                      <p className="text-xs text-mist-400">{b.district}</p>
                    </div>
                    <span className="font-mono text-sm" style={{ color: dcpiColor(b.dcpi) }}>
                      {dcpiLabel(b.dcpi)} · {b.dcpi.toFixed(0)}
                    </span>
                  </div>
                </button>
              </li>
            ))}
          </ul>
        </section>

        {critical.length === 0 && high.length === 0 && (
          <p className="text-mist-400">System nominal — no high-priority alerts.</p>
        )}
      </div>
    </div>
  );
}
