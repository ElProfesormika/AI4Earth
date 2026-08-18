import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import LiveMap from "./modules/LiveMap";
import Prediction from "./modules/Prediction";
import RoutesModule from "./modules/Routes";
import DigitalTwin from "./modules/DigitalTwin";
import KPIs from "./modules/KPIs";
import Alerts from "./modules/Alerts";
import BinDetailPanel from "./components/BinDetailPanel";

const qc = new QueryClient();

const tabs = [
  { path: "/", label: "Live Map", el: <LiveMap /> },
  { path: "/predict", label: "Prediction", el: <Prediction /> },
  { path: "/routes", label: "Routes", el: <RoutesModule /> },
  { path: "/twin", label: "Digital Twin", el: <DigitalTwin /> },
  { path: "/kpis", label: "KPIs", el: <KPIs /> },
  { path: "/alerts", label: "Alerts", el: <Alerts /> },
];

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <div className="flex h-screen">
          <aside className="w-56 bg-slate-900 text-white p-4 flex flex-col">
            <h1 className="text-xl font-bold mb-1">SmartWasteAI</h1>
            <p className="text-xs text-slate-400 mb-6">AI4Earth · SmartAIthon 2026</p>
            <nav className="flex flex-col gap-2">
              {tabs.map((t) => (
                <NavLink
                  key={t.path}
                  to={t.path}
                  className={({ isActive }) =>
                    `px-3 py-2 rounded ${isActive ? "bg-orange-600" : "hover:bg-slate-800"}`
                  }
                >
                  {t.label}
                </NavLink>
              ))}
            </nav>
          </aside>
          <main className="flex-1 flex min-w-0">
            <div className="flex-1 min-w-0">
              <Routes>
                {tabs.map((t) => (
                  <Route key={t.path} path={t.path} element={t.el} />
                ))}
              </Routes>
            </div>
            <BinDetailPanel />
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
