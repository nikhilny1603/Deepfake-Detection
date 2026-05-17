import { useState } from "react";
import api, { fileUrl } from "../api/client";
import UploadZone from "../components/UploadZone";
import Loader from "../components/Loader";
import ResultCard from "../components/ResultCard";
import toast from "react-hot-toast";

export default function VideoDetect() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);

  const onFile = (f) => {
    setFile(f);
    setResult(null);
    setPreview(URL.createObjectURL(f));
  };

  const detect = async () => {
    if (!file) return;
    setBusy(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const r = await api.post("/api/detect/video", fd);
      setResult(r.data);
    } catch {
      toast.error("Detection failed");
    } finally { setBusy(false); }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Video Detection</h1>
        <p className="text-white/60 mt-1">CNN per frame + LSTM aggregation. Up to 16 frames are sampled.</p>
      </div>
      <UploadZone accept={{ "video/*": [] }} file={file} onFile={onFile} />
      {preview && (
        <div className="glass p-4">
          <video controls src={preview} className="max-h-80 mx-auto rounded-lg" />
        </div>
      )}
      <button onClick={detect} disabled={!file || busy} className="btn-primary w-full disabled:opacity-50">
        {busy ? "Analysing video…" : "Detect"}
      </button>
      {busy && <Loader label="Extracting frames & running model…" />}
      {result && (
        <ResultCard result={result}>
          <div>
            <div className="text-xs uppercase tracking-wider text-white/40 mb-2">Most influential frames</div>
            <div className="grid grid-cols-3 gap-3">
              {result.explanation.key_frame_urls.map((u) => (
                <img key={u} src={fileUrl(u)} alt="frame" className="rounded-lg border border-white/10" />
              ))}
            </div>
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-white/40 mb-2">Per-frame fake probability</div>
            <div className="flex items-end gap-1 h-20">
              {result.explanation.frame_scores.map((s, i) => (
                <div key={i} className="flex-1 bg-indigo-400/70 rounded-t" style={{ height: `${s * 100}%` }} title={`${(s * 100).toFixed(1)}%`} />
              ))}
            </div>
          </div>
        </ResultCard>
      )}
    </div>
  );
}
