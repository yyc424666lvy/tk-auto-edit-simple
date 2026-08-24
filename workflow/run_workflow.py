#!/usr/bin/env python3
"""TK Product Video: Codex plan -> Montaj cut -> portable FFmpeg output.

This is an orchestration layer. It intentionally does not implement shot
selection or a new editing engine. Codex supplies the plan JSON; Montaj
materialize-cut performs the exact multi-source cut/concat; portable FFmpeg
performs the final crop/scale, optional simple copy layer, and silent encode.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


GATES = {"CLEAN_SOURCE", "CROPPABLE_TEXT", "MASKABLE_TEXT", "SOURCE_TEXT_LIMITATION"}
VERSIONS = {"B_result_first": "B_TIMELINE", "C_product_logic": "C_TIMELINE"}


def run(cmd: list[str], env: dict[str, str], *, check: bool = True,
        cwd: Path | None = None) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, env=env, cwd=str(cwd) if cwd else None,
                            capture_output=True, text=True)
    if check and result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(cmd)}\n{result.stderr[-4000:]}")
    return result


def probe(path: Path, ffprobe: str, env: dict[str, str]) -> dict:
    cmd = [ffprobe, "-v", "error", "-show_entries",
           "format=duration:stream=index,codec_name,codec_type,width,height,avg_frame_rate,channels",
           "-of", "json", str(path)]
    data = json.loads(run(cmd, env).stdout)
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio_count = sum(1 for s in streams if s.get("codec_type") == "audio")
    return {
        "file": path.name,
        "path": str(path.resolve()),
        "duration": float(data.get("format", {}).get("duration", 0)),
        "width": video.get("width"),
        "height": video.get("height"),
        "fps": video.get("avg_frame_rate"),
        "codec": video.get("codec_name"),
        "audio_streams": audio_count,
        "size_bytes": path.stat().st_size,
        "mtime_ns": path.stat().st_mtime_ns,
    }


def analyze(inputs: list[Path], out_dir: Path, ffmpeg: str, ffprobe: str, env: dict[str, str]) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    frames_dir = out_dir / "analysis_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    sources = []
    for path in inputs:
        meta = probe(path, ffprobe, env)
        sheet = frames_dir / f"{path.stem}_1fps_contact.jpg"
        # One representative frame per second; enough for Codex planning and
        # deliberately avoids a full frame-by-frame analysis.
        run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(path),
             "-vf", "fps=1,scale=240:-2,tile=5x5:padding=2:margin=2",
             "-frames:v", "1", str(sheet)], env)
        meta["contact_sheet"] = str(sheet)
        sources.append(meta)
    cache = {"schema": "tk-product-video.analysis.v1", "sources": sources}
    (out_dir / "analysis_cache.json").write_text(json.dumps(cache, indent=2), encoding="utf-8")
    return cache


def cached_analysis(inputs: list[Path], out_dir: Path, ffmpeg: str, ffprobe: str, env: dict[str, str]) -> dict:
    cache_path = out_dir / "analysis_cache.json"
    if cache_path.is_file():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
            by_path = {s["path"]: s for s in cache.get("sources", [])}
            if all(str(p.resolve()) in by_path and
                   by_path[str(p.resolve())].get("size_bytes") == p.stat().st_size and
                   by_path[str(p.resolve())].get("mtime_ns") == p.stat().st_mtime_ns
                   for p in inputs):
                return cache
        except (OSError, ValueError, KeyError, TypeError):
            pass
    return analyze(inputs, out_dir, ffmpeg, ffprobe, env)


def resolve_sources(plan: dict, inputs: list[Path]) -> dict[str, Path]:
    available = {p.name: p.resolve() for p in inputs}
    names = {Path(name).name for version in plan.get("versions", {}).values()
             for segment in version.get("timeline", []) for name in [segment["src"]]}
    missing = sorted(name for name in names if name not in available)
    if missing:
        raise ValueError(f"plan references inputs not supplied: {', '.join(missing)}")
    return available


def validate_copy(copy: list[dict], total: float) -> None:
    if len(copy) > 4:
        raise ValueError("copy layer exceeds 1 Hook + 2 Feature + 1 Ending")
    for item in copy:
        text = str(item.get("text", "")).strip()
        if not text or len(text.split()) > 6:
            raise ValueError(f"copy must be non-empty and <=6 words: {text!r}")
        start, end = float(item["start"]), float(item["end"])
        if start < 0.0 or end <= start or end > total + 0.5:
            raise ValueError(f"copy timing outside timeline: {item}")
        if item.get("region", "bottom") not in {"top", "bottom"}:
            raise ValueError("copy region must be top or bottom")


def validate_version(version: dict, source_map: dict[str, Path]) -> float:
    timeline = version.get("timeline", [])
    if not 5 <= len(timeline) <= 8:
        raise ValueError("each version must contain 5–8 clips")
    total = 0.0
    for segment in timeline:
        name = Path(segment["src"]).name
        if name not in source_map:
            raise ValueError(f"unknown source: {name}")
        start, end = float(segment["in"]), float(segment["out"])
        duration = end - start
        if duration < 0.8 or duration > 3.0:
            raise ValueError(f"clip duration outside 0.8–3.0 seconds: {segment}")
        total += duration
    if not 10.0 <= total <= 15.0:
        raise ValueError(f"timeline duration {total:.3f}s is outside 10–15s")
    validate_copy(version.get("copy", []), total)
    return total


def ffmpeg_filter(version: dict) -> str:
    mode = version.get("crop_mode", "safe_crop")
    if mode == "safe_crop":
        # Fill 9:16 and center-crop; Codex must choose this only when the
        # source gate says the product remains inside the safe crop.
        chain = ["scale=1080:1920:force_original_aspect_ratio=increase",
                 "crop=1080:1920:(iw-1080)/2:(ih-1920)/2"]
    elif mode == "safe_scale":
        chain = ["scale=1080:1920:force_original_aspect_ratio=decrease",
                 "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black"]
    else:
        raise ValueError("crop_mode must be safe_crop or safe_scale")
    chain += ["setsar=1", "fps=30"]
    for item in version.get("copy", []):
        text = str(item["text"]).replace("\\", "\\\\").replace(":", "\\:").replace("'", "’")
        start, end = float(item["start"]), float(item["end"])
        region = item.get("region", "bottom")
        if region == "top":
            y_box, h_box, y_text = "0", "300", "105"
        else:
            y_box, h_box, y_text = "1500", "420", "1585"
        enable = f"between(t,{start:.3f},{end:.3f})"
        chain.append(f"drawbox=x=0:y={y_box}:w=iw:h={h_box}:color=0x061A2B:t=fill:enable='{enable}'")
        fontsize = int(item.get("fontsize", 64))
        chain.append(
            f"drawtext=fontfile={item['fontfile']}:text='{text}':fontcolor=white:"
            f"fontsize={fontsize}:borderw=3:bordercolor=black:x=(w-text_w)/2:y={y_text}:enable='{enable}'"
        )
    return ",".join(chain)


def render(inputs: list[Path], plan_path: Path, out_dir: Path, ffmpeg: str, ffprobe: str,
           montaj_root: Path, python_bin: str, env: dict[str, str], analysis: dict) -> dict:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    gate = plan.get("source_gate")
    if gate not in GATES:
        raise ValueError(f"source_gate must be one of {sorted(GATES)}")
    source_map = resolve_sources(plan, inputs)
    font = plan.get("fontfile", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    if not Path(font).is_file():
        raise ValueError(f"fontfile not found: {font}")
    for version in plan.get("versions", {}).values():
        version["copy"] = [dict(item, fontfile=font) for item in version.get("copy", [])]
        version["crop_mode"] = plan.get("crop_mode", version.get("crop_mode", "safe_crop"))
        validate_version(version, source_map)

    out_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    outputs = {}
    timelines = {}
    copies = {}
    for version_name, report_key in VERSIONS.items():
        version = plan["versions"][version_name]
        spec_path = out_dir / f"{version_name}_cut_spec.json"
        spec = {"segments": [{"src": str(source_map[Path(s["src"]).name]),
                              "in": float(s["in"]), "out": float(s["out"])}
                             for s in version["timeline"]]}
        spec_path.write_text(json.dumps(spec, indent=2), encoding="utf-8")
        concat_path = out_dir / f"{version_name}_concat.mp4"
        final_path = out_dir / ("B_result_first.mp4" if version_name.startswith("B_") else "C_product_logic.mp4")
        run([python_bin, "-m", "cli.main", "materialize-cut", str(spec_path), "--out", str(concat_path)],
            env, cwd=montaj_root)
        run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(concat_path),
             "-vf", ffmpeg_filter(version), "-map", "0:v:0", "-an", "-c:v", "libx264",
             "-pix_fmt", "yuv420p", "-r", "30", "-movflags", "+faststart", str(final_path)], env)
        outputs[version_name] = {"path": str(final_path), **probe(final_path, ffprobe, env)}
        timelines[report_key] = version["timeline"]
        copies[version_name] = version["copy"]

    report = {
        "schema": "tk-product-video.report.v1",
        "SOURCE_GATE": gate,
        "SOURCE_SUMMARY": analysis["sources"],
        "B_TIMELINE": timelines["B_TIMELINE"],
        "C_TIMELINE": timelines["C_TIMELINE"],
        "COPY": copies,
        "OUTPUT": outputs,
        "RUNTIME": {"seconds": round(time.monotonic() - started, 3), "target_seconds": 120},
        "LIMITATION": plan.get("limitation", ""),
        "ARCHITECTURE": {
            "planner": "Codex",
            "editor": "Montaj",
            "renderer": "portable FFmpeg 8.1.2",
            "external_llm_or_api": False,
            "node_or_puppeteer": False,
        },
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Reusable TK Product Video workflow")
    parser.add_argument("command", choices=["analyze", "render", "run"])
    parser.add_argument("--input", action="append", required=True, help="one or two local MP4 files")
    parser.add_argument("--plan", help="Codex-generated B/C plan JSON (required for render/run)")
    parser.add_argument("--out-dir", default="./tk-product-video-output")
    parser.add_argument("--montaj-root", default=os.environ.get("MONTAJ_ROOT", "."))
    parser.add_argument("--ffmpeg", default=os.environ.get("MONTAJ_FFMPEG", "ffmpeg"))
    parser.add_argument("--ffprobe", default=os.environ.get("MONTAJ_FFPROBE", "ffprobe"))
    args = parser.parse_args()
    if not 1 <= len(args.input) <= 2:
        parser.error("provide one or two --input files")
    if args.command in {"render", "run"} and not args.plan:
        parser.error("--plan is required for render/run")

    inputs = [Path(p).resolve() for p in args.input]
    if any(not p.is_file() for p in inputs):
        parser.error("all --input paths must exist")
    out_dir = Path(args.out_dir).resolve()
    env = os.environ.copy()
    env["MONTAJ_FFMPEG"] = str(Path(args.ffmpeg).resolve()) if Path(args.ffmpeg).is_file() else args.ffmpeg
    env["MONTAJ_FFPROBE"] = str(Path(args.ffprobe).resolve()) if Path(args.ffprobe).is_file() else args.ffprobe
    analysis = cached_analysis(inputs, out_dir, args.ffmpeg, args.ffprobe, env)
    if args.command == "analyze":
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
        return 0
    plan_path = Path(args.plan).resolve()
    report = render(inputs, plan_path, out_dir, args.ffmpeg, args.ffprobe,
                    Path(args.montaj_root).resolve(), sys.executable, env, analysis)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
