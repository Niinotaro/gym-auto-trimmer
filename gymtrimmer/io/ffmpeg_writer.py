from __future__ import annotations
import shutil
import subprocess

def check_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None

def cut_cfr(input_path: str, start_sec: float, end_sec: float, output_path: str, fps: int = 30) -> None:
    """精度優先で -i の後に -ss/-to を置く。CFR(30fps)で書き出し。"""
    if end_sec <= start_sec:
        return
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-ss", f"{start_sec:.3f}",
        "-to", f"{end_sec:.3f}",
        "-r", str(fps),
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-an",
        output_path,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
