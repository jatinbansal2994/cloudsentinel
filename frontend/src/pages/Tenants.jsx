import { useState, useEffect } from "react";
import { getTenants, postTenant } from "../api";
import { useAuth } from "../useAuth.jsx";

export default function Tenants() {
  const { user } = useAuth();
  const [tenant, setTenant] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [form, setForm] = useState({ name: "", plan: "free" });
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState("");

  function load() {
    setLoading(true);
    getTenants()
      .then((items) => {
        const t = items[0] ?? null;
        setTenant(t);
        if (t) setForm({ name: t.name ?? "", plan: t.plan ?? "free" });
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  async function handleSave(e) {
    e.preventDefault();
    setSubmitting(true);
    setSuccess("");
    setError("");
    try {
      await postTenant(form);
      setSuccess("Account saved.");
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-lg space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-800">My Account</h2>
        <p className="text-sm text-gray-500 mt-1">
          Tenant ID: <span className="font-mono text-indigo-600">{user?.["custom:tenantId"] ?? "—"}</span>
        </p>
      </div>

      {loading ? (
        <p className="text-gray-500 text-sm">Loading…</p>
      ) : (
        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Display name</label>
            <input
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
              placeholder="e.g. Acme Corp"
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Plan</label>
            <select
              value={form.plan}
              onChange={(e) => setForm({ ...form, plan: e.target.value })}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="free">Free</option>
              <option value="pro">Pro</option>
              <option value="enterprise">Enterprise</option>
            </select>
          </div>
          {error   && <p className="text-red-600 text-sm">{error}</p>}
          {success && <p className="text-green-600 text-sm">{success}</p>}
          <button
            type="submit"
            disabled={submitting}
            className="bg-indigo-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
          >
            {submitting ? "Saving…" : tenant ? "Save changes" : "Set up account"}
          </button>
        </form>
      )}
    </div>
  );
}
