import { motion } from "framer-motion";
import { CheckCircle2, AlertTriangle } from "lucide-react";
import MetricsPanel from "./MetricsPanel";

export default function ResultCard({ result, children }) {
  if (!result) return null;
  const isFake = result.prediction === "fake";
  const pct = (result.confidence * 100).toFixed(1);
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass p-6 mt-6 space-y-6"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {isFake
            ? <AlertTriangle className="text-red-400" />
            : <CheckCircle2 className="text-emerald-400" />}
          <div>
            <div className="text-xs uppercase tracking-wider text-white/40">Prediction</div>
            <div className={`text-2xl font-bold ${isFake ? "text-red-300" : "text-emerald-300"}`}>
              {isFake ? "Likely Fake" : "Likely Real"}
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs uppercase tracking-wider text-white/40">Confidence</div>
          <div className="text-2xl font-semibold">{pct}%</div>
        </div>
      </div>

      <div className="h-2 rounded bg-white/10 overflow-hidden">
        <div
          className={`h-full ${isFake ? "bg-red-400" : "bg-emerald-400"}`}
          style={{ width: `${pct}%` }}
        />
      </div>

      {children}

      <div>
        <div className="text-xs uppercase tracking-wider text-white/40 mb-2">Model performance on test set</div>
        <MetricsPanel metrics={result.metrics} />
      </div>
    </motion.div>
  );
}
