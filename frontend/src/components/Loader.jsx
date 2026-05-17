import { motion } from "framer-motion";

export default function Loader({ label = "Analysing…" }) {
  return (
    <div className="flex items-center justify-center gap-3 py-8">
      <motion.div
        className="w-3 h-3 rounded-full bg-indigo-400"
        animate={{ y: [0, -8, 0] }}
        transition={{ repeat: Infinity, duration: 0.6 }}
      />
      <motion.div
        className="w-3 h-3 rounded-full bg-cyan-400"
        animate={{ y: [0, -8, 0] }}
        transition={{ repeat: Infinity, duration: 0.6, delay: 0.15 }}
      />
      <motion.div
        className="w-3 h-3 rounded-full bg-fuchsia-400"
        animate={{ y: [0, -8, 0] }}
        transition={{ repeat: Infinity, duration: 0.6, delay: 0.3 }}
      />
      <span className="ml-3 text-white/70">{label}</span>
    </div>
  );
}
