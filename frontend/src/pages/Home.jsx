import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Image, Video, Music, FileText, ShieldCheck } from "lucide-react";

const tiles = [
  { to: "/detect/image", icon: Image, label: "Image", desc: "EfficientNet + Grad-CAM heatmap" },
  { to: "/detect/video", icon: Video, label: "Video", desc: "CNN + LSTM frame aggregation" },
  { to: "/detect/audio", icon: Music, label: "Audio", desc: "Mel-spectrogram CNN" },
  { to: "/detect/text",  icon: FileText, label: "Text",  desc: "BERT + AI humaniser" },
];

export default function Home() {
  return (
    <div className="space-y-12">
      <section className="text-center pt-10">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 text-sm text-white/60 border border-white/10 rounded-full px-3 py-1"
        >
          <ShieldCheck size={14} className="text-indigo-300" />
          Multimodal deepfake detection · explainable AI
        </motion.div>
        <h1 className="mt-6 text-4xl sm:text-6xl font-bold tracking-tight">
          See through the noise.
        </h1>
        <p className="mt-4 max-w-xl mx-auto text-white/60">
          Upload an image, video, audio clip, or block of text — DeepGuard tells you
          whether it's real, how confident it is, and shows you why.
        </p>
        <div className="mt-8 flex justify-center gap-3">
          <Link to="/detect/image" className="btn-primary">Get started</Link>
          <Link to="/about" className="btn-ghost">How it works</Link>
        </div>
      </section>

      <section className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {tiles.map((t, i) => (
          <motion.div
            key={t.to}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <Link to={t.to} className="glass p-5 block hover:bg-white/10 transition group">
              <t.icon className="text-indigo-300 group-hover:text-indigo-200 mb-3" />
              <div className="text-lg font-semibold">{t.label}</div>
              <div className="text-sm text-white/60 mt-1">{t.desc}</div>
            </Link>
          </motion.div>
        ))}
      </section>
    </div>
  );
}
