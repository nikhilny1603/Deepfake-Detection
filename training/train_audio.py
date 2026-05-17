"""
Train the audio deepfake detector on ASVspoof 2019 LA.

Expected layout:
    data_dir/train/real/*.wav
    data_dir/train/fake/*.wav
    data_dir/val/...

Usage:
    python training/train_audio.py --data_dir /path/to/dataset
"""
import argparse
from pathlib import Path
from typing import List

import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import precision_recall_fscore_support, accuracy_score

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.models.audio_model import AudioDeepfakeModel
from backend.utils.audio_utils import load_waveform, waveform_to_melspec


class AudioFolder(Dataset):
    def __init__(self, root: Path):
        self.samples: List[tuple[Path, int]] = []
        for cls, label in [("real", 0), ("fake", 1)]:
            for p in (root / cls).rglob("*.wav"):
                self.samples.append((p, label))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        y, _ = load_waveform(path)
        spec = waveform_to_melspec(y)[0]   # remove batch dim → [1, n_mels, T]
        return spec, label


def evaluate(model, loader, device):
    model.eval()
    preds, labels = [], []
    with torch.no_grad():
        for x, y in loader:
            preds.extend(model(x.to(device)).argmax(1).cpu().numpy().tolist())
            labels.extend(y.numpy().tolist())
    acc = accuracy_score(labels, preds)
    prec, rec, f1, _ = precision_recall_fscore_support(labels, preds, average="binary")
    return acc, prec, rec, f1


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir", required=True, type=Path)
    p.add_argument("--epochs", type=int, default=15)
    p.add_argument("--batch", type=int, default=32)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--out", type=Path, default=Path("models_store/audio_model.pth"))
    args = p.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    train_loader = DataLoader(AudioFolder(args.data_dir / "train"), batch_size=args.batch, shuffle=True, num_workers=2)
    val_loader = DataLoader(AudioFolder(args.data_dir / "val"), batch_size=args.batch, num_workers=2)

    model = AudioDeepfakeModel().to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    crit = torch.nn.CrossEntropyLoss()

    best_f1 = 0.0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    for ep in range(1, args.epochs + 1):
        model.train()
        running = 0.0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)
            opt.zero_grad()
            loss = crit(model(x), y)
            loss.backward()
            opt.step()
            running += loss.item() * x.size(0)
        acc, prec, rec, f1 = evaluate(model, val_loader, device)
        print(f"Epoch {ep:02d} | loss={running/len(train_loader.dataset):.4f} | "
              f"acc={acc:.3f} prec={prec:.3f} rec={rec:.3f} f1={f1:.3f}")
        if f1 > best_f1:
            best_f1 = f1
            torch.save(model.state_dict(), args.out)
            print(f"  -> saved {args.out}")


if __name__ == "__main__":
    main()
