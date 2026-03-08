import { Outlet, Link, useLocation } from "react-router-dom";

export default function AppShell() {
  const loc = useLocation();
  const tabs = [
    { path: "/sites", name: "Moje strony" },
    { path: "/dashboard", name: "Dashboard" },
    { path: "/integrations", name: "Integracje" },
  ];

  return (
    <div className="h-screen flex flex-col bg-gray-50" style={{ fontFamily: "'Outfit', system-ui, sans-serif" }}>
      <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />

      {/* Header */}
      <nav className="bg-gray-950 px-6 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-4">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <span className="text-white font-extrabold text-sm">W</span>
            </div>
            <span className="text-white font-bold text-lg">WebCreator</span>
          </Link>
          <div className="flex items-center gap-1 ml-4">
            {tabs.map(t => (
              <Link key={t.path} to={t.path}
                className={`text-sm font-medium px-4 py-2 rounded-lg transition-all ${loc.pathname.startsWith(t.path) ? "text-white bg-white/10" : "text-gray-400 hover:text-white hover:bg-white/5"}`}>
                {t.name}
              </Link>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/account" className="flex items-center gap-2 text-gray-300 hover:text-white">
            <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-xs font-bold text-indigo-600">JK</div>
            <span className="text-sm">Konto</span>
          </Link>
        </div>
      </nav>

      {/* Content */}
      <div className="flex-1 overflow-auto p-8">
        <Outlet />
      </div>
    </div>
  );
}
