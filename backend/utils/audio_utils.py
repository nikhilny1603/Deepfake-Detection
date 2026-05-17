"""Audio preprocessing: waveform → mel-spectrogram tensor."""
from pathlib import Path
from typing import Tuple
import numpy as np
import librosa
import torch

SAMPLE_RATE = 16000
N_MELS = 128
N_FFT = 1024
HOP_LENGTH = 256
DURATION_SEC = 4.0  # crop / pad to fixed length


def load_waveform(path: str | Path) -> Tuple[np.ndarray, int]:
    y, sr = librosa.load(str(path), sr=SAMPLE_RATE, mono=True)
    target_len = int(SAMPLE_RATE * DURATION_SEC)
    if len(y) < target_len:
        y = np.pad(y, (0, target_len - len(y)))
    else:
        y = y[:target_len]
    return y, sr


def waveform_to_melspec(y: np.ndarray) -> torch.Tensor:
    mel = librosa.feature.melspectrogram(
        y=y, sr=SAMPLE_RATE, n_fft=N_FFT, hop_length=HOP_LENGTH, n_mels=N_MELS
    )
    mel_db = librosa.power_to_db(mel, ref=np.max)
    # Normalise to [0, 1]
    mel_db = (mel_db - mel_db.min()) / (mel_db.max() - mel_db.min() + 1e-9)
    # Add channel dim: [1, n_mels, time]
    return torch.from_numpy(mel_db).float().unsqueeze(0).unsqueeze(0)
