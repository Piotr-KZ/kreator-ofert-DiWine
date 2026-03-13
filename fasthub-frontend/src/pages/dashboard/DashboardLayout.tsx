/**
 * Dashboard layout — top nav with tabs + outlet.
 * Brief 36.
 */

import { useEffect } from "react";
import { Outlet, Link, useLocation, useNavigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import { APP_CONFIG } from "@/config/app.config";

const tabs = [
  { path: "/panel", label: "Moje strony" },
  { path: "/panel/integrations", label: "Integracje" },
];

export default function DashboardLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const initials = user?.full_name
    ? user.full_name.split(" ").map((n: string) => n[0]).join("").toUpperCase().slice(0, 2)
    : APP_CONFIG.logo.icon;

  return (
    <div className="h-screen flex flex-col bg-gray-50" style={{ fontFamily: APP_CONFIG.theme.fontFamily }}>
      {/* Top nav */}
      <nav className="bg-gray-950 px-6 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-6">
          <Link to="/panel" className="flex items-center gap-2.5">
            <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${APP_CONFIG.logo.gradient} flex items-center justify-center`}>
              <span className="text-white font-extrabold text-sm">{APP_CONFIG.logo.icon}</span>
            </div>
            <span className="text-white font-bold text-lg hidden sm:inline">{APP_CONFIG.name}</span>
          </Link>

          {/* Tabs */}
          <div className="flex gap-1">
            {tabs.map((tab) => {
              const isActive =
                tab.path === "/panel"
                  ? location.pathname === "/panel" || location.pathname.startsWith("/panel/sites")
                  : location.pathname === tab.path;
              return (
                <Link
                  key={tab.path}
                  to={tab.path}
                  className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-white/15 text-white"
                      : "text-gray-400 hover:text-gray-200 hover:bg-white/5"
                  }`}
                >
                  {tab.label}
                </Link>
              );
            })}
          </div>
        </div>

        <div className="flex items-center gap-4">
          <Link
            to="/creator/new"
            className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm px-4 py-1.5 rounded-lg font-medium transition-colors"
          >
            + Nowa strona
          </Link>

          <div className="flex items-center gap-2 text-gray-300">
            <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-xs font-bold text-indigo-600">
              {initials}
            </div>
            <Link to="/account" className="text-sm hidden sm:inline hover:text-white transition-colors">
              {user?.full_name || "Konto"}
            </Link>
            <button onClick={handleLogout} className="text-gray-500 hover:text-red-400 ml-2" title="Wyloguj">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
