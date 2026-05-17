"""
Train the video deepfake detector (CNN + LSTM) on Celeb-DF / DFDC.

Expected layout (each video pre-extracted to a folder of frames):
    data_dir/train/real/<video_id>/*.jpg
    data_dir/train/fake/<video_id>/*.jpg
    data_dir/val/...

Usage:
    python training/train_video.py --data_dir /path/to/dataset --epochs 8
"""
import argparse
import random
from pathlib import Path
from typing import List

import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
from sklearn.metrics import precision_recall_fscore_support, accuracy_score

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.models.video_model import VideoDeepfakeModel
from backend.utils.preprocessing import IMG_SIZE, IMAGENET_MEAN, IMAGENET_STD


SEQ_LEN = 16
TF = transforms.Compose(
    [
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ]
)


class VideoFolder(Dataset):
    def __init__(self, root: Path):
        self.samples: List[tuple[Path, int]] = []
        for cls, label in [("real", 0), ("fake", 1)]:
            for vid_dir in (root / cls).iterdir():
                if vid_dir.is_dir():
                    self.samples.append((vid_dir, label))
        random.shuffle(self.samples)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        vid_dir, label = self.samples[idx]
        frames = sorted(vid_dir.glob("*.jpg"))
        if len(frames) >= SEQ_LEN:
            step = len(frames) // SEQ_LEN
            picks = frames[::step][:SEQ_LEN]
        else:
            picks = frames + [frames[-1]] * (SEQ_LEN - len(frames))
        seq = torch.stack([TF(Image.open(p).convert("RGB")) for p in picks])
        return seq, label


def evaluate(model, loader, device):
    model.eval()
    preds, labels = [], []
    with torch.no_grad():
        for x, y in loader:
            out = model(x.to(device)).argmax(1).cpu().numpy()
            preds.extend(out.tolist())
            labels.extend(y.numpy().tolist())
    acc = accuracy_score(labels, preds)
    prec, rec, f1, _ = precision_recall_fscore_support(labels, preds, average="binary")
    return acc, prec, rec, f1


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir", required=True, type=Path)
    p.add_argument("--epochs", type=int, default=8)
    p.add_argument("--batch", type=int, default=4)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--out", type=Path, default=Path("models_store/video_model.pth"))
    args = p.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    train_loader = DataLoader(VideoFolder(args.data_dir / "train"), batch_size=args.batch, shuffle=True, num_workers=2)
    val_loader = DataLoader(VideoFolder(args.data_dir / "val"), batch_size=args.batch, num_workers=2)

    model = VideoDeepfakeModel(pretrained=True).to(device)
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
