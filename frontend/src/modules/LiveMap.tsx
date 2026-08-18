import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import { useQuery } from "@tanstack/react-query";
import { listDCPI } from "../api/dcpi";
import type { DCPIItem } from "../types/domain";
import { useSelectionStore } from "../store/selection";
import { pollInterval } from "../api/client";
import { dcpiColor, DARK_TILES } from "../lib/theme";
import "leaflet/dist/leaflet.css";

export default function LiveMap() {
  const { data = [] } = useQuery<DCPIItem[]>({
    queryKey: ["dcpi"],
    queryFn: listDCPI,
    refetchInterval: pollInterval,
  });
  const selected = useSelectionStore((s) => s.selectedBin);
  const setSelectedBin = useSelectionStore((s) => s.setSelectedBin);
  const center: [number, number] = data.length
    ? [
        data.reduce((a, b) => a + b.lat, 0) / data.length,
        data.reduce((a, b) => a + b.lon, 0) / data.length,
      ]
    : [12.9716, 77.5946];

  const critical = data.filter((b) => b.dcpi >= 75).length;
  const high = data.filter((b) => b.dcpi >= 55 && b.dcpi < 75).length;

  return (
    <div className="h-full w-full relative">
      <MapContainer
        key={data.length ? "ready" : "empty"}
        center={center}
        zoom={13}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer attribution="&copy; OSM &copy; CARTO" url={DARK_TILES} />
        {data.map((b) => (
          <CircleMarker
            key={b.bin_id}
            center={[b.lat, b.lon]}
            radius={selected === b.bin_id ? 12 : 7 + b.dcpi / 14}
            pathOptions={{
              fillColor: dcpiColor(b.dcpi),
              color: selected === b.bin_id ? "#fff" : dcpiColor(b.dcpi),
              weight: selected === b.bin_id ? 2 : 1,
              fillOpacity: 0.85,
            }}
            eventHandlers={{ click: () => setSelectedBin(b.bin_id) }}
          >
            <Popup>
              <div className="min-w-[140px]">
                <p className="font-display font-semibold">{b.name}</p>
                <p className="text-mist-400 text-xs mt-0.5">{b.district}</p>
                <p className="mt-2 text-ember-400 font-mono">DCPI {b.dcpi.toFixed(0)}</p>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>

      <div className="absolute top-4 left-4 flex gap-2">
        <div className="rounded-2xl border border-white/10 bg-ink-900/85 backdrop-blur px-4 py-3 shadow-panel">
          <p className="text-[10px] uppercase tracking-[0.18em] text-mist-400">City pulse</p>
          <p className="font-display text-xl mt-0.5">{data.length} live bins</p>
          <p className="text-xs text-mist-400 mt-1">
            <span className="text-red-400">{critical} critical</span>
            <span className="mx-1.5 text-ink-600">·</span>
            <span className="text-ember-400">{high} high</span>
          </p>
        </div>
      </div>

      <div className="absolute bottom-4 left-4 rounded-2xl border border-white/10 bg-ink-900/90 backdrop-blur p-3 text-xs shadow-panel">
        <p className="text-[10px] uppercase tracking-[0.16em] text-mist-400 mb-2">DCPI legend</p>
        {[
          ["#3dcc7a", "Stable"],
          ["#f59e0b", "Watch"],
          ["#e85d25", "High"],
          ["#ef4444", "Critical"],
        ].map(([c, l]) => (
          <div key={l} className="flex gap-2 items-center py-0.5">
            <span className="w-2.5 h-2.5 rounded-full" style={{ background: c }} />
            {l}
          </div>
        ))}
      </div>
    </div>
  );
}
