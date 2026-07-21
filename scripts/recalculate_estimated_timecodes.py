#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
LATIN_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)*")
NUMBER_RE = re.compile(r"\d+(?:[.,:]\d+)*")


def weighted_units(text: str) -> float:
    han = len(HAN_RE.findall(text))
    latin = len(LATIN_RE.findall(text))
    numbers = len(NUMBER_RE.findall(text))
    commas = sum(text.count(x) for x in "，、,")
    medium_pauses = sum(text.count(x) for x in "；;：:")
    sentence_stops = sum(text.count(x) for x in "。！？?!")
    newlines = text.count("\n")
    ellipses = text.count("……") + text.count("...")

    # Approximate English words and number strings as slower spoken chunks.
    units = (
        han
        + latin * 2.2
        + numbers * 2.0
        + commas * 0.45
        + medium_pauses * 0.75
        + sentence_stops * 1.15
        + newlines * 0.55
        + ellipses * 0.8
    )
    return max(units, 1.0)


def round_half(value: float) -> float:
    return max(0.5, round(value * 2) / 2)


def compact_time(seconds: float) -> str:
    total = max(0, int(round(seconds)))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    return f"{hours:02d}{minutes:02d}{secs:02d}"


def format_time(seconds: float) -> str:
    milliseconds = int(round(seconds * 1000))
    hours, rem = divmod(milliseconds, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, millis = divmod(rem, 1000)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    return f"{minutes:02d}:{secs:02d}.{millis:03d}"


def load(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"File not found: {path}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}")
    if not isinstance(data, dict) or not isinstance(data.get("segments"), list):
        raise ValueError("visual plan must contain a segments array")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Recalculate estimated timecodes from each segment's spoken_text.")
    parser.add_argument("plan", type=Path)
    parser.add_argument("--out", type=Path, help="Write to a new path; default updates the input file")
    parser.add_argument("--pace", type=float, help="Weighted speaking units per second")
    parser.add_argument("--target-duration", type=float, help="Scale all segments to this total duration in seconds")
    parser.add_argument("--error-band", type=float, default=0.12, help="Project duration range, default ±12%%")
    args = parser.parse_args()

    try:
        data = load(args.plan)
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        return 1

    analysis = data.setdefault("script_analysis", {})
    pace_info = analysis.setdefault("speech_pace", {})
    pace = args.pace or pace_info.get("units_per_second") or 4.1
    if not isinstance(pace, (int, float)) or pace <= 0:
        print("[ERROR] pace must be a positive number")
        return 1

    durations: list[float] = []
    for index, seg in enumerate(data["segments"], start=1):
        text = seg.get("spoken_text")
        if not isinstance(text, str) or not text.strip():
            print(f"[ERROR] segment {index} has no spoken_text")
            return 1
        durations.append(round_half(weighted_units(text) / float(pace)))

    raw_total = sum(durations)
    if args.target_duration is not None:
        if args.target_duration <= 0:
            print("[ERROR] target duration must be positive")
            return 1
        scale = args.target_duration / raw_total
        durations = [round_half(x * scale) for x in durations]
        # Correct rounding drift on the final segment.
        drift = args.target_duration - sum(durations)
        durations[-1] = max(0.5, durations[-1] + drift)

    cursor = 0.0
    for seg, duration in zip(data["segments"], durations):
        seg["start"] = format_time(cursor)
        cursor += duration
        seg["end"] = format_time(cursor)
        seg["timecode_confidence"] = "estimated"
        seg["estimated_spoken_seconds"] = round(duration, 3)
        filename = seg.get("filename")
        if isinstance(filename, str) and filename:
            parts = filename.split("_", 2)
            if len(parts) == 3:
                seg["filename"] = f"{parts[0]}_{compact_time(cursor - duration)}-{compact_time(cursor)}_{parts[2]}"

    project = data.setdefault("project", {})
    project["source_type"] = "script"
    project["timecode_mode"] = "estimated"
    project["duration_seconds"] = round(cursor, 3)
    band = max(0.0, min(float(args.error_band), 0.5))
    project["duration_range_seconds"] = [
        round(cursor * (1 - band), 1),
        round(cursor * (1 + band), 1),
    ]

    pace_info["units_per_second"] = float(pace)
    pace_info["calculation"] = "weighted Chinese speaking units; all timecodes are estimates"
    if args.target_duration is not None:
        pace_info["scaled_to_target_duration"] = float(args.target_duration)

    output = args.out or args.plan
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Recalculated {len(durations)} segments; estimated total {cursor:.1f}s -> {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
