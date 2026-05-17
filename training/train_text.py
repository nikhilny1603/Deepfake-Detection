"""
Fine-tune DistilBERT to classify human vs AI-generated text.

Expected CSV layout: data_dir/train.csv and data_dir/val.csv with columns
    text,label   (label = 0 for human, 1 for AI)

Usage:
    python training/train_text.py --data_dir /path/to/dataset --epochs 3
"""
import argparse
from pathlib import Path
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import precision_recall_fscore_support, accuracy_score

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

MODEL_NAME = "distilbert-base-uncased"
MAX_LEN = 256


class TextDS(Dataset):
    def __init__(self, csv_path: Path, tokenizer):
        self.df = pd.read_csv(csv_path)
        self.tok = tokenizer

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        enc = self.tok(
            str(row["text"]),
            truncation=True,
            padding="max_length",
            max_length=MAX_LEN,
            return_tensors="pt",
        )
        return {
            "input_ids": enc["input_ids"][0],
            "attention_mask": enc["attention_mask"][0],
            "labels": torch.tensor(int(row["label"]), dtype=torch.long),
        }


def evaluate(model, loader, device):
    model.eval()
    preds, labels = [], []
    with torch.no_grad():
        for batch in loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            logits = model(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"]).logits
            preds.extend(logits.argmax(-1).cpu().numpy().tolist())
            labels.extend(batch["labels"].cpu().numpy().tolist())
    acc = accuracy_score(labels, preds)
    prec, rec, f1, _ = precision_recall_fscore_support(labels, preds, average="binary")
    return acc, prec, rec, f1


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data_dir", required=True, type=Path)
    p.add_argument("--epochs", type=int, default=3)
    p.add_argument("--batch", type=int, default=16)
    p.add_argument("--lr", type=float, default=2e-5)
    p.add_argument("--out", type=Path, default=Path("models_store/text_model.pth"))
    args = p.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2).to(device)

    train_loader = DataLoader(TextDS(args.data_dir / "train.csv", tok), batch_size=args.batch, shuffle=True)
    val_loader = DataLoader(TextDS(args.data_dir / "val.csv", tok), batch_size=args.batch)

    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    best_f1 = 0.0
    args.out.parent.mkdir(parents=True, exist_ok=True)

    for ep in range(1, args.epochs + 1):
        model.train()
        running = 0.0
        for batch in train_loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            opt.zero_grad()
            out = model(**batch)
            out.loss.backward()
            opt.step()
            running += out.loss.item() * batch["labels"].size(0)
        acc, prec, rec, f1 = evaluate(model, val_loader, device)
        print(f"Epoch {ep} | loss={running/len(train_loader.dataset):.4f} | "
              f"acc={acc:.3f} prec={prec:.3f} rec={rec:.3f} f1={f1:.3f}")
        if f1 > best_f1:
            best_f1 = f1
            torch.save(model.state_dict(), args.out)
            print(f"  -> saved {args.out}")


if __name__ == "__main__":
    main()
