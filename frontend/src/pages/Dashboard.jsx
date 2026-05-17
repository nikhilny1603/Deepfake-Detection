import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
  const { user, loading } = useAuth();
  const [items, setItems] = useState([]);
  const [busy, setBusy] = useState(true);

  useEffect(() => {
    if (!user) { setBusy(false); return; }
    api.get("/api/history")
      .then((r) => setItems(r.data.items || []))
      .finally(() => setBusy(false));
  }, [user]);

  if (loading) return <p className="text-white/60">Loading…</p>;
  if (!user) {
    return (
      <div className="glass p-6 text-center">
        <p>You need an account to see your detection history.</p>
        <Link to="/login" className="btn-primary inline-flex mt-4">Sign in</Link>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Welcome, {user.name}</h1>
      <h2 className="text-lg font-semibold mb-3">Recent detections</h2>
      {busy && <p className="text-white/60">Loading history…</p>}
      {!busy && items.length === 0 && <p className="text-white/60">No detections yet.</p>}
      <ul className="space-y-3">
        {items.map((it) => (
          <li key={it._id} className="glass p-4 flex items-center justify-between">
            <div>
              <div className="text-xs uppercase tracking-wider text-white/40">{it.modality}</div>
              <div className={it.prediction === "fake" ? "text-red-300 font-semibold" : "text-emerald-300 font-semibold"}>
                {it.prediction.toUpperCase()} · {(it.confidence * 100).toFixed(1)}%
              </div>
            </div>
            <div className="text-xs text-white/40">{new Date(it.created_at).toLocaleString()}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}
