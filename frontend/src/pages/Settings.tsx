import { useEffect, useState } from "react";
import {
  fetchRecognitionSettings,
  RecognitionSettings,
  updateRecognitionSettings,
} from "../api/settings";

const Settings = () => {
  const defaultRecognitionSettings: RecognitionSettings = {
    recognition_threshold: 0.4,
    live_recognition_stride: 2,
    live_recognition_width: 480,
  };
  const [apiBase, setApiBase] = useState(
    localStorage.getItem("attendance_api_base") || "http://localhost:8000/api"
  );
  const [message, setMessage] = useState<string | null>(null);
  const [recognition, setRecognition] = useState<RecognitionSettings | null>(null);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchRecognitionSettings();
        setRecognition(data);
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const save = () => {
    localStorage.setItem("attendance_api_base", apiBase);
    setMessage("API base URL saved. Refresh the page to apply.");
  };

  const saveRecognition = async () => {
    if (!recognition) return;
    setSaving(true);
    setMessage(null);
    try {
      await updateRecognitionSettings(recognition);
      setMessage("Recognition settings saved.");
    } finally {
      setSaving(false);
    }
  };

  const restoreDefaults = async () => {
    setSaving(true);
    setMessage(null);
    try {
      setRecognition(defaultRecognitionSettings);
      await updateRecognitionSettings(defaultRecognitionSettings);
      setMessage("Recognition settings restored to defaults.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="stack">
      <div className="card form">
        <h3>Settings</h3>
        <label>
          API Base URL
          <input value={apiBase} onChange={(e) => setApiBase(e.target.value)} />
        </label>
        {message && <div className="muted">{message}</div>}
        <button className="primary" onClick={save}>
          Save Settings
        </button>
      </div>

      <div className="card form">
        <h3>Recognition Settings</h3>
        {loading && <div className="muted">Loading recognition settings...</div>}
        {!loading && recognition && (
          <>
            <label>
              Recognition Threshold (0.0 - 1.0)
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={recognition.recognition_threshold}
                onChange={(e) =>
                  setRecognition({
                    ...recognition,
                    recognition_threshold: Number(e.target.value),
                  })
                }
              />
              <div className="muted">
                Higher = stricter matching, fewer false positives.
              </div>
            </label>
            <label>
              Live Recognition Stride (frames)
              <input
                type="number"
                min="1"
                max="10"
                value={recognition.live_recognition_stride}
                onChange={(e) =>
                  setRecognition({
                    ...recognition,
                    live_recognition_stride: Number(e.target.value),
                  })
                }
              />
              <div className="muted">
                Higher = faster preview, recognition runs less often.
              </div>
            </label>
            <label>
              Live Recognition Width (px)
              <input
                type="number"
                min="160"
                max="1280"
                value={recognition.live_recognition_width}
                onChange={(e) =>
                  setRecognition({
                    ...recognition,
                    live_recognition_width: Number(e.target.value),
                  })
                }
              />
              <div className="muted">
                Lower width speeds up recognition, may reduce accuracy.
              </div>
            </label>
            <button className="primary" onClick={saveRecognition} disabled={saving}>
              {saving ? "Saving..." : "Save Recognition Settings"}
            </button>
            <button className="ghost-button" onClick={restoreDefaults} disabled={saving}>
              Restore Defaults
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default Settings;
