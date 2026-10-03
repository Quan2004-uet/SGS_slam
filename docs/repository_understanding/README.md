# SGS-SLAM repository understanding

Static audit target: commit `e4183986204242a8bb422624618af07780a49d26` (audit date 2026-10-02). No experiment or profiler was run. The local paper `2402.03246v6.pdf` (arXiv v6, 2024-11-24) was used for paper/code comparison.

Evidence labels used throughout:

- **[VERIFIED FROM SOURCE]** directly established by executable source.
- **[VERIFIED FROM CONFIG]** established by checked-in configuration.
- **[VERIFIED FROM README/DOCUMENTATION]** stated in README or paper, but not necessarily implemented.
- **[INFERRED]** a reasoned consequence of source; runtime confirmation is still desirable.
- **[UNKNOWN / NEEDS RUNTIME VERIFICATION]** static inspection cannot prove it.

Documents:

1. [Repository overview](00_repository_overview.md)
2. [Execution flow and call graph](01_execution_flow.md)
3. [Core state](02_core_state.md)
4. [Gaussian representation and renderer](03_gaussian_representation.md)
5. [Tracking](04_tracking.md)
6. [Mapping, densification, and post optimization](05_mapping.md)
7. [Semantic pipeline](06_semantic_pipeline.md)
8. [Keyframe system](07_keyframe_system.md)
9. [Losses and optimizers](08_loss_and_optimization.md)
10. [Datasets, coordinates, configuration, and evaluation](09_dataset_and_coordinates.md)
11. [GPU/VRAM architecture](10_memory_architecture.md)
12. [Paper/code mapping and critical files](11_paper_code_mapping.md)
13. [Research modification surface](12_research_modification_surface.md)
14. [Unknowns and runtime verification](13_unknowns_and_runtime_verification.md)

The audit treats `scripts/slam.py` as the current semantic online system. `scripts/gaussian_splatting.py` is an older/non-semantic Gaussian-only training pipeline and is not the main README entry point. **[VERIFIED FROM SOURCE; VERIFIED FROM README/DOCUMENTATION]**

## Final-report coverage map

| Requested section | Canonical document |
|---|---|
| 1. Repository architecture | `00_repository_overview.md` |
| 2. Main execution flow | `01_execution_flow.md` |
| 3. Core state | `02_core_state.md` |
| 4. Gaussian representation | `03_gaussian_representation.md` |
| 5. Tracking | `04_tracking.md` |
| 6. Mapping | `05_mapping.md` |
| 7. Bundle Adjustment | `05_mapping.md` (“not active” finding) |
| 8. Gaussian densification | `05_mapping.md` |
| 9. Semantic pipeline | `06_semantic_pipeline.md` |
| 10. Keyframe system | `07_keyframe_system.md` |
| 11. Loss functions | `08_loss_and_optimization.md` |
| 12. Optimizers | `08_loss_and_optimization.md` |
| 13. Dataset pipeline | `09_dataset_and_coordinates.md` |
| 14. Coordinate system | `09_dataset_and_coordinates.md` |
| 15. Evaluation | `09_dataset_and_coordinates.md` |
| 16. GPU memory architecture | `10_memory_architecture.md` |
| 17. Paper ↔ code mapping | `11_paper_code_mapping.md` |
| 18. Critical files | `11_paper_code_mapping.md` |
| 19. Research modification surface | `12_research_modification_surface.md` |
| 20. Runtime-verification unknowns | `13_unknowns_and_runtime_verification.md` |
