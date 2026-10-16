#!/usr/bin/env python3
"""Prepare a deterministic, sanitized P6-BAM-006 visualization backup.

This copies only the three validated visualization packages and selected
research reports. It never reads model files for publication, writes only to a
new staging directory, and excludes NPZ/PLY/checkpoint and raw array files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


RUN_ID = "p6_bam_006_room0_0_1999_va2_r01"
PACKAGE_NAMES = (
    "va2",
    "va2_phase4_matched",
    "va2_phase4_extended_matched",
)
TEXT_SUFFIXES = {".json", ".md", ".log", ".txt", ".yaml", ".yml", ".csv"}
PAYLOAD_SUFFIXES = {".png", *TEXT_SUFFIXES}
SANITIZATIONS = (
    ("/home/robot/research/SGS_slam", "<SGS_SLAM_REPOSITORY>"),
    ("/home/robot", "<LOCAL_HOME>"),
    ("/tmp/", "<TEMP>/"),
)
REPORTS = (
    "docs/research/phase6_bam/P6_BAM_006_FULL_SCENE_REPORT.md",
    "docs/research/phase6_bam/P6_BAM_006_FULL_SCENE_COMPARISON.md",
    "docs/research/phase6_bam/P6_BAM_006_3D_VISUALIZATION_INVENTORY.md",
    "docs/research/phase6_bam/P6_BAM_006_PHASE4_MATCHED_VISUALIZATION_REPORT.md",
    "docs/research/phase6_bam/P6_BAM_006_PHASE4_EXTENDED_CAMERA_MATCHED_VISUALIZATION_REPORT.md",
    "docs/research/phase6_bam/P6_BAM_006_FINAL_SESSION_HANDOFF.md",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--staging-root", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo_root.resolve(strict=True)
    staging = args.staging_root.absolute()
    artifact_root = (repo / "results/runtime_artifacts/phase6_bam").resolve(strict=True)
    if staging.exists() or staging.is_symlink():
        raise SystemExit(f"Refusing occupied staging root: {staging}")
    if artifact_root not in staging.resolve(strict=False).parents:
        raise SystemExit(f"Staging root escapes Phase 6 artifact root: {staging}")

    remote_root = staging / "phase6_bam/p6_bam_006/visualization"
    remote_root.mkdir(parents=True, exist_ok=False)
    source_inventory: list[dict[str, object]] = []
    package_png_counts: dict[str, int] = {}
    excluded_arrays: list[str] = []

    for name in PACKAGE_NAMES:
        source = artifact_root / "p6_bam_006_comparison/visualization" / name
        if not source.is_dir() or source.is_symlink():
            raise SystemExit(f"Missing or unsafe source visualization package: {source}")
        destination = remote_root / name
        destination.mkdir()
        png_count = 0
        for item in sorted(source.rglob("*")):
            if item.is_symlink():
                raise SystemExit(f"Refusing symlink in visualization package: {item}")
            if not item.is_file():
                continue
            rel = item.relative_to(source)
            if item.suffix.lower() == ".npy":
                excluded_arrays.append(f"{name}/{rel.as_posix()}")
                continue
            if item.suffix.lower() not in PAYLOAD_SUFFIXES:
                raise SystemExit(f"Unexpected non-visualization payload type: {item}")
            target = destination / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            before_hash = sha256(item)
            shutil.copy2(item, target)
            sanitized = False
            if target.suffix.lower() in TEXT_SUFFIXES:
                original = target.read_text(encoding="utf-8", errors="strict")
                sanitized_text = original
                for needle, replacement in SANITIZATIONS:
                    sanitized_text = sanitized_text.replace(needle, replacement)
                if sanitized_text != original:
                    target.write_text(sanitized_text, encoding="utf-8")
                    sanitized = True
            after_hash = sha256(target)
            source_inventory.append(
                {
                    "source": item.relative_to(repo).as_posix(),
                    "staged": target.relative_to(staging).as_posix(),
                    "source_size_bytes": item.stat().st_size,
                    "staged_size_bytes": target.stat().st_size,
                    "source_sha256": before_hash,
                    "staged_sha256": after_hash,
                    "sanitized_copy": sanitized,
                }
            )
            png_count += int(target.suffix.lower() == ".png")
        package_png_counts[name] = png_count

    docs_dir = remote_root / "documentation"
    docs_dir.mkdir()
    for rel_text in REPORTS:
        source = repo / rel_text
        if not source.is_file() or source.is_symlink():
            raise SystemExit(f"Required publication report missing or unsafe: {source}")
        target = docs_dir / source.name
        original = source.read_text(encoding="utf-8")
        sanitized = original
        for needle, replacement in SANITIZATIONS:
            sanitized = sanitized.replace(needle, replacement)
        target.write_text(sanitized, encoding="utf-8")
        source_inventory.append(
            {
                "source": source.relative_to(repo).as_posix(),
                "staged": target.relative_to(staging).as_posix(),
                "source_size_bytes": source.stat().st_size,
                "staged_size_bytes": target.stat().st_size,
                "source_sha256": sha256(source),
                "staged_sha256": sha256(target),
                "sanitized_copy": sanitized != original,
            }
        )

    checksummed_files = sorted(
        path
        for path in remote_root.rglob("*")
        if path.is_file() and path.name not in {
            "SHA256SUMS.txt",
            "backup_manifest.json",
            "source_to_staging_inventory.json",
        }
    )
    sums = "".join(
        f"{sha256(path)}  {path.relative_to(remote_root).as_posix()}\n"
        for path in checksummed_files
    )
    (remote_root / "SHA256SUMS.txt").write_text(sums, encoding="utf-8")

    sanitized_count = sum(bool(row["sanitized_copy"]) for row in source_inventory)
    manifest = {
        "repository": "QuanDinh/SGS-SLAM-assets",
        "repo_type": "dataset",
        "destination_prefix": "phase6_bam/p6_bam_006/visualization/",
        "experiment": "P6-BAM-006-FULL",
        "run_id": RUN_ID,
        "experiment_status": "PASS_P6_BAM_006_FULL_SCENE_QUALITY_CONSTRAINED",
        "runtime_status": "FULL_SCENE_RUNTIME_SPEEDUP_UNVERIFIED",
        "source_revision": "002927f3b24dd69418c17da08bd4ae987bae9ee2",
        "package_png_counts": package_png_counts,
        "package_counts_include_phase4_reference_images": {
            "va2_phase4_extended_matched": True
        },
        "excluded_npy_visualization_intermediates": excluded_arrays,
        "sanitized_text_copy_count": sanitized_count,
        "sanitization_note": "Text copies redact server-local home and temporary-directory paths; originals remain unchanged. Staged hashes therefore differ for sanitized text, and source_to_staging_inventory.json records both hashes.",
        "deliberate_exclusions": [
            "Replica dataset and raw training images",
            "NPZ checkpoints and RGB/semantic PLY model files",
            "Six .npy visualization intermediates listed explicitly in this manifest",
            "Unrelated Phase 4/Phase 5 artifacts and runtime logs outside the three packages",
            "Secrets, credentials, environments, caches, and Git internals",
        ],
        "payload_file_count_excluding_three_backup_control_files": len(checksummed_files),
        "payload_bytes_excluding_three_backup_control_files": sum(p.stat().st_size for p in checksummed_files),
        "source_phase4_reference_images_are_labeled": "reconstruction_fidelity/phase4_reference/",
        "generated_by": "scripts/visualization/stage_phase6_hf_backup.py",
    }
    (remote_root / "backup_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (remote_root / "source_to_staging_inventory.json").write_text(
        json.dumps(source_inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    forbidden = ("/home/robot", "/tmp/")
    leaks = []
    for path in remote_root.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            text = path.read_text(encoding="utf-8", errors="strict")
            if any(marker in text for marker in forbidden):
                leaks.append(path.relative_to(staging).as_posix())
    if leaks:
        raise SystemExit(f"Unredacted local paths remain: {leaks}")
    print(json.dumps({
        "staging_root": str(staging),
        "remote_root": "phase6_bam/p6_bam_006/visualization",
        "package_png_counts": package_png_counts,
        "payload_file_count": len(checksummed_files),
        "payload_bytes": manifest["payload_bytes_excluding_three_backup_control_files"],
        "sanitized_text_copies": sanitized_count,
        "excluded_npy_count": len(excluded_arrays),
    }, indent=2))


if __name__ == "__main__":
    main()
