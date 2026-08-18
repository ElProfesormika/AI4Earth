import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { MapContainer, TileLayer, CircleMarker, Polyline, Popup } from "react-leaflet";
import { getTodayRoute, optimizeRoute } from "../api/routes";
import { listDCPI } from "../api/dcpi";
import KPICard from "../components/KPICard";
import { DARK_TILES } from "../lib/theme";
import "leaflet/dist/leaflet.css";

const DEPOT: [number, number] = [12.9716, 77.5946];

export default function RoutesModule() {
  const qc = useQueryClient();
  const { data: route, isLoading } = useQuery({
    queryKey: ["route-today"],
    queryFn: getTodayRoute,
    refetchInterval: 30000,
  });
  const { data: dcpi = [] } = useQuery({ queryKey: ["dcpi"], queryFn: listDCPI });

  const optimize = useMutation({
    mutationFn: optimizeRoute,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["route-today"] }),
  });

  const binMap = Object.fromEntries(dcpi.map((b) => [b.bin_id, b]));
  const stops = route?.stops ?? [];
  const polyline: [number, number][] = [
    DEPOT,
    ...stops.map((id) => [binMap[id]?.lat ?? DEPOT[0], binMap[id]?.lon ?? DEPOT[1]] as [number, number]),
    DEPOT,
  ];

  return (
    <div className="h-full flex flex-col bg-ink-950">
      <div className="px-6 py-4 flex flex-wrap gap-3 items-center border-b border-white/10 bg-ink-900/70">
        <div className="mr-auto">
          <p className="text-[10px] uppercase tracking-[0.2em] text-ember-400">OR-Tools</p>
          <h2 className="font-display text-xl font-semibold">Collection tour</h2>
        </div>
        <button
          onClick={() => optimize.mutate()}
          disabled={optimize.isPending}
          className="px-4 py-2.5 bg-ember-600 text-white rounded-xl font-medium text-sm hover:bg-ember-500 disabled:opacity-50 shadow-glow"
        >
          {optimize.isPending ? "Optimizing…" : "Optimize route"}
        </button>
        {route && (
          <>
            <KPICard label="Distance" value={`${route.distance_km.toFixed(1)} km`} tone="mist" />
            <KPICard label="Fuel saving" value={`${route.expected_fuel_saving_pct}%`} />
            <KPICard label="CO₂ saved" value={`${route.expected_co2_saving_kg} kg`} tone="moss" />
          </>
        )}
      </div>
      <div className="flex-1 min-h-0">
        {isLoading ? (
          <p className="p-6 text-mist-400">Loading route…</p>
        ) : (
          <MapContainer center={DEPOT} zoom={13} style={{ height: "100%", width: "100%" }}>
            <TileLayer url={DARK_TILES} />
            <CircleMarker center={DEPOT} radius={11} pathOptions={{ fillColor: "#60a5fa", color: "#93c5fd", weight: 2 }}>
              <Popup>Depot</Popup>
            </CircleMarker>
            {stops.map((id, i) => {
              const b = binMap[id];
              if (!b) return null;
              return (
                <CircleMarker
                  key={id}
                  center={[b.lat, b.lon]}
                  radius={8}
                  pathOptions={{ fillColor: "#e85d25", color: "#ffb347", weight: 1.5 }}
                >
                  <Popup>
                    Stop {i + 1}: {b.name} (DCPI {b.dcpi.toFixed(0)})
                  </Popup>
                </CircleMarker>
              );
            })}
            {polyline.length > 1 && (
              <Polyline positions={polyline} pathOptions={{ color: "#f08c2e", weight: 3, opacity: 0.9 }} />
            )}
          </MapContainer>
        )}
      </div>
    </div>
  );
}
