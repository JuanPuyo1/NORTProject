#!/usr/bin/env python3
"""Size-capped OpenNeuro ds003626 derivative downloader.

Raw BDFs are ~0.7GB/session (~20GB full set). Within a 5GB budget we
download preprocessed EEG+events derivatives, which are what Phase 0
classification needs.

Uses the same OpenNeuro source as Raw_data_download_tutorial.py /
download_helper.get_* (ds003626), via public S3 when git-annex is unavailable.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def list_derivative_objects():
    out = subprocess.check_output(
        [
            "aws",
            "s3",
            "ls",
            "--no-sign-request",
            "s3://openneuro.org/ds003626/derivatives/",
            "--recursive",
        ],
        text=True,
    )
    rows = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 4:
            continue
        size = int(parts[2])
        key = parts[3]  # ds003626/derivatives/sub-XX/...
        if not (key.endswith("_eeg-epo.fif") or key.endswith("_events.dat")):
            continue
        # Strip leading ds003626/ because bucket prefix already includes dataset id
        # Actual key on S3 is: ds003626/derivatives/sub-...
        rows.append((size, key))
    return rows


def subject_of(key: str) -> str:
    for part in key.split("/"):
        if part.startswith("sub-"):
            return part
    raise ValueError(key)


def local_bytes(root: Path) -> int:
    total = 0
    if not root.exists():
        return 0
    for p in root.rglob("*"):
        if p.is_file():
            total += p.stat().st_size
    return total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", default="projects/ds003626")
    parser.add_argument("--max-gb", type=float, default=5.0)
    parser.add_argument(
        "--subjects",
        default="all",
        help='Comma subjects like "02,03" or "all"',
    )
    args = parser.parse_args()

    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)
    max_bytes = int(args.max_gb * (1024**3))
    current = local_bytes(dest)
    print(
        f"[download] existing={current/(1024**3):.3f} GiB  budget={args.max_gb:.2f} GiB"
    )

    rows = list_derivative_objects()
    by_sub = {}
    for size, key in rows:
        by_sub.setdefault(subject_of(key), []).append((size, key))

    if args.subjects == "all":
        wanted = sorted(by_sub.keys())
    else:
        wanted = [f"sub-{int(s):02d}" if not s.startswith("sub-") else s for s in args.subjects.split(",")]

    selected = []
    planned = current
    for sub in wanted:
        files = by_sub.get(sub, [])
        need = 0
        for size, key in files:
            # local relative path under derivatives/
            # key: ds003626/derivatives/sub-../file
            rel = Path(*Path(key).parts[1:])  # derivatives/sub-...
            local = dest / rel
            if local.exists() and local.stat().st_size > 0:
                continue
            need += size
        if planned + need > max_bytes:
            print(f"[download] stop before {sub}: would reach {(planned+need)/1e9:.3f} GB")
            break
        selected.append(sub)
        planned += need
        print(f"[download] queue {sub} (+{need/1e9:.3f} GB) -> {planned/1e9:.3f} GB")

    downloaded = []
    for sub in selected:
        for size, key in by_sub[sub]:
            rel = Path(*Path(key).parts[1:])
            local = dest / rel
            if local.exists() and local.stat().st_size > 0:
                print(f"[download] skip {rel}")
                continue
            local.parent.mkdir(parents=True, exist_ok=True)
            src = f"s3://openneuro.org/{key}"
            print(f"[download] GET {src}")
            subprocess.check_call(["aws", "s3", "cp", "--no-sign-request", src, str(local)])
            downloaded.append(str(rel))

    final = local_bytes(dest)
    print(f"[download] done subjects={selected}")
    print(f"[download] files_fetched={len(downloaded)} final_size={final/1e9:.3f} GB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
