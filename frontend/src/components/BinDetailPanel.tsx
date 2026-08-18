import { useQuery } from "@tanstack/react-query";
import { useSelectionStore } from "../store/selection";
import { getDCPI } from "../api/dcpi";

export default function BinDetailPanel() {
  const selectedBin = useSelectionStore((s) => s.selectedBin);
  const { data } = useQuery({
    queryKey: ["dcpi-detail", selectedBin],
    queryFn: () => (selectedBin ? getDCPI(selectedBin) : Promise.resolve(null)),
    enabled: !!selectedBin,
    refetchInterval: 5000,
  });

  if (!selectedBin || !data) {
    return <aside className="w-80 border-l bg-slate-50" />;
  }

  return (
    <aside className="w-80 border-l bg-slate-50 p-4 overflow-y-auto">
      <h2 className="text-lg font-bold">Bin #{data.bin_id}</h2>
      <p className="text-4xl font-bold text-orange-600 my-3">{data.dcpi.toFixed(0)}</p>
      <p className="text-sm text-slate-500 uppercase tracking-wider">DCPI · Priority</p>

      <h3 className="mt-6 font-semibold">Why this priority?</h3>
      <ul className="mt-2 text-sm space-y-1">
        {data.reasons.map((r) => (
          <li key={r.feature}>
            <b>{r.feature}</b>: contribution {r.contribution.toFixed(1)}
          </li>
        ))}
      </ul>

      <h3 className="mt-6 font-semibold">Sensor snapshot</h3>
      <dl className="mt-2 text-sm">
        {Object.entries(data.features).map(([k, v]) => (
          <div key={k} className="flex justify-between border-b py-1">
            <dt>{k}</dt>
            <dd className="font-mono">{v.toFixed(1)}</dd>
          </div>
        ))}
      </dl>
    </aside>
  );
}
