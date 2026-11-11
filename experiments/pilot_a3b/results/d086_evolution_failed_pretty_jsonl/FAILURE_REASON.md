# Failed D-086 first execution — invalid JSONL artifact

The first execution of `dependency_experiment.py` generated analysis files but failed during `validate_artifact()` with:

`json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 2 column 1 (char 2)`

Root cause: raw records were serialized using indented multi-line JSON while the artifact was named JSONL. This directory preserves the failed, invalid artifact and is not a valid experiment result.

Before any rerun, regression tests were added for independently decodable JSONL, ledger provenance and Train/Validation cache isolation. The cache key was also corrected to include split, preventing a same-ID Train row from being reused as Validation evidence. No scenario, threshold, optimizer seed, objective or baseline was changed.
