import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import { useQuery } from "@tanstack/react-query";
import { listDCPI } from "../api/dcpi";
import type { DCPIItem } from "../types/domain";
import { useSelectionStore } from "../store/selection";
import { pollInterval } from "../api/client";
import "leaflet/dist/leaflet.css";

function dcpiColor(v: number) {
  if (v >= 75) return "#DC2626";
  if (v >= 55) return "#E85D25";
  if (v >= 35) return "#D97706";
  return "#16A34A";
}

export default function LiveMap() {
  const { data = [] } = useQuery<DCPIItem[]>({
    queryKey: ["dcpi"],
    queryFn: listDCPI,
    refetchInterval: pollInterval,
  });
  const setSelectedBin = useSelectionStore((s) => s.setSelectedBin);
  const center: [number, number] = data.length
    ? [data.reduce((a, b) => a + b.lat, 0) / data.length, data.reduce((a, b) => a + b.lon, 0) / data.length]
    : [12.9716, 77.5946];

  return (
    <div className="h-full w-full relative">
      <MapContainer center={center} zoom={13} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {data.map((b) => (
          <CircleMarker
            key={b.bin_id}
            center={[b.lat, b.lon]}
            radius={8 + b.dcpi / 12}
            pathOptions={{
              fillColor: dcpiColor(b.dcpi),
              color: "#111",
              weight: 1,
              fillOpacity: 0.85,
            }}
            eventHandlers={{ click: () => setSelectedBin(b.bin_id) }}
          >
            <Popup>
              <b>{b.name}</b>
              <br />
              DCPI: <b>{b.dcpi.toFixed(0)}</b>
              <br />
              District: {b.district}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
      <div className="absolute bottom-4 left-4 bg-white/90 p-3 rounded shadow text-xs">
        <p className="font-bold mb-1">DCPI legend</p>
        <div className="flex gap-2 items-center"><span className="w-3 h-3 rounded-full bg-green-600" /> Low</div>
        <div className="flex gap-2 items-center"><span className="w-3 h-3 rounded-full bg-yellow-600" /> Medium</div>
        <div className="flex gap-2 items-center"><span className="w-3 h-3 rounded-full bg-orange-600" /> High</div>
        <div className="flex gap-2 items-center"><span className="w-3 h-3 rounded-full bg-red-600" /> Critical</div>
      </div>
    </div>
  );
}
