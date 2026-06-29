import { useState } from "react";
import { postIngest } from "../api";

// Anomalous values — high CPU/memory, spiked latency, elevated errors — will trigger an alert.
// Normal ranges: cpu_util 10–70, memory_util 35–75, latency_ms 40–200, error_rate 0–0.05, request_count 300–700
const DEFAULT_PAYLOAD = JSON.stringify(
  { cpu_util: 95, memory_util: 93, latency_ms: 4200, error_rate: 0.82, request_count: 4500 },
  null,
  2
);

export default function Ingest() {
  const [payload, setPayload] = useState(DEFAULT_PAYLOAD);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setResult(null);
    setSubmitting(true);
    try {
      const body = JSON.parse(payload);
      const res = await postIngest(body);
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-800 mb-1">Ingest Telemetry</h2>
      <p className="text-sm text-gray-500 mb-4">Send a test event to the pipeline. The stream-processor picks it up and scores it via SageMaker.</p>
      <form onSubmit={handleSubmit} className="space-y-4 max-w-lg">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">JSON Payload</label>
          <p className="text-xs text-gray-400 mb-1">
            Tip: values above trigger an alert. For normal traffic try cpu_util&nbsp;45, memory_util&nbsp;60, latency_ms&nbsp;120, error_rate&nbsp;0.01, request_count&nbsp;200.
          </p>
          <textarea
            rows={10}
            value={payload}
            onChange={(e) => setPayload(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        {error && <p className="text-red-600 text-sm">{error}</p>}
        {result && (
          <pre className="bg-gray-100 rounded p-3 text-xs overflow-x-auto">
            {JSON.stringify(result, null, 2)}
          </pre>
        )}
        <button
          type="submit"
          disabled={submitting}
          className="bg-indigo-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
        >
          {submitting ? "Sending…" : "Send Event"}
        </button>
      </form>
    </div>
  );
}
