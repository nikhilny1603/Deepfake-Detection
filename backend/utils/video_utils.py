"""Video frame extraction helpers."""
from pathlib import Path
from typing import List, Tuple
import cv2
import numpy as np


def extract_frames(video_path: str | Path, max_frames: int = 16) -> List[np.ndarray]:
    """Uniformly sample up to `max_frames` BGR frames from the video."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video {video_path}")

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    if total <= 0:
        # Fallback: read until exhaustion
        frames = []
        while True:
            ok, fr = cap.read()
            if not ok:
                break
            frames.append(fr)
        cap.release()
        idx = np.linspace(0, max(0, len(frames) - 1), num=min(max_frames, len(frames))).astype(int)
        return [frames[i] for i in idx]

    indices = np.linspace(0, total - 1, num=min(max_frames, total)).astype(int)
    frames: List[np.ndarray] = []
    for i in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(i))
        ok, fr = cap.read()
        if ok:
            frames.append(fr)
    cap.release()
    return frames


def save_frame_thumbnails(
    frames: List[np.ndarray], out_dir: Path, prefix: str, top_indices: List[int]
) -> List[str]:
    """Save the highlighted frames as JPEGs and return relative paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: List[str] = []
    for i in top_indices:
        if 0 <= i < len(frames):
            p = out_dir / f"{prefix}_frame_{i}.jpg"
            cv2.imwrite(str(p), frames[i])
            paths.append(str(p))
    return paths
