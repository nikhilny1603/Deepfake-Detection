# Saved Models

This folder holds trained model checkpoints used at inference time:

```
image_model.pth
video_model.pth
audio_model.pth
text_model.pth
```

If a checkpoint is missing, the backend falls back to pretrained ImageNet /
HuggingFace weights with a freshly initialised classification head, so the API
still works end-to-end for development and testing.

Run the corresponding script in `training/` to populate this directory.
