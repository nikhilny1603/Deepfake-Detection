import { useState } from "react";
import api, { fileUrl } from "../api/client";
import UploadZone from "../components/UploadZone";
import Loader from "../components/Loader";
import ResultCard from "../components/ResultCard";
import toast from "react-hot-toast";

export default function AudioDetect() {
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
      const r = await api.post("/api/detect/audio", fd);
      setResult(r.data);
    } catch {
      toast.error("Detection failed");
    } finally { setBusy(false); }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Audio Detection</h1>
        <p className="text-white/60 mt-1">Mel-spectrogram CNN with waveform region highlighting.</p>
      </div>
      <UploadZone accept={{ "audio/*": [] }} file={file} onFile={onFile} />
      {preview && (
        <div className="glass p-4">
          <audio controls src={preview} className="w-full" />
        </div>
      )}
      <button onClick={detect} disabled={!file || busy} className="btn-primary w-full disabled:opacity-50">
        {busy ? "Analysing audio…" : "Detect"}
      </button>
      {busy && <Loader />}
      {result && (
        <ResultCard result={result}>
          <div>
            <div className="text-xs uppercase tracking-wider text-white/40 mb-2">Waveform (suspicious regions in red)</div>
            <img src={fileUrl(result.explanation.waveform_url)} alt="waveform" className="rounded-lg border border-white/10 w-full bg-white" />
          </div>
        </ResultCard>
      )}
    </div>
  );
}
