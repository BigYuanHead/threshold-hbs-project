# Benchmark README

This folder contains the benchmark code for the project.

## Files

### `timer.py`
Provides simple timing helpers.
Used to measure setup time, signing time, and verification time.

### `metrics.py`
Provides helper functions for benchmark processing.
Main uses:
- hash input messages into a fixed 32-byte digest
- measure serialized object size
- compute summary statistics such as mean and standard deviation
- save results to CSV and JSON

### `bench_baseline.py`
Benchmarks the baseline stateful hash-based signature scheme.
It measures:
- setup time
- signing time
- verification time
- final signature size
- average Merkle path length
- success rate

### `bench_threshold.py`
Benchmarks the threshold signing scheme.
It uses the entity layer:
- `TrustedServer`
- `Party`
- `UntrustedServer`
- `Verifier`

It measures:
- setup time
- signing time
- verification time
- final signature size
- average Merkle path length
- success rate

### `bench_compare.py`
Runs comparison experiments.
It is used for two main tests:
- compare baseline and threshold for different `total_keys`
- compare threshold performance for different `n_parties`

### `run_benchmarks.py`
Main script for running all benchmark experiments.
It saves the results into `benchmark/results/`.

## Current benchmark experiments

### 1. Compare by `total_keys`
This test compares baseline and threshold when the number of one-time keys changes.
Typical values:
- 4
- 8
- 16
- 32
- 64

This helps evaluate:
- setup scalability
- signing cost
- verification cost
- signature size growth

### 2. Compare by `n_parties`
This test measures threshold performance when the number of parties changes.
Typical values:
- 2
- 3
- 4

This helps evaluate:
- threshold scalability
- extra signing overhead from more parties
- whether verification stays stable

## How to run

Run from the project root:

```bash
python -m benchmark.run_benchmarks
```

## Output

Results are written to:

```text
benchmark/results/
```

Typical output files:
- `compare_total_keys_rows.csv`
- `compare_total_keys_summary.json`
- `compare_n_parties_rows.csv`
- `compare_n_parties_summary.json`

## Notes

- All benchmark messages are first hashed to a 32-byte SHA-256 digest.
- The current threshold benchmark measures computation cost only.
- It does not simulate real network delay or communication latency.
- This benchmark is for the minimal project implementation.
