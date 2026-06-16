import { useState, useEffect } from "react";
import { getAdminTenants, postAdminTenant, getAdminAlerts } from "../api";

const SEVERITY = {
  critical: "bg-red-700 text-white",
  high:     "bg-red-100 text-red-700",
  medium:   "bg-yellow-100 text-yellow-700",
  low:      "bg-green-100 text-green-700",
};

const PLANS = ["free", "pro", "enterprise"];

function TenantsTab() {
  const [tenants, setTenants]   = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState("");
  const [form, setForm]         = useState({ email: "", name: "", plan: "free", password: "" });
  const [creating, setCreating] = useState(false);
  const [createMsg, setCreateMsg] = useState("");

  useEffect(() => {
    getAdminTenants()
      .then(setTenants)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  async function handleCreate(e) {
    e.preventDefault();
    setCreating(true);
    setCreateMsg("");
    try {
      const res = await postAdminTenant(form);
      setCreateMsg(`Created: ${res.tenantId}`);
      setForm({ email: "", name: "", plan: "free", password: "" });
      const updated = await getAdminTenants();
      setTenants(updated);
    } catch (err) {
      setCreateMsg(`Error: ${err.message}`);
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="space-y-8">
      {/* Tenant table */}
      <div>
        <h3 className="text-base font-semibold text-gray-700 mb-3">All Tenants</h3>
        {loading && <p className="text-gray-500 text-sm">Loading…</p>}
        {error   && <p className="text-red-600 text-sm">{error}</p>}
        {!loading && !error && tenants.length === 0 && (
          <p className="text-gray-500 text-sm">No tenants yet.</p>
        )}
        {tenants.length > 0 && (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm border-collapse">
              <thead>
                <tr className="bg-gray-100 text-gray-600 text-left">
                  <th className="px-4 py-2 font-medium">Tenant ID</th>
                  <th className="px-4 py-2 font-medium">Name</th>
                  <th className="px-4 py-2 font-medium">Email</th>
                  <th className="px-4 py-2 font-medium">Plan</th>
                  <th className="px-4 py-2 font-medium">Created</th>
                </tr>
              </thead>
              <tbody>
                {tenants.map((t) => (
                  <tr key={t.tenantId} className="border-t hover:bg-gray-50">
                    <td className="px-4 py-2 font-mono text-xs text-gray-500">{t.tenantId}</td>
                    <td className="px-4 py-2">{t.name ?? "—"}</td>
                    <td className="px-4 py-2 text-gray-600">{t.email ?? "—"}</td>
                    <td className="px-4 py-2">
                      <span className="px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-700">
                        {t.plan ?? "free"}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-gray-500">
                      {t.createdAt ? new Date(t.createdAt).toLocaleString() : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create tenant form */}
      <div className="border-t pt-6">
        <h3 className="text-base font-semibold text-gray-700 mb-4">Create Tenant</h3>
        <form onSubmit={handleCreate} className="grid grid-cols-1 gap-4 max-w-md">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Email (login username)</label>
            <input
              type="email"
              required
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
              placeholder="user@example.com"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Tenant display name</label>
            <input
              type="text"
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
              placeholder="Acme Corp"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Plan</label>
            <select
              value={form.plan}
              onChange={(e) => setForm({ ...form, plan: e.target.value })}
              className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            >
              {PLANS.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Initial password</label>
            <input
              type="password"
              required
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
              placeholder="Min 8 chars, upper + lower + number"
            />
          </div>
          <div className="flex items-center gap-4">
            <button
              type="submit"
              disabled={creating}
              className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded"
            >
              {creating ? "Creating…" : "Create Tenant"}
            </button>
            {createMsg && (
              <span className={`text-sm ${createMsg.startsWith("Error") ? "text-red-600" : "text-green-600"}`}>
                {createMsg}
              </span>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}

function AlertsTab() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState("");

  useEffect(() => {
    getAdminAlerts()
      .then(setAlerts)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-gray-500 text-sm">Loading alerts…</p>;
  if (error)   return <p className="text-red-600 text-sm">{error}</p>;

  return (
    <div>
      <h3 className="text-base font-semibold text-gray-700 mb-3">All Alerts (cross-tenant)</h3>
      {alerts.length === 0 ? (
        <p className="text-gray-500 text-sm">No alerts found.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm border-collapse">
            <thead>
              <tr className="bg-gray-100 text-gray-600 text-left">
                <th className="px-4 py-2 font-medium">Tenant</th>
                <th className="px-4 py-2 font-medium">Alert ID</th>
                <th className="px-4 py-2 font-medium">Score</th>
                <th className="px-4 py-2 font-medium">Severity</th>
                <th className="px-4 py-2 font-medium">Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((a) => (
                <tr key={a.alertId} className="border-t hover:bg-gray-50">
                  <td className="px-4 py-2 font-mono text-xs text-gray-500">{a.tenantId}</td>
                  <td className="px-4 py-2 font-mono text-xs text-gray-400">{a.alertId}</td>
                  <td className="px-4 py-2">{typeof a.score === "number" ? a.score.toFixed(4) : a.score}</td>
                  <td className="px-4 py-2">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${SEVERITY[a.severity] ?? "bg-gray-100 text-gray-600"}`}>
                      {a.severity ?? "unknown"}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-gray-500">
                    {a.createdAt ? new Date(a.createdAt).toLocaleString() : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default function Admin() {
  const [tab, setTab] = useState("tenants");

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Admin Panel</h2>

      {/* Tab bar */}
      <div className="flex gap-1 mb-6 border-b">
        {[{ id: "tenants", label: "Tenants" }, { id: "alerts", label: "Alerts" }].map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors ${
              tab === t.id
                ? "border-indigo-600 text-indigo-700"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "tenants" && <TenantsTab />}
      {tab === "alerts"  && <AlertsTab />}
    </div>
  );
}
