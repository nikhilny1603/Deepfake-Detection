"""
Text AI-detector — DistilBERT fine-tuned for binary classification
(human-written vs AI-generated). Falls back to pretrained weights when no
fine-tuned checkpoint is available.

Also exposes a lightweight `humanize_text` rewriter — a deterministic rule-based
paraphraser that softens AI-typical phrasing. For higher quality, swap in a
seq2seq model such as `humarin/chatgpt_paraphraser_on_T5_base`.
"""
from __future__ import annotations
from pathlib import Path
import re
from typing import Tuple, List

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
)


MODEL_NAME = "distilbert-base-uncased"


class TextDeepfakeModel:
    def __init__(self, weights_path: Path | None = None, device: str = "cpu"):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_NAME, num_labels=2
        )
        if weights_path and Path(weights_path).is_file():
            state = torch.load(weights_path, map_location=device)
            self.model.load_state_dict(state, strict=False)
        self.model.to(device).eval()

    @torch.no_grad()
    def predict(self, text: str) -> Tuple[float, float]:
        """Returns (p_ai, p_human)."""
        enc = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors="pt",
        ).to(self.device)
        logits = self.model(**enc).logits[0]
        probs = torch.softmax(logits, dim=-1).cpu().numpy()
        # Convention: index 1 = AI, index 0 = Human
        p_ai = float(probs[1])
        p_human = float(probs[0])
        return p_ai, p_human

    def highlight_ai_tokens(self, text: str, top_k_pct: float = 0.2) -> List[dict]:
        """
        Rough explainability: per-sentence AI probability. Returns a list of
        {sentence, p_ai, highlight} dicts so the frontend can colour them.
        """
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        out = []
        for s in sentences:
            if not s.strip():
                continue
            p_ai, _ = self.predict(s)
            out.append({"sentence": s, "p_ai": p_ai, "highlight": p_ai > 0.5})
        return out


# ------------------- Rule-based humaniser -------------------

_AI_PHRASES = [
    (r"\bIn conclusion,\s*", ""),
    (r"\bMoreover,\s*", "Also, "),
    (r"\bFurthermore,\s*", "Plus, "),
    (r"\bAdditionally,\s*", "Also, "),
    (r"\bIt is important to note that\s*", ""),
    (r"\bIt should be noted that\s*", ""),
    (r"\bdelve into\b", "look at"),
    (r"\butilize\b", "use"),
    (r"\bleverage\b", "use"),
    (r"\bfacilitate\b", "help"),
    (r"\bnumerous\b", "many"),
    (r"\bplethora of\b", "lots of"),
    (r"\bin order to\b", "to"),
    (r"\bdue to the fact that\b", "because"),
    (r"\bat this point in time\b", "now"),
    (r"\bsubsequently\b", "then"),
    (r"\bnevertheless\b", "still"),
]


def humanize_text(text: str) -> str:
    """Deterministic rewrite that strips classic AI tells and tightens prose."""
    out = text
    for pat, rep in _AI_PHRASES:
        out = re.sub(pat, rep, out, flags=re.IGNORECASE)
    # Break overly long sentences on " and " into two
    out = re.sub(r"(\b\w+\b[^.!?]{80,}?)\s+and\s+", r"\1. ", out)
    # Collapse double spaces
    out = re.sub(r"\s+", " ", out).strip()
    # Capitalise sentence starts
    out = re.sub(r"(^|[.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), out)
    return out
