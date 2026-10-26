# P5-G3A Retry 1 — Equivalence report

Evidence is limited to the three fresh 0–99 runs. The exact machine-readable
record is `comparison/equivalence_report.json`.

## Preserved observables

- All conditions processed frames 0–99 and logged 100 selected-keyframe records.
- Keyframe insertion indices were identical: `0,4,9,14,19,24,29,34,39,44,49,54,59,64,69,74,79,84,89,94,98,99`.
- Logged mapping-selection lists matched pairwise for OFF/LIGHT/DETAILED.
- Tracking and mapping iteration configuration remained 40 and 60 respectively.
- LIGHT and DETAILED archive logical bytes were both `574,464,000`; staging was
  `5,190` events and `135,521,280,000` bytes in both runs.
- All saved numeric arrays checked finite.

## Non-equivalence / limits

Final Gaussian counts differed: OFF `1,404,715`, LIGHT `1,405,052`, DETAILED
`1,403,275`. This is recorded as runtime nondeterminism or profiler interaction;
the data do not support a bit-exact claim. Mapping selection is only the log
observable, not a proof that every internal random call matched. The dropped
detailed event count (`1,958`) also invalidates detailed timing equivalence.
