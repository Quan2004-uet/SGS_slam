# R1 BCGM Admission Validation — Replica room1

**Status: PASS.** Independently parsed 1,999 BCGM_INSERTION records from the saved stdout and matched all 1,999 worker insertion transitions in insertion_counts.jsonl. Frames are contiguous 1–1999.

| Counter | Verified |
|---|---:|
| Event Cap / Global Cap | 9,000 / 4,500,000 |
| Valid candidates | 33,408,344 |
| Admitted | 3,892,851 |
| Rejected | 29,515,493 |
| event_saturated activations | 294 |
| global_saturated activations | 1251 |
| Maximum admitted/event | 9,000 |
| Invariant violations | 0 |

Every event satisfies N_admitted = min(N_valid, 9000, max(0, 4500000 - N_before)); N_valid = admitted + rejected; N_after = N_before + admitted; nonnegative values and N_after <= cap. Flags independently match the implementation: event_saturated iff candidates were rejected at Event Cap; global_saturated iff before + admitted reaches Global Cap; budget_saturated is their OR. Before/after counts agree with worker trace.

Global Cap runtime behavior is verified because global_saturated occurred 1251 times. Event and Global Cap can overlap. The final saved count 4,498,964 differs by 27 from last immediate post-insertion count 4,498,991, consistent with mapping pruning at scripts/slam.py:1038-1040 after event logging at 504-508. Pruning can change map size without invalidating admission cap evidence.

Evidence: results/runtime_artifacts/phase7_gate3_room1/p7_bcgm_r1_full_room1_on_0_1999_r01/stdout_stderr.log and insertion_counts.jsonl; hashes are indexed by original artifact_manifest.json.
