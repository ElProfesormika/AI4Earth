import { QueryClient, QueryClientProvider, useQuery } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, NavLink, useLocation } from "react-router-dom";
import LiveMap from "./modules/LiveMap";
import Prediction from "./modules/Prediction";
import RoutesModule from "./modules/Routes";
import DigitalTwin from "./modules/DigitalTwin";
import KPIs from "./modules/KPIs";
import Alerts from "./modules/Alerts";
import BinDetailPanel from "./components/BinDetailPanel";
import { listDCPI } from "./api/dcpi";
import { pollInterval } from "./api/client";
import { IconBell, IconChart, IconCube, IconGauge, IconMap, IconRoute } from "./components/Icons";

const qc = new QueryClient();

const tabs = [
  { path: "/", label: "Live Map", el: <LiveMap />, icon: IconMap },
  { path: "/predict", label: "Prediction", el: <Prediction />, icon: IconChart },
  { path: "/routes", label: "Routes", el: <RoutesModule />, icon: IconRoute },
  { path: "/twin", label: "Digital Twin", el: <DigitalTwin />, icon: IconCube },
  { path: "/kpis", label: "KPIs", el: <KPIs />, icon: IconGauge },
  { path: "/alerts", label: "Alerts", el: <Alerts />, icon: IconBell },
];

function Shell() {
  const location = useLocation();
  const { data = [] } = useQuery({
    queryKey: ["dcpi"],
    queryFn: listDCPI,
    refetchInterval: pollInterval,
  });
  const critical = data.filter((b) => b.dcpi >= 75).length;
  const current = tabs.find((t) => t.path === location.pathname)?.label ?? "Live Map";

  return (
    <div className="flex h-screen bg-ink-950 text-mist-100 overflow-hidden">
      <aside className="w-[232px] shrink-0 bg-ink-900 border-r border-white/10 flex flex-col">
        <div className="px-5 pt-6 pb-5">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-ember-600/20 border border-ember-500/40 grid place-items-center font-display text-ember-400 text-sm">
              SW
            </div>
            <div>
              <h1 className="font-display text-[17px] font-semibold leading-tight">SmartWasteAI</h1>
              <p className="text-[10px] uppercase tracking-[0.16em] text-mist-400">Command center</p>
            </div>
          </div>
        </div>

        <nav className="px-3 flex flex-col gap-1 flex-1">
          {tabs.map((t) => {
            const Icon = t.icon;
            return (
              <NavLink
                key={t.path}
                to={t.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition ${
                    isActive
                      ? "bg-ember-600 text-white shadow-glow"
                      : "text-mist-400 hover:bg-white/5 hover:text-mist-100"
                  }`
                }
              >
                <Icon className="w-[18px] h-[18px]" />
                {t.label}
              </NavLink>
            );
          })}
        </nav>

        <div className="p-4 m-3 rounded-2xl border border-white/10 bg-ink-800">
          <div className="flex items-center gap-2 text-xs">
            <span className="w-1.5 h-1.5 rounded-full bg-moss-400 live-dot" />
            <span className="text-mist-400">MQTT live</span>
          </div>
          <p className="font-display text-lg mt-1 tabular-nums">{data.length} bins</p>
          <p className="text-[11px] text-mist-500">4 districts · DemoCity</p>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-14 shrink-0 border-b border-white/10 px-6 flex items-center justify-between bg-ink-900/60 backdrop-blur">
          <div className="flex items-center gap-3 text-sm">
            <span className="text-mist-400">AI4Earth</span>
            <span className="text-ink-600">/</span>
            <span className="font-medium">{current}</span>
          </div>
          <div className="flex items-center gap-4 text-xs">
            <span className="hidden sm:inline text-mist-400">SmartAIthon 2026 · Round 2</span>
            {critical > 0 && (
              <span className="px-2.5 py-1 rounded-full bg-red-500/15 text-red-400 border border-red-500/30">
                {critical} critical
              </span>
            )}
          </div>
        </header>
        <main className="flex-1 flex min-h-0">
          <div className="flex-1 min-w-0 overflow-hidden">
            <Routes>
              {tabs.map((t) => (
                <Route key={t.path} path={t.path} element={t.el} />
              ))}
            </Routes>
          </div>
          <BinDetailPanel />
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <Shell />
      </BrowserRouter>
    </QueryClientProvider>
  );
}
