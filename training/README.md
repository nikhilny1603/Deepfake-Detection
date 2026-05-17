# Training Scripts

Each script trains one model and saves the best checkpoint into `models_store/`,
which is read by the FastAPI backend at startup.

## Datasets

| Modality | Dataset | Layout |
| --- | --- | --- |
| Image | FaceForensics++, Celeb-DF | `train/{real,fake}/*.jpg`, `val/{real,fake}/*.jpg` |
| Video | Celeb-DF, DFDC (frames pre-extracted) | `train/{real,fake}/<vid_id>/*.jpg` |
| Audio | ASVspoof 2019 LA | `train/{real,fake}/*.wav` |
| Text  | HC3, M4 | `train.csv` / `val.csv` with `text,label` |

For video datasets, run a one-off frame extraction step using
`backend/utils/video_utils.extract_frames` or any standard tool (ffmpeg).

## Reproducing the Reported Metrics

```bash
python training/train_image.py --data_dir data/faceforensics --epochs 10 --batch 32
python training/train_video.py --data_dir data/celebdf      --epochs 8  --batch 4
python training/train_audio.py --data_dir data/asvspoof     --epochs 15 --batch 32
python training/train_text.py  --data_dir data/hc3          --epochs 3  --batch 16
```

A modern single GPU (e.g. RTX 3060 / T4) is sufficient. CPU training is supported
but slow.
