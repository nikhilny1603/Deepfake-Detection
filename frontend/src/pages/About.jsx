export default function About() {
  return (
    <article className="prose prose-invert max-w-none space-y-6">
      <h1 className="text-3xl font-bold">How DeepGuard Works</h1>
      <p className="text-white/70">
        Deepfakes are synthetic media — images, videos, audio, or text — generated
        or manipulated by AI. DeepGuard runs four specialised neural networks that
        each look for the artefacts characteristic of generated content in their
        modality.
      </p>

      <div className="grid md:grid-cols-2 gap-4">
        <Card title="Image">
          A fine-tuned EfficientNet-B0 inspects pixel-level statistics. Grad-CAM
          produces a heatmap so you can see exactly which regions drove the model's
          decision — typically eyes, mouth blending boundaries, and skin texture
          inconsistencies.
        </Card>
        <Card title="Video">
          Frames are sampled uniformly with OpenCV, embedded by the same CNN
          backbone, and fed into a bidirectional LSTM that reasons over time. We
          highlight the frames that contributed most to the verdict.
        </Card>
        <Card title="Audio">
          The waveform is converted to a mel-spectrogram and analysed by a CNN. We
          slide the model over short windows to flag suspicious sections of the
          waveform — useful for spotting splices and TTS artefacts.
        </Card>
        <Card title="Text">
          DistilBERT is fine-tuned on human-vs-AI text corpora (HC3, M4). We score
          each sentence individually and offer a one-click rewriter that tones down
          AI-typical phrasing.
        </Card>
      </div>

      <h2 className="text-2xl font-bold mt-10">Honest Limitations</h2>
      <ul className="list-disc pl-6 text-white/70 space-y-1">
        <li>No detector is 100% accurate. Adversarial deepfakes can fool any model.</li>
        <li>Generalisation to unseen generators (new GANs, diffusion models) requires retraining.</li>
        <li>Treat results as <em>assistive evidence</em>, never as legal proof.</li>
      </ul>
    </article>
  );
}

function Card({ title, children }) {
  return (
    <div className="glass p-5">
      <h3 className="font-semibold text-lg text-indigo-300">{title}</h3>
      <p className="text-white/70 text-sm mt-2 leading-relaxed">{children}</p>
    </div>
  );
}
