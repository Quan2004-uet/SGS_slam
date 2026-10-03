# SGS-SLAM GPU server migration — 2026-10-04

Use `MIGRATION_MANIFEST.md` for the asset identities and checksums. The
archive-root `RESTORE_ON_SERVER.md` records the earlier bundle-based restore
protocol; the GitHub and Hugging Face sequence below applies to this final
checkpoint. The
canonical work state after restore remains `CURRENT_STATE.md` and
`state.yaml` from GitHub `main`; the older `project_management/` files are
archival. `SESSION_002` remains `PAUSED`, and Phase 3C-4 has not started.

## Fetch and verify on the GPU server

Run these commands from a new parent directory. The private Hub repository is
`QuanDinh/SGS-SLAM-assets` (repo type `dataset`). The full download includes
both the extracted Replica dataset and its separate ZIP, plus the migration
directory and archive.

```bash
git clone https://github.com/Quan2004-uet/SGS_slam.git SGS-SLAM
hf auth login
hf download QuanDinh/SGS-SLAM-assets --repo-type dataset --local-dir SGS-SLAM-assets

( cd SGS-SLAM-assets && sha256sum -c migration/SGS_SLAM_MIGRATION_2026-10-03.tar.zst.sha256 )
printf '%s  %s\n' \
  '1e4a71b656936f2b75a91fb938cde2b22d690175410fd9be32d0a198471bf041' \
  'SGS-SLAM-assets/data/Replica_data.zip' | sha256sum -c -

mkdir -p SGS-SLAM-assets/restore
tar --zstd -xf SGS-SLAM-assets/migration/SGS_SLAM_MIGRATION_2026-10-03.tar.zst \
  -C SGS-SLAM-assets/restore
( cd SGS-SLAM-assets/restore/SGS_SLAM_MIGRATION_2026-10-03 && sha256sum -c CHECKSUMS.sha256 )

# Copy only files absent from the newer GitHub checkout.
cp -an SGS-SLAM-assets/restore/SGS_SLAM_MIGRATION_2026-10-03/overlay/. SGS-SLAM/
mkdir -p SGS-SLAM/data
unzip -q SGS-SLAM-assets/data/Replica_data.zip -d SGS-SLAM/data
```

Inspect `ARTIFACT_PATHS.tsv` and `RESTORE_ON_SERVER.md` inside the extracted
archive for original paths and research evidence. The archive is a 2026-10-03
snapshot; do not overwrite newer GitHub documentation with its older overlay.
The included Git bundle preserves older history and is a fallback, not the
source checkout when GitHub `main` is available. Check
`git -C SGS-SLAM status --short` and the canonical project state after
restoration.

## Compatibility boundary

The captured environment is evidence of the working old host, not a promise
that its binary packages will load on another GPU or driver. Inspect the
destination driver, CUDA toolkit, compiler, and PyTorch ABI before building
the pinned renderer. The old renderer source was temporary and is absent from
the archive; fetch exactly the recorded Git revision. Do not silently switch
forks, upgrade dependencies, or change the SGS-SLAM algorithm/config.

The Phase 3C-3 result establishes 4 GiB sufficiency through frame 49 on the
old GTX 1650 Ti only. Record the destination `nvidia-smi`, `nvcc --version`,
compiler versions, PyTorch/CUDA ABI, and GPU VRAM before rebuilding the exact
renderer revision. A new host needs dataset[0], first-frame, and bounded 0–4
migration regressions before the Phase 3C-4 frame 0–99 run. Those are future
restore checks, not checks performed during this migration checkpoint.

## Continuity

`SESSION_002` remains paused. Phase 3C-4 is not started. The previous
`/tmp/sgs_phase3c1_bounded_online.py` harness is absent, and no persistent
copy currently exists. Reconstruct the bounded harness during Phase 3C-4
preparation from released SGS-SLAM functions and the prior runtime records;
do not infer that this migration bundle contains it.
