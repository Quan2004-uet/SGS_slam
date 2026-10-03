# SGS-SLAM GPU server migration — 2026-10-03

Use `MIGRATION_MANIFEST.md` for the asset identities and checksums, and the
archive-root `RESTORE_ON_SERVER.md` for the required execution order. The
canonical work state after restore remains `CURRENT_STATE.md` and
`state.yaml`; the older `project_management/` files are archival.

## Transfer as two assets

1. Transfer `migration/SGS_SLAM_MIGRATION_2026-10-03.tar.zst` and its adjacent
   `.sha256` file. Verify the archive SHA-256 before extraction.
2. Transfer `data/Replica_data.zip` separately. Verify its 13,221,213,627-byte
   size and SHA-256
   `1e4a71b656936f2b75a91fb938cde2b22d690175410fd9be32d0a198471bf041`.
   Never substitute an unidentified Replica package.

After extraction, run `sha256sum -c CHECKSUMS.sha256` in the migration
directory. Restore the tracked repository from `git/sgs-slam-history.bundle`
at `e4183986204242a8bb422624618af07780a49d26` on `main`, then overlay
the included untracked documents and evidence at the paths listed in
`ARTIFACT_PATHS.tsv`. Do not treat the Git bundle alone as the full research
state: current project-state documents and runtime records were untracked or
Git-ignored on the old host.

## Compatibility boundary

The captured environment is evidence of the working old host, not a promise
that its binary packages will load on another GPU or driver. Inspect the
destination driver, CUDA toolkit, compiler, and PyTorch ABI before building
the pinned renderer. The old renderer source was temporary and is absent from
the archive; fetch exactly the recorded Git revision. Do not silently switch
forks, upgrade dependencies, or change the SGS-SLAM algorithm/config.

The Phase 3C-3 result establishes 4 GiB sufficiency through frame 49 on the
old GTX 1650 Ti only. A new host needs dataset[0], first-frame, and bounded
0–4 migration regressions before the Phase 3C-4 frame 0–99 run. Those are
future restore checks, not checks performed during packaging.

## Continuity

`SESSION_002` remains paused. Phase 3C-4 is not started. The previous
`/tmp/sgs_phase3c1_bounded_online.py` harness is absent, and no persistent
copy currently exists. Reconstruct the bounded harness during Phase 3C-4
preparation from released SGS-SLAM functions and the prior runtime records;
do not infer that this migration bundle contains it.
