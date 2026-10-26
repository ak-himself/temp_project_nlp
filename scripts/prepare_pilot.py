"""Prepare bounded XL-Sum pilot records from the official source archives."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import tarfile
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_records(archive: Path, language: str, limit: int) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with tarfile.open(archive, mode="r:bz2") as bundle:
        for split in ("train", "val", "test"):
            member_name = f"./{language}_{split}.jsonl"
            member = bundle.extractfile(member_name)
            if member is None:
                raise FileNotFoundError(f"Missing archive member: {member_name}")
            for line_number, raw_line in enumerate(member, start=1):
                if line_number > limit:
                    break
                item = json.loads(raw_line)
                records.append(
                    {
                        "stable_id": f"xlsum-{language}-{split}-{item['id']}",
                        "dataset": "csebuetnlp/xlsum",
                        "config": language,
                        "split": "validation" if split == "val" else split,
                        "category": language,
                        "source": item["text"],
                        "reference_summary": item["summary"],
                        "title": item["title"],
                        "url": item["url"],
                    }
                )
    return records


def write_records(records: list[dict[str, Any]], output_dir: Path, language: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{language}_pilot.jsonl"
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw/xlsum"))
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed/xlsum"))
    parser.add_argument("--manifest-dir", type=Path, default=Path("data/manifests"))
    parser.add_argument("--limit-per-split", type=int, default=20)
    args = parser.parse_args()
    if args.limit_per_split < 1:
        raise ValueError("--limit-per-split must be positive")

    all_records: list[dict[str, Any]] = []
    archive_metadata: list[dict[str, Any]] = []
    for language in ("hindi", "english"):
        archive = args.raw_dir / f"{language}_XLSum_v2.0.tar.bz2"
        if not archive.is_file():
            raise FileNotFoundError(archive)
        records = read_records(archive, language, args.limit_per_split)
        write_records(records, args.processed_dir, language)
        all_records.extend(records)
        archive_metadata.append(
            {
                "language": language,
                "path": str(archive),
                "bytes": archive.stat().st_size,
                "sha256": sha256(archive),
                "revision": "30fece425f9a3866e04321773ca7a80056d55ca6",
            }
        )

    counts: dict[str, dict[str, int]] = {}
    for record in all_records:
        counts.setdefault(record["config"], {}).setdefault(record["split"], 0)
        counts[record["config"]][record["split"]] += 1
    manifest = {
        "status": "bounded_pilot_prepared",
        "dataset": "csebuetnlp/xlsum",
        "license": "CC BY-NC-SA 4.0",
        "source_revision": "30fece425f9a3866e04321773ca7a80056d55ca6",
        "fields": ["stable_id", "dataset", "config", "split", "category", "source", "reference_summary", "title", "url"],
        "official_split_counts": {
            "hindi": {"train": 70778, "validation": 8847, "test": 8847},
            "english": {"train": 306522, "validation": 11535, "test": 11535},
        },
        "pilot_limit_per_split": args.limit_per_split,
        "pilot_counts": counts,
        "archives": archive_metadata,
        "limitations": [
            "Pilot is not representative of the full dataset.",
            "Official test records are retained only for pilot inspection and must remain untouched for model/prompt selection.",
        ],
    }
    args.manifest_dir.mkdir(parents=True, exist_ok=True)
    (args.manifest_dir / "xlsum_pilot.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    with (args.manifest_dir / "xlsum_pilot.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["config", "split", "count", "official_count"])
        writer.writeheader()
        for config, split_counts in counts.items():
            for split, count in split_counts.items():
                writer.writerow(
                    {
                        "config": config,
                        "split": split,
                        "count": count,
                        "official_count": manifest["official_split_counts"][config][split],
                    }
                )


if __name__ == "__main__":
    main()
