from __future__ import annotations
from typing import List, Tuple

import cv2
import numpy as np

from gymtrimmer.io.video_reader import iter_roi_frames

def _moving_average(x: np.ndarray, win: int) -> np.ndarray:
    if win <= 1:
        return x
    pad = win // 2
    xpad = np.pad(x, (pad, pad), mode="edge")
    ker = np.ones(win, dtype=np.float32) / float(win)
    return np.convolve(xpad, ker, mode="valid")

def compute_motion_scores(path: str, roi: tuple[int,int,int,int], diff_thr: int = 20, smooth_win: int = 5) -> tuple[list[float], float]:
    """ROI内のフレーム差分→二値化→非ゼロ率[%]をスコア化。"""
    # fps取得（VideoCaptureから再取得）
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise FileNotFoundError(f"cannot open video: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    cap.release()

    prev = None
    scores: List[float] = []
    for frame in iter_roi_frames(path, roi):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev is None:
            prev = gray
            continue
        diff = cv2.absdiff(gray, prev)
        _, bin_ = cv2.threshold(diff, diff_thr, 255, cv2.THRESH_BINARY)
        score = float(np.count_nonzero(bin_)) / float(bin_.size) * 100.0
        scores.append(score)
        prev = gray

    if not scores:
        return ([], float(fps))

    smoothed = _moving_average(np.asarray(scores, dtype=np.float32), max(1, int(smooth_win)))
    return (smoothed.astype(float).tolist(), float(fps))

def scores_to_segments(scores: list[float], fps: float, score_thr: float) -> list[tuple[float, float]]:
    """スコア列をしきい値で2値化し、連続区間を秒単位で返す。"""
    segs: list[tuple[float, float]] = []
    if not scores or fps <= 1e-6:
        return segs
    active = np.asarray(scores, dtype=np.float32) > float(score_thr)
    n = active.shape[0]
    in_run = False
    start_idx = 0
    for i in range(n):
        if active[i] and not in_run:
            in_run = True
            start_idx = i
        if (not active[i] and in_run) or (in_run and i == n - 1):
            end_idx = i if not active[i] else i + 1
            s = max(0.0, start_idx / fps)
            e = max(s, end_idx / fps)
            if e > s:
                segs.append((s, e))
            in_run = False
    return segs
