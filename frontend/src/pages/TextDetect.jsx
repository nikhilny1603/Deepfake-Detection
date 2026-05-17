import { useState } from "react";
import api from "../api/client";
import Loader from "../components/Loader";
import ResultCard from "../components/ResultCard";
import toast from "react-hot-toast";
import { Wand2 } from "lucide-react";

export default function TextDetect() {
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [rewrite, setRewrite] = useState(null);

  const detect = async () => {
    if (!text.trim()) return;
    setBusy(true); setRewrite(null);
    try {
      const r = await api.post("/api/detect/text", { text });
      setResult(r.data);
    } catch { toast.error("Detection failed"); }
    finally { setBusy(false); }
  };

  const humanize = async () => {
    setBusy(true);
    try {
      const r = await api.post("/api/text/humanize", { text });
      setRewrite(r.data);
    } catch { toast.error("Rewrite failed"); }
    finally { setBusy(false); }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Text AI Detection & Humaniser</h1>
        <p className="text-white/60 mt-1">DistilBERT classifier + rule-based rewriter.</p>
      </div>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={8}
        placeholder="Paste any text to analyse — articles, essays, posts…"
        className="w-full glass p-4 outline-none focus:ring-2 ring-indigo-400 resize-y"
      />
      <div className="flex gap-3">
        <button onClick={detect} disabled={!text.trim() || busy} className="btn-primary disabled:opacity-50">
          {busy ? "…" : "Detect"}
        </button>
        <button onClick={humanize} disabled={!text.trim() || busy} className="btn-ghost disabled:opacity-50">
          <Wand2 size={16} /> Humanize
        </button>
      </div>
      {busy && <Loader />}

      {result && (
        <ResultCard result={result}>
          <div className="grid grid-cols-2 gap-3">
            <Stat label="AI-generated" value={`${result.explanation.ai_percent}%`} color="text-red-300" />
            <Stat label="Human-like" value={`${result.explanation.human_percent}%`} color="text-emerald-300" />
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-white/40 mb-2">Per-sentence highlighting</div>
            <div className="space-y-1 leading-relaxed">
              {result.explanation.sentences.map((s, i) => (
                <span
                  key={i}
                  className={`px-1 rounded ${s.highlight ? "bg-red-500/20 text-red-200" : "text-white/80"}`}
                  title={`AI prob: ${(s.p_ai * 100).toFixed(1)}%`}
                >
                  {s.sentence}{" "}
                </span>
              ))}
            </div>
          </div>
        </ResultCard>
      )}

      {rewrite && (
        <div className="glass p-6 space-y-3">
          <div className="text-xs uppercase tracking-wider text-white/40">Humanised version</div>
          <p className="leading-relaxed">{rewrite.rewritten}</p>
          <div className="text-sm text-white/60">
            AI score: {rewrite.ai_percent_before}% → <span className="text-emerald-300">{rewrite.ai_percent_after}%</span>
          </div>
        </div>
      )}
    </div>
  );
}

function Stat({ label, value, color }) {
  return (
    <div className="glass p-4 text-center">
      <div className="text-xs uppercase tracking-wider text-white/40">{label}</div>
      <div className={`text-2xl font-semibold mt-1 ${color}`}>{value}</div>
    </div>
  );
}
