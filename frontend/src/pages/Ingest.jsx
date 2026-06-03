import { useState } from "react";
import { postIngest } from "../api";

const DEFAULT_PAYLOAD = JSON.stringify(
  { tenantId: "tenant-1", metrics: { cpu: 0.45, memory: 0.6, latency: 120, error_rate: 0.01 } },
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
