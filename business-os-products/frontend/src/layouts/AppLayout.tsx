import { LayoutGrid, Menu, Package, Users, X } from "lucide-react";
import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";

const NAV = [
  { to: "/dashboard", label: "Overview", icon: LayoutGrid },
  { to: "/products", label: "Products & Categories", icon: Package },
  { to: "/customers", label: "Customers CRM", icon: Users },
];

export default function AppLayout() {
  const [open, setOpen] = useState(false);

  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <header className="sticky top-0 z-30 flex items-center gap-3 border-b border-gray-200 bg-white p-4 md:hidden">
        <button type="button" aria-label="Open menu" onClick={() => setOpen(true)} className="rounded-lg p-1.5 text-gray-600 hover:bg-gray-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-600">
          <Menu className="h-6 w-6" />
        </button>
        <span className="text-sm font-bold">Wavespace OS</span>
      </header>

      {open && <div onClick={() => setOpen(false)} className="fixed inset-0 z-40 bg-black/40 md:hidden" />}

      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 shrink-0 border-r border-gray-200 bg-white p-4 transition-transform duration-300 md:static md:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600 text-xs font-bold text-white">W</div>
            <span className="text-sm font-semibold">Wavespace OS</span>
          </div>
          <button type="button" aria-label="Close menu" onClick={() => setOpen(false)} className="rounded-lg p-1 text-gray-500 hover:bg-gray-100 md:hidden">
            <X className="h-5 w-5" />
          </button>
        </div>
        <nav aria-label="Main" className="space-y-1 text-sm font-medium">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 transition-colors ${
                  isActive ? "bg-gray-100 font-semibold text-gray-900" : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                }`
              }
            >
              <Icon className="h-4 w-4" />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <main className="min-w-0 flex-1 space-y-6 p-4 sm:p-6 md:p-8">
        <Outlet />
      </main>
    </div>
  );
}
