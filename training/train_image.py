"""
Train the image deepfake detector (EfficientNet-B0) on FaceForensics++ / Celeb-DF.

Expected directory layout:
    data_dir/
        train/real/*.jpg
        train/fake/*.jpg
        val/real/*.jpg
        val/fake/*.jpg

Usage:
    python training/train_image.py --data_dir /path/to/dataset --epochs 10 --batch 32
"""
import argparse
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from sklearn.metrics import precision_recall_fscore_support, accuracy_score

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.models.image_model import ImageDeepfakeModel
from backend.utils.preprocessing import IMG_SIZE, IMAGENET_MEAN, IMAGENET_STD


def get_loaders(data_dir: Path, batch: int):
    train_tf = transforms.Compose(
        [
            transforms.Resize((IMG_SIZE, IMG_SIZE)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(0.2, 0.2, 0.2),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ]
    )
    val_tf = transforms.Compose(
        [
            transforms.Resize((IMG_SIZE, IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ]
    )
    train_ds = datasets.ImageFolder(data_dir / "train", transform=train_tf)
    val_ds = datasets.ImageFolder(data_dir / "val", transform=val_tf)
    return (
        DataLoader(train_ds, batch_size=batch, shuffle=True, num_workers=4),
        DataLoader(val_ds, batch_size=batch, shuffle=False, num_workers=4),
    )


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
    p.add_argument("--epochs", type=int, default=10)
    p.add_argument("--batch", type=int, default=32)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--out", type=Path, default=Path("models_store/image_model.pth"))
    args = p.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    train_loader, val_loader = get_loaders(args.data_dir, args.batch)
    model = ImageDeepfakeModel(pretrained=True).to(device)
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
        train_loss = running / len(train_loader.dataset)
        acc, prec, rec, f1 = evaluate(model, val_loader, device)
        print(
            f"Epoch {ep:02d} | loss={train_loss:.4f} | "
            f"acc={acc:.3f} prec={prec:.3f} rec={rec:.3f} f1={f1:.3f}"
        )
        if f1 > best_f1:
            best_f1 = f1
            torch.save(model.state_dict(), args.out)
            print(f"  -> saved {args.out} (f1={f1:.3f})")


if __name__ == "__main__":
    main()
