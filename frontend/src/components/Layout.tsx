import { NavLink, Outlet } from "react-router-dom";
import { t } from "../i18n";

const tabs = [
  { to: "/", label: "nav_home", icon: "🏠" },
  { to: "/tariffs", label: "nav_tariffs", icon: "💳" },
  { to: "/connect", label: "nav_connect", icon: "🔌" },
  { to: "/referral", label: "nav_referral", icon: "🎁" },
  { to: "/help", label: "nav_help", icon: "❓" },
] as const;

export default function Layout() {
  return (
    <div className="flex h-full flex-col">
      <main className="flex-1 overflow-y-auto px-4 pb-24 pt-4">
        <Outlet />
      </main>
      <nav
        className="fixed inset-x-0 bottom-0 grid grid-cols-5 border-t"
        style={{
          background: "var(--tg-theme-secondary-bg-color, #232e3c)",
          borderColor: "var(--tg-theme-section-separator-color, #1a2734)",
        }}
      >
        {tabs.map((tab) => (
          <NavLink
            key={tab.to}
            to={tab.to}
            end
            className={({ isActive }) =>
              `flex flex-col items-center justify-center gap-1 py-2 text-xs transition-opacity ${
                isActive ? "opacity-100" : "opacity-60"
              }`
            }
            style={({ isActive }) => ({
              color: isActive
                ? "var(--tg-theme-button-color, #2ea6ff)"
                : "var(--tg-theme-text-color, #fff)",
            })}
          >
            <span className="text-lg">{tab.icon}</span>
            <span>{t(tab.label)}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
