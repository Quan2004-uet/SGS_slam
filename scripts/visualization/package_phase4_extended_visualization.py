#!/usr/bin/env python3
"""Package and validate the saved-model Phase 4-camera-matched Phase 6 views."""

from __future__ import annotations

import hashlib
import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat


ROOT = Path("results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched")
P6_RUN = Path("results/runtime_artifacts/phase6_bam/p6_bam_006_room0_0_1999_va2_r01")
P4_V1 = Path("results/runtime_artifacts/phase4_vb001_visualization")
P4_V2 = Path("results/runtime_artifacts/phase4_vb001_visualization_v2")
P4_V3A = Path("results/runtime_artifacts/phase4_vb001_visualization_v3a")
FRAMES = (0, 499, 999, 1499, 1999)
V3A_VIEWS = ("trajectory_observed", "room_overview", "top_oblique")
CAMERA_HASHES = {
    "v1/overview.json": "c5e0029b1758788322538ce27e587c8cdfa5a3277aba331431e50d5ac80865bb",
    "v1/oblique.json": "9846a224e93b3615afd45097b9106037c3550b5199b74d4e0550f328ad220120",
    "v1/top_oblique.json": "0d865494919fb2066cf769ef654163ee3f1e262d5ebb4cf8b95681d6934ec196",
    "v3a/room_overview.json": "f5598e540e78c8c838f3db0e83194520477e528735b65336c5f66a590b7a8cfc",
    "v3a/top_oblique.json": "a85a5e8f06370743894a58003034e0ee415eecafbc626ec308cf9d6f0e4a745d",
    "v3a/trajectory_observed.json": "df75161d510552a31bd5096ac3cc5a07eea5b58cf9c0ac777d15aa507af17f1a",
}
MODEL_HASHES = {
    "params.npz": "1193f5d5a854225d6e9fc68154d459b5eb026e056a91b5f00639b8da0facd0a5",
    "params.ply": "dc10441cd383ad7861d27fb70a4f9a76fe9dd88a91e2bacc197b18bbe24cb50a",
    "seg_params.ply": "98676b4c3e6447681f99426153dfb112bee76882ac9f5d3a18cf11f4832fec21",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def copy_new(source: Path, destination: Path) -> None:
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-metadata", action="store_true", help="Refresh only package metadata after additive outputs; never copy or overwrite images.")
    args = parser.parse_args()
    root = ROOT.resolve()
    model_root = P6_RUN.resolve()
    cross = root / "cross_modal_overview"
    semantic_family = root / "semantic_id_structure"
    trajectory_family = root / "trajectory_in_geometry"

    # Family-specific copies keep the overview, class structure, and trajectory
    # deliverables discoverable without duplicating or changing camera records.
    if not args.refresh_metadata:
        for view in V3A_VIEWS:
            copy_new(cross / "semantic/categorical" / f"{view}.png", semantic_family / f"{view}.png")
        copy_new(cross / "semantic/categorical/legend_29_classes.png", semantic_family / "legend_29_classes.png")
        for source in sorted((cross / "semantic/classwise").glob("*.png")):
            copy_new(source, semantic_family / source.name)
        copy_new(cross / "trajectory/estimated_trajectory_3d.png", trajectory_family / "estimated_trajectory_3d.png")
        copy_new(cross / "cameras/top_oblique.json", trajectory_family / "camera_top_oblique.json")

    camera_validation: dict[str, bool] = {}
    for relative, expected_hash in CAMERA_HASHES.items():
        path = root / "cameras" / relative
        camera_validation[relative] = path.is_file() and digest(path) == expected_hash
    if not all(camera_validation.values()):
        raise RuntimeError(f"Phase 4 camera copies do not match authoritative hashes: {camera_validation}")

    phase4_v2_camera_hashes: dict[str, str] = {}
    for frame_id in FRAMES:
        frame_name = f"frame_{frame_id:04d}"
        source_dir = P4_V2 / "frames" / frame_name
        frame_metadata = json.loads((source_dir / "frame_metadata.json").read_text(encoding="utf-8"))
        camera_copy = root / "reconstruction_fidelity/cameras/phase4_v2" / f"{frame_name}.json"
        if not camera_copy.is_file() or digest(camera_copy) != digest(source_dir / "frame_metadata.json"):
            raise RuntimeError(f"Phase 4 V2 camera metadata copy mismatch for {frame_name}")
        phase4_v2_camera_hashes[frame_name] = digest(camera_copy)
        rendered = root / "reconstruction_fidelity/phase6_rendered/rgb/unfiltered" / f"{frame_name}.png"
        semantic = root / "reconstruction_fidelity/phase6_rendered/semantic/raw" / f"{frame_name}.png"
        if not rendered.is_file() or not semantic.is_file():
            raise FileNotFoundError(f"Missing exact-camera Phase 6 rendering for {frame_name}")
        if frame_metadata["image_dimensions_wh"] != [1200, 680]:
            raise RuntimeError(f"Unexpected Phase 4 V2 resolution in {frame_name}")

    model_validation: dict[str, bool] = {}
    for filename, expected_hash in MODEL_HASHES.items():
        model_validation[filename] = digest(model_root / filename) == expected_hash
    if not all(model_validation.values()):
        raise RuntimeError(f"Saved Phase 6 model changed: {model_validation}")

    family_inventory = {
        "families": [
            {
                "name": "camera_aligned_reconstruction_fidelity",
                "phase4_source": str(P4_V2),
                "accepted_evidence": str(P4_V2 / "GATE_V2_REPORT.md"),
                "phase4_status": "PASS_V2_CAMERA_ALIGNED_QUALITATIVE",
                "camera_source": "per-frame estimated_w2c/intrinsics in Phase 4 V2 frame_metadata.json",
                "frame_ids": list(FRAMES),
                "resolution": [1200, 680],
                "phase6_rendered_outputs": 15,
                "matching": "Phase 6 RGB and learned semantic colors rendered from saved params.npz at the exact five Phase 4 estimated-w2c matrices; original Phase 4 V2 images copied as reference.",
                "not_recomputed": ["metrics", "GT-palette-assisted semantic recoloring"],
                "depth_render": "Five saved-checkpoint depth-only renderings using Phase 4 eval_helpers depth/silhouette color pass; fixed JET display range [0,6] m; no metrics or dataset access.",
            },
            {
                "name": "full_scene_3d_cross_modal_overview",
                "phase4_source": str(P4_V3A),
                "accepted_evidence": str(P4_V3A / "GATE_V3A_REPORT.md"),
                "phase4_status": "PASS_V3A_FULL_SCENE_VISUALIZATION_PROOF",
                "camera_source": str(P4_V3A / "cameras"),
                "camera_names": list(V3A_VIEWS),
                "camera_resolution": [960, 540],
                "renderer": "Phase 4 V3A saved-map repository-native Gaussian renderer; supplied camera JSON files used without regeneration.",
                "modalities": ["RGB Gaussian render", "geometry-only Gaussian-center diagnostic", "raw learned semantic colors", "categorical ID overlay", "cross-modal panels"],
            },
            {
                "name": "fixed_semantic_id_class_structure",
                "phase4_source": str(P4_V3A / "semantic/categorical"),
                "accepted_evidence": str(P4_V3A / "GATE_V3A_REPORT.md"),
                "phase4_status": "PASS_V3A_FULL_SCENE_VISUALIZATION_PROOF",
                "camera_source": str(P4_V3A / "cameras"),
                "palette_source": str(Path("results/runtime_artifacts/phase4_vb001_visualization_audit/semantic_mapping.csv")),
                "source_field": "params.npz semantic_ids",
                "camera_names": list(V3A_VIEWS),
                "output_pngs": sorted(path.name for path in semantic_family.glob("*.png")),
                "interpretation": "Fixed per-Gaussian Semantic-ID visualization using the verified 29-class Replica palette; not a per-pixel semantic predictor and not semantic-color PLY.",
            },
            {
                "name": "estimated_trajectory_in_reconstructed_geometry",
                "phase4_source": str(P4_V3A / "trajectory/estimated_trajectory_3d.png"),
                "accepted_evidence": str(P4_V3A / "GATE_V3A_REPORT.md"),
                "phase4_status": "PASS_V3A_FULL_SCENE_VISUALIZATION_PROOF",
                "camera_source": str(P4_V3A / "cameras/top_oblique.json"),
                "camera_sha256": CAMERA_HASHES["v3a/top_oblique.json"],
                "pose_source": "Phase 6 saved params.npz cam_unnorm_rots/cam_trans (2,000 estimated poses)",
                "output": "trajectory_in_geometry/estimated_trajectory_3d.png",
                "interpretation": "Blue estimated path with green start and red end over deterministic sampled Gaussian-center geometry; no GT alignment.",
            },
        ]
    }
    write_json(root / "metadata/family_inventory.json", family_inventory)

    pngs = sorted(path for path in root.rglob("*.png") if path.is_file())
    image_records = []
    all_nonempty_nonuniform = True
    for path in pngs:
        with Image.open(path) as im:
            rgb = im.convert("RGB")
            std = float(sum(ImageStat.Stat(rgb).stddev) / 3.0)
            record = {
                "path": path.relative_to(root).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": digest(path),
                "width": im.width,
                "height": im.height,
                "mode": im.mode,
                "nonuniform": std > 0,
                "mean_channel_stddev": std,
            }
            image_records.append(record)
            all_nonempty_nonuniform &= record["size_bytes"] > 0 and record["nonuniform"]
    if not all_nonempty_nonuniform:
        raise RuntimeError("At least one PNG is empty or uniform")

    expected_families = {
        "reconstruction_fidelity": 10,
        "cross_modal_overview": 26,
        "semantic_id_structure": len(list(semantic_family.glob("*.png"))),
        "trajectory_in_geometry": 1,
    }
    family_counts = {key: len(list((root / key).rglob("*.png"))) for key in expected_families}
    validation = {
        "status": "PASS",
        "all_images_nonempty_and_nonuniform": all_nonempty_nonuniform,
        "png_count_total": len(pngs),
        "png_counts_by_family": family_counts,
        "all_v3a_views_present": all((cross / "rgb/unfiltered" / f"{name}.png").is_file() for name in V3A_VIEWS),
        "all_v3a_semantic_id_views_present": all((semantic_family / f"{name}.png").is_file() for name in V3A_VIEWS),
        "all_phase4_v2_camera_definitions_copied_byte_identically": len(phase4_v2_camera_hashes) == len(FRAMES),
        "v1_and_v3a_camera_json_hashes_match_phase4": camera_validation,
        "phase4_v2_camera_metadata_sha256": phase4_v2_camera_hashes,
        "phase6_source_model_hashes_unchanged": model_validation,
        "phase6_saved_checkpoint_hash_from_render_metadata": json.loads((root / "reconstruction_fidelity/render_metadata.json").read_text())["source_checkpoint_sha256_before"],
        "phase6_v3a_model_hashes_before_after": {
            "params.npz": MODEL_HASHES["params.npz"],
            "params.ply": MODEL_HASHES["params.ply"],
            "seg_params.ply": MODEL_HASHES["seg_params.ply"],
            "evidence": "Pre-render SHA256 verification plus saved-checkpoint renderer before/after check; PLY hashes rechecked after export.",
        },
        "source_model_hashes_expected": MODEL_HASHES,
        "no_slam_or_evaluation_rerun": True,
        "cuda_visualization_only": True,
        "image_records": image_records,
    }
    write_json(root / "metadata/validation_report.json", validation)

    manifest_files = sorted(
        path for path in root.rglob("*")
        if path.is_file() and path.name not in {
            "visualization_manifest.json", "validation_report.json", "family_inventory.json", "summary.md"
        }
    )
    manifest = {
        "output_root": str(root),
        "source_model": str(model_root),
        "source_model_sha256": MODEL_HASHES,
        "camera_sources": {key: value for key, value in CAMERA_HASHES.items()},
        "artifacts": [
            {"path": path.relative_to(root).as_posix(), "size_bytes": path.stat().st_size, "sha256": digest(path)}
            for path in manifest_files
        ],
    }
    write_json(root / "metadata/visualization_manifest.json", manifest)
    (root / "metadata/summary.md").write_text(
        "# Extended Phase 4 Camera-Matched Phase 6 Visualization\n\n"
        f"- Families: {', '.join(item['name'] for item in family_inventory['families'])}\n"
        f"- PNG total (including copied Phase 4 V2 references): {len(pngs)}\n"
        f"- Phase 4 V1/V3A cameras byte-identical: {all(camera_validation.values())}\n"
        f"- Phase 4 V2 frame cameras used for Phase 6 renders: {list(FRAMES)} at 1200x680\n"
        f"- Phase 6 source model hashes unchanged: {all(model_validation.values())}\n"
        "- Scope: saved-model visualization only; no SLAM, metric evaluation, or training.\n",
        encoding="utf-8",
    )
    print(json.dumps({"png_counts_by_family": family_counts, "png_count_total": len(pngs), "validation": validation["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
