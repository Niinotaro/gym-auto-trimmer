from __future__ import annotations
from typing import List, Tuple

Segment = tuple[float, float]

def merge_close_segments(segs: List[Segment], gap_sec: float) -> List[Segment]:
    if not segs:
        return []
    segs = sorted(segs, key=lambda x: x[0])
    out: List[Segment] = []
    cs, ce = segs[0]
    for s, e in segs[1:]:
        if s - ce <= gap_sec:
            ce = max(ce, e)
        else:
            out.append((cs, ce))
            cs, ce = s, e
    out.append((cs, ce))
    return out

def suppress_too_short(segs: List[Segment], min_len_sec: float) -> List[Segment]:
    if not segs:
        return []
    out: List[Segment] = []
    for s, e in segs:
        if (e - s) >= min_len_sec:
            out.append((s, e))
        else:
            # 近傍と統合試行（前と近ければ延長）
            if out and (s - out[-1][1]) <= min_len_sec:
                ps, pe = out.pop()
                out.append((ps, max(pe, e)))
            # それでも短ければ破棄
    return out

def apply_padding_and_clip(segs: List[Segment], pad_pre: float, pad_post: float, duration: float) -> List[Segment]:
    out: List[Segment] = []
    for s, e in segs:
        ns = max(0.0, s - pad_pre)
        ne = min(duration, e + pad_post)
        if ne > ns:
            out.append((ns, ne))
    return out

def postprocess_segments(segs: List[Segment], duration: float, gap: float, min_len: float, pad_pre: float, pad_post: float) -> List[Segment]:
    segs = merge_close_segments(segs, gap)
    segs = suppress_too_short(segs, min_len)
    segs = apply_padding_and_clip(segs, pad_pre, pad_post, duration)
    return segs
