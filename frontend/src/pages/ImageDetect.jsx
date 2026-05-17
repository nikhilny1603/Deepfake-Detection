import { useState } from "react";
import api, { fileUrl } from "../api/client";
import UploadZone from "../components/UploadZone";
import Loader from "../components/Loader";
import ResultCard from "../components/ResultCard";
import toast from "react-hot-toast";

export default function ImageDetect() {
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
      const r = await api.post("/api/detect/image", fd);
      setResult(r.data);
    } catch (e) {
      toast.error("Detection failed");
    } finally { setBusy(false); }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Image Detection</h1>
        <p className="text-white/60 mt-1">EfficientNet-B0 + Grad-CAM heatmap.</p>
      </div>
      <UploadZone accept={{ "image/*": [] }} file={file} onFile={onFile} />
      {preview && (
        <div className="glass p-4">
          <img src={preview} alt="preview" className="max-h-80 mx-auto rounded-lg" />
        </div>
      )}
      <button onClick={detect} disabled={!file || busy} className="btn-primary w-full disabled:opacity-50">
        {busy ? "Analysing…" : "Detect"}
      </button>
      {busy && <Loader />}
      {result && (
        <ResultCard result={result}>
          <div className="grid sm:grid-cols-2 gap-4">
            <Thumb label="Original" src={fileUrl(result.explanation.original_url)} />
            <Thumb label="Grad-CAM heatmap" src={fileUrl(result.explanation.heatmap_url)} />
          </div>
        </ResultCard>
      )}
    </div>
  );
}

function Thumb({ label, src }) {
  return (
    <div>
      <div className="text-xs uppercase tracking-wider text-white/40 mb-2">{label}</div>
      <img src={src} alt={label} className="rounded-lg border border-white/10 w-full" />
    </div>
  );
}
