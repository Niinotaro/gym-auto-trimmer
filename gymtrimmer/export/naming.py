from __future__ import annotations
from pathlib import Path
from datetime import datetime
import re

def next_clip_path(out_dir: str, apparatus: str, date_str: str | None = None) -> str:
    """YYYYMMDD_{apparatus}_{seq:03d}.mp4 を返す。既存を走査して次の連番を採番。"""
    d = date_str or datetime.now().strftime("%Y%m%d")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    pat = re.compile(rf"^{re.escape(d)}_{re.escape(apparatus)}_(\d{{3}})\.mp4$")
    max_seq = 0
    for p in out.glob(f"{d}_{apparatus}_*.mp4"):
        m = pat.match(p.name)
        if m:
            max_seq = max(max_seq, int(m.group(1)))
    return str(out / f"{d}_{apparatus}_{max_seq+1:03d}.mp4")
