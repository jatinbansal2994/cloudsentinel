import { useState, useEffect } from "react";
import { getAlerts } from "../api";

const SEVERITY = {
  high:   "bg-red-100 text-red-700",
  medium: "bg-yellow-100 text-yellow-700",
  low:    "bg-green-100 text-green-700",
};

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getAlerts()
      .then(setAlerts)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-gray-500 text-sm">Loading alerts…</p>;
  if (error)   return <p className="text-red-600 text-sm">{error}</p>;

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Anomaly Alerts</h2>
      {alerts.length === 0 ? (
        <p className="text-gray-500 text-sm">No alerts found.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm border-collapse">
            <thead>
              <tr className="bg-gray-100 text-gray-600 text-left">
                <th className="px-4 py-2 font-medium">Alert ID</th>
                <th className="px-4 py-2 font-medium">Tenant</th>
                <th className="px-4 py-2 font-medium">Score</th>
                <th className="px-4 py-2 font-medium">Severity</th>
                <th className="px-4 py-2 font-medium">Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((a) => (
                <tr key={a.alertId} className="border-t hover:bg-gray-50">
                  <td className="px-4 py-2 font-mono text-xs text-gray-500">{a.alertId}</td>
                  <td className="px-4 py-2">{a.tenantId}</td>
                  <td className="px-4 py-2">{typeof a.score === "number" ? a.score.toFixed(4) : a.score}</td>
                  <td className="px-4 py-2">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${SEVERITY[a.severity] ?? "bg-gray-100 text-gray-600"}`}>
                      {a.severity ?? "unknown"}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-gray-500">{a.timestamp ? new Date(a.timestamp).toLocaleString() : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
