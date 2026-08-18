import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { MapContainer, TileLayer, CircleMarker, Polyline, Popup } from "react-leaflet";
import { getTodayRoute, optimizeRoute } from "../api/routes";
import { listDCPI } from "../api/dcpi";
import KPICard from "../components/KPICard";

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
    <div className="h-full flex flex-col">
      <div className="p-4 flex gap-4 items-center border-b bg-white">
        <button
          onClick={() => optimize.mutate()}
          disabled={optimize.isPending}
          className="px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700 disabled:opacity-50"
        >
          {optimize.isPending ? "Optimizing..." : "Optimize Route"}
        </button>
        {route && (
          <>
            <KPICard label="Distance" value={`${route.distance_km.toFixed(1)} km`} />
            <KPICard label="Fuel saving" value={`${route.expected_fuel_saving_pct}%`} />
            <KPICard label="CO₂ saved" value={`${route.expected_co2_saving_kg} kg`} accent="text-green-600" />
          </>
        )}
      </div>
      <div className="flex-1">
        {isLoading ? (
          <p className="p-6">Loading route...</p>
        ) : (
          <MapContainer center={DEPOT} zoom={13} style={{ height: "100%", width: "100%" }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            <CircleMarker center={DEPOT} radius={10} pathOptions={{ fillColor: "#2563EB", color: "#111" }}>
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
                  pathOptions={{ fillColor: "#EA580C", color: "#111" }}
                >
                  <Popup>
                    Stop {i + 1}: {b.name} (DCPI {b.dcpi.toFixed(0)})
                  </Popup>
                </CircleMarker>
              );
            })}
            {polyline.length > 1 && <Polyline positions={polyline} pathOptions={{ color: "#EA580C", weight: 3 }} />}
          </MapContainer>
        )}
      </div>
    </div>
  );
}
