import { useState } from "react";
import { AuthProvider, useAuth } from "./useAuth.jsx";
import Login from "./pages/Login";
import Alerts from "./pages/Alerts";
import Tenants from "./pages/Tenants";
import Ingest from "./pages/Ingest";
import Admin from "./pages/Admin";

const BASE_NAV = [
  { id: "alerts",  label: "Alerts"   },
  { id: "tenants", label: "Account"  },
  { id: "ingest",  label: "Ingest"   },
];

function Dashboard() {
  const { user, logout } = useAuth();
  const [page, setPage] = useState("alerts");

  const groups = user?.["cognito:groups"] ?? [];
  const isAdmin = Array.isArray(groups)
    ? groups.includes("cloudsentinel-admins")
    : groups === "cloudsentinel-admins";

  const nav = isAdmin
    ? [...BASE_NAV, { id: "admin", label: "Admin" }]
    : BASE_NAV;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-indigo-700 text-white px-6 py-3 flex items-center justify-between shadow">
        <span className="font-bold text-lg">CloudSentinel</span>
        <div className="flex items-center gap-4">
          <span className="text-sm text-indigo-200">{user?.email ?? user?.["cognito:username"]}</span>
          <button
            onClick={logout}
            className="text-sm bg-indigo-900 hover:bg-indigo-800 px-3 py-1 rounded"
          >
            Sign out
          </button>
        </div>
      </header>

      <div className="flex flex-1">
        <nav className="w-48 bg-white border-r pt-6 px-3 space-y-1">
          {nav.map((n) => (
            <button
              key={n.id}
              onClick={() => setPage(n.id)}
              className={`w-full text-left px-3 py-2 rounded text-sm font-medium ${
                page === n.id
                  ? "bg-indigo-50 text-indigo-700"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
            >
              {n.label}
            </button>
          ))}
        </nav>

        <main className="flex-1 p-8">
          {page === "alerts"  && <Alerts />}
          {page === "tenants" && <Tenants />}
          {page === "ingest"  && <Ingest />}
          {page === "admin"   && <Admin />}
        </main>
      </div>
    </div>
  );
}

function Root() {
  const { user } = useAuth();
  if (user === undefined) return (
    <div className="min-h-screen flex items-center justify-center text-gray-400 text-sm">
      Loading…
    </div>
  );
  return user ? <Dashboard /> : <Login />;
}

export default function App() {
  return (
    <AuthProvider>
      <Root />
    </AuthProvider>
  );
}
