from __future__ import annotations
from typing import Iterator, Tuple, Dict

import cv2
import numpy as np

def parse_roi(s: str) -> Tuple[int, int, int, int]:
    """'x,y,w,h' を (x,y,w,h) に変換。簡易バリデーション含む。"""
    x, y, w, h = (int(p.strip()) for p in s.split(","))
    if w <= 0 or h <= 0:
        raise ValueError("ROI width/height must be positive")
    return (x, y, w, h)

def video_meta(path: str) -> Dict[str, float]:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise FileNotFoundError(f"cannot open video: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0.0
    cap.release()
    if fps <= 1e-6:
        fps = 30.0
    duration = float(frame_count / fps) if frame_count > 0 else 0.0
    return {"fps": float(fps), "frame_count": float(frame_count), "duration": float(duration)}

def iter_roi_frames(path: str, roi: Tuple[int, int, int, int]) -> Iterator[np.ndarray]:
    """動画からROI領域を切り出したフレームを順に返す。"""
    x, y, w, h = roi
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise FileNotFoundError(f"cannot open video: {path}")
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            crop = frame[y:y+h, x:x+w]
            yield crop
    finally:
        cap.release()
