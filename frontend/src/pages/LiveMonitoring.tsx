import { useEffect, useState } from "react";
import { fetchPreview, fetchStatus, startMonitoring, stopMonitoring } from "../api/webcam";

const LiveMonitoring = () => {
  const [status, setStatus] = useState<any | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const refreshStatus = async () => {
    const data = await fetchStatus();
    setStatus(data);
  };

  useEffect(() => {
    refreshStatus();
  }, []);

  useEffect(() => {
    let timer: number | undefined;
    if (status?.monitoring_active) {
      timer = window.setInterval(async () => {
        try {
          const data = await fetchPreview();
          setPreview(data.frame_base64);
          setResults(data.recognition_results || []);
        } catch {
          // ignore
        }
      }, 1500);
    }
    return () => {
      if (timer) window.clearInterval(timer);
    };
  }, [status?.monitoring_active]);

  const handleStart = async () => {
    setLoading(true);
    try {
      await startMonitoring();
      await refreshStatus();
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    setLoading(true);
    try {
      await stopMonitoring();
      await refreshStatus();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="stack">
      <div className="card">
        <div className="row-between">
          <div>
            <h3>Live Monitoring</h3>
            <p className="muted">
              Start the webcam to track recognized students and staff in real-time.
            </p>
          </div>
          <div className="row">
            <button className="primary" onClick={handleStart} disabled={loading}>
              Start
            </button>
            <button className="danger" onClick={handleStop} disabled={loading}>
              Stop
            </button>
          </div>
        </div>
        <div className="status-row">
          <span className={status?.monitoring_active ? "dot active" : "dot"} />
          <span>
            {status?.monitoring_active ? "Monitoring Active" : "Monitoring Stopped"}
          </span>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <h4>Webcam Preview</h4>
          {preview ? (
            <img
              className="preview"
              src={`data:image/jpeg;base64,${preview}`}
              alt="Webcam preview"
            />
          ) : (
            <div className="muted">Preview will appear when monitoring starts.</div>
          )}
        </div>
        <div className="card">
          <h4>Latest Detections</h4>
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Attendance</th>
              </tr>
            </thead>
            <tbody>
              {results.map((result, index) => (
                <tr key={`${result.name}-${index}`}>
                  <td>{result.name}</td>
                  <td className={result.recognized ? "badge success" : "badge warning"}>
                    {result.recognized ? "Recognized" : "Unknown"}
                  </td>
                  <td>{result.recognized ? "Attendance marked" : "Not marked"}</td>
                </tr>
              ))}
              {!results.length && (
                <tr>
                  <td colSpan={3} className="muted">
                    No detections yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default LiveMonitoring;
