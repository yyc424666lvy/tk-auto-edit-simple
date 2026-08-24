#!/usr/bin/env python3
"""Create a 1-fps contact sheet with source filename + timestamp labels.

Packaging helper for planner handoff. This does not modify the frozen core
workflow and uses FFmpeg/ffprobe only.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path


def run(cmd: list[str]) -> str:
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr[-4000:])
    return p.stdout


def duration_seconds(path: Path, ffprobe: str) -> float:
    raw = run([
        ffprobe, "-v", "error", "-show_entries", "format=duration",
        "-of", "json", str(path)
    ])
    return float(json.loads(raw)["format"]["duration"])


def escape_drawtext(text: str) -> str:
    return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--ffmpeg", default="ffmpeg")
    ap.add_argument("--ffprobe", default="ffprobe")
    ap.add_argument("--out", required=True)
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--thumb-width", type=int, default=240)
    ap.add_argument("--fontfile", default=None)
    args = ap.parse_args()

    src = Path(args.input).resolve()
    if not src.is_file():
        ap.error("--input file not found")
    duration = duration_seconds(src, args.ffprobe)
    cells = max(1, int(math.floor(duration)) + 1)
    rows = math.ceil(cells / args.cols)

    name = escape_drawtext(src.name)
    font = f":fontfile='{escape_drawtext(args.fontfile)}'" if args.fontfile else ""
    # pts:hms is the source timestamp after fps=1. Draw the label on every frame
    # before tiling so each tile remains independently grounded.
    vf = (
        f"fps=1,scale={args.thumb_width}:-2,"
        "drawbox=x=0:y=h-34:w=iw:h=34:color=black@0.72:t=fill,"
        f"drawtext=text='{name} | %{{pts\\:hms}}':fontcolor=white:fontsize=18:"
        f"x=6:y=h-27{font},"
        f"tile={args.cols}x{rows}:padding=2:margin=2"
    )
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    run([
        args.ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(src), "-vf", vf, "-frames:v", "1", str(out)
    ])
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
