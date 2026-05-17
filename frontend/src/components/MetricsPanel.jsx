export default function MetricsPanel({ metrics }) {
  if (!metrics) return null;
  const items = [
    { label: "Accuracy", value: metrics.accuracy },
    { label: "Precision", value: metrics.precision },
    { label: "Recall", value: metrics.recall },
    { label: "F1", value: metrics.f1 },
  ];
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {items.map((m) => (
        <div key={m.label} className="glass p-4 text-center">
          <div className="text-xs uppercase tracking-wider text-white/50">{m.label}</div>
          <div className="text-2xl font-semibold mt-1 text-white">
            {(m.value * 100).toFixed(1)}%
          </div>
        </div>
      ))}
    </div>
  );
}
