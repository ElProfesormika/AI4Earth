import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { useMutation, useQuery } from "@tanstack/react-query";
import { listDCPI } from "../api/dcpi";
import { runSimulation } from "../api/kpis";
import { useState } from "react";
import { dcpiColor } from "../lib/theme";

function Bin3D({ position, dcpi }: { position: [number, number, number]; dcpi: number }) {
  const height = 0.5 + (dcpi / 100) * 2.5;
  return (
    <mesh position={[position[0], height / 2, position[2]]}>
      <cylinderGeometry args={[0.28, 0.32, height, 16]} />
      <meshStandardMaterial color={dcpiColor(dcpi)} metalness={0.25} roughness={0.4} />
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
    <div className="h-full w-full bg-ink-950 relative">
      <Canvas camera={{ position: [15, 12, 15], fov: 50 }}>
        <color attach="background" args={["#07090b"]} />
        <fog attach="fog" args={["#07090b", 18, 42]} />
        <ambientLight intensity={0.35} />
        <directionalLight position={[10, 14, 5]} intensity={1.1} />
        <pointLight position={[-8, 6, -4]} color="#e85d25" intensity={0.4} />
        <gridHelper args={[22, 22, "#24303a", "#1a232c"]} />
        {bins.map((b, i) => {
          const x = (i % 8) - 4;
          const z = Math.floor(i / 8) - 2.5;
          return <Bin3D key={b.bin_id} position={[x * 2, 0, z * 2]} dcpi={b.dcpi} />;
        })}
        <OrbitControls />
      </Canvas>
      <div className="absolute top-5 left-5 rounded-2xl border border-white/10 bg-ink-900/90 p-4 max-w-sm backdrop-blur shadow-panel">
        <p className="text-[10px] uppercase tracking-[0.2em] text-ember-400">Digital twin</p>
        <p className="font-display text-lg font-semibold mt-1">{bins.length} bins · DemoCity</p>
        <p className="text-xs text-mist-400 mt-1 mb-3">Height ∝ DCPI · color = urgency. Drag to orbit.</p>
        <button
          onClick={() => simulate.mutate()}
          className="text-sm px-3 py-2 bg-ember-600 text-white rounded-xl hover:bg-ember-500"
        >
          Run festival scenario
        </button>
        {simResult && <p className="text-xs mt-3 text-moss-400 leading-relaxed">{simResult}</p>}
      </div>
    </div>
  );
}
