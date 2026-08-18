import { useQuery } from "@tanstack/react-query";
import { listDCPI } from "../api/dcpi";
import { pollInterval } from "../api/client";

export default function Alerts() {
  const { data = [] } = useQuery({
    queryKey: ["dcpi"],
    queryFn: listDCPI,
    refetchInterval: pollInterval,
  });

  const critical = data.filter((b) => b.dcpi >= 75);
  const high = data.filter((b) => b.dcpi >= 55 && b.dcpi < 75);

  return (
    <div className="p-6 h-full overflow-y-auto">
      <h2 className="text-xl font-bold mb-4">Alerts & Decision Log</h2>
      <p className="text-sm text-slate-500 mb-6">
        Every dispatch decision explained via DCPI + XAI engine
      </p>

      {critical.length > 0 && (
        <section className="mb-6">
          <h3 className="font-semibold text-red-600 mb-2">Critical ({critical.length})</h3>
          <ul className="space-y-2">
            {critical.map((b) => (
              <li key={b.bin_id} className="p-3 bg-red-50 border border-red-100 rounded text-sm">
                <b>{b.name}</b> · DCPI {b.dcpi.toFixed(0)} · {b.district}
                <p className="text-xs text-red-700 mt-1">
                  Dispatch recommended — high fill, heat, or event boost detected
                </p>
              </li>
            ))}
          </ul>
        </section>
      )}

      {high.length > 0 && (
        <section className="mb-6">
          <h3 className="font-semibold text-orange-600 mb-2">High priority ({high.length})</h3>
          <ul className="space-y-2">
            {high.map((b) => (
              <li key={b.bin_id} className="p-3 bg-orange-50 border border-orange-100 rounded text-sm">
                <b>{b.name}</b> · DCPI {b.dcpi.toFixed(0)} · {b.district}
              </li>
            ))}
          </ul>
        </section>
      )}

      {critical.length === 0 && high.length === 0 && (
        <p className="text-slate-500">No high-priority alerts. System nominal.</p>
      )}
    </div>
  );
}
