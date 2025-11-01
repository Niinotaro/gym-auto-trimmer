from __future__ import annotations
import sys
from pathlib import Path
from typing import Optional, Tuple

import typer
from rich.console import Console
from rich.table import Table
import yaml

from gymtrimmer.io.video_reader import parse_roi, video_meta
from gymtrimmer.logic.motion_detect import compute_motion_scores, scores_to_segments
from gymtrimmer.logic.merge_rules import postprocess_segments
from gymtrimmer.export.naming import next_clip_path
from gymtrimmer.io.ffmpeg_writer import check_ffmpeg, cut_cfr

app = typer.Typer(help="Gym Auto Trimmer (Non-AI PoC)")
console = Console()

def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

@app.command()
def main(
    input: Path = typer.Option(..., "--input", "-i", help="Input video path"),
    roi: str = typer.Option(..., "--roi", help="ROI 'x,y,w,h'"),
    config: Path = typer.Option(Path("configs/default_hbar.yaml"), "--config"),
    out_dir: Path = typer.Option(Path("runs/out"), "--out-dir"),
    dry_run: bool = typer.Option(True, "--dry-run/--no-dry-run"),
    write_clips: bool = typer.Option(False, "--write-clips"),
) -> None:
    """CLI：スコア→区間抽出→結合→余白。dry-run時は表形式で表示のみ。"""
    cfg = load_config(config)
    r = parse_roi(roi)
    meta = video_meta(str(input))
    fps = meta["fps"]
    duration = meta["duration"]

    motion_cfg = cfg.get("motion", {})
    diff_thr = int(motion_cfg.get("diff_threshold", 20))
    score_thr = float(motion_cfg.get("score_threshold", 18.0))
    smooth_win = int(motion_cfg.get("smooth_window", 5))
    min_active = float(motion_cfg.get("min_active_sec", 0.6))

    gap = float(cfg.get("gap_merge_sec", 0.8))
    pad_pre = float(cfg.get("pad_pre_sec", 0.1))
    pad_post = float(cfg.get("pad_post_sec", 0.1))
    cfr_fps = int(cfg.get("cfr_fps", 30))

    console.rule("[bold]Compute motion scores")
    scores, fps_used = compute_motion_scores(str(input), r, diff_thr=diff_thr, smooth_win=smooth_win)
    segs = scores_to_segments(scores, fps_used, score_thr)
    segs = postprocess_segments(segs, duration, gap, min_active, pad_pre, pad_post)

    table = Table(title="Detected Segments (after postprocess)")
    table.add_column("#", justify="right")
    table.add_column("start [s]", justify="right")
    table.add_column("end [s]", justify="right")
    table.add_column("len [s]", justify="right")
    total = 0.0
    for i, (s, e) in enumerate(segs, 1):
        table.add_row(str(i), f"{s:.3f}", f"{e:.3f}", f"{(e-s):.3f}")
        total += (e - s)
    console.print(table)
    console.print(f"[green]segments={len(segs)} total={total:.3f}s duration={duration:.3f}s fps={fps_used:.3f}")

    if dry_run:
        console.print("[yellow]dry-run: no files will be written")
        return

    if write_clips:
        if not check_ffmpeg():
            console.print("[red]ffmpeg not found. install ffmpeg to enable clip writing.")
            raise SystemExit(1)
        out_dir.mkdir(parents=True, exist_ok=True)
        for (s, e) in segs:
            out_path = Path(next_clip_path(str(out_dir), cfg.get("apparatus", "hbar")))
            cut_cfr(str(input), s, e, str(out_path), fps=cfr_fps)
            console.print(f"[cyan]wrote: {out_path}")

if __name__ == "__main__":
    app()
