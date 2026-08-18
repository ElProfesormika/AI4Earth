import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { useMutation, useQuery } from "@tanstack/react-query";
import { listDCPI } from "../api/dcpi";
import { runSimulation } from "../api/kpis";
import { useState } from "react";

function Bin3D({ position, dcpi }: { position: [number, number, number]; dcpi: number }) {
  const color = dcpi >= 75 ? "#DC2626" : dcpi >= 55 ? "#E85D25" : dcpi >= 35 ? "#D97706" : "#16A34A";
  const height = 0.5 + (dcpi / 100) * 2.5;
  return (
    <mesh position={[position[0], height / 2, position[2]]}>
      <cylinderGeometry args={[0.3, 0.3, height, 12]} />
      <meshStandardMaterial color={color} />
    </mesh>
  );
}

export default function DigitalTwin() {
  const { data = [] } = useQuery({ queryKey: ["dcpi"], queryFn: listDCPI, refetchInterval: 5000 });
  const [simResult, setSimResult] = useState<string | null>(null);
  const bins = data.slice(0, 40);

  const simulate = useMutation({
    mutationFn: () => runSimulation("festival", "Market"),
    onSuccess: (r) => setSimResult(r.message),
  });

  return (
    <div className="h-full w-full bg-slate-800 relative">
      <Canvas camera={{ position: [15, 12, 15], fov: 50 }}>
        <ambientLight intensity={0.4} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <gridHelper args={[20, 20, "#444", "#333"]} />
        {bins.map((b, i) => {
          const x = (i % 8) - 4;
          const z = Math.floor(i / 8) - 2.5;
          return <Bin3D key={b.bin_id} position={[x * 2, 0, z * 2]} dcpi={b.dcpi} />;
        })}
        <OrbitControls />
      </Canvas>
      <div className="absolute top-4 left-4 bg-white/90 p-3 rounded max-w-sm">
        <p className="text-sm font-bold">Digital Twin · {bins.length} bins</p>
        <p className="text-xs text-slate-500 mb-2">Height ∝ DCPI · Color = urgency</p>
        <button
          onClick={() => simulate.mutate()}
          className="text-xs px-3 py-1 bg-orange-600 text-white rounded"
        >
          Run festival scenario
        </button>
        {simResult && <p className="text-xs mt-2 text-slate-700">{simResult}</p>}
      </div>
    </div>
  );
}
