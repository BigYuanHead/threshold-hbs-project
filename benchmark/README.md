# Benchmark README

This benchmark suite evaluates the current implementation of the project under several controlled experiments.

## What the benchmark currently measures

The benchmark currently measures:
- setup time
- signing time
- verification time
- signature size
- batch pack size
- success / rejection behavior for some extension tests

All experiments save:
- raw CSV results
- summary CSV / JSON results
- plot images

## What variables are controlled

The benchmark follows a control-variable approach.
In each experiment, one main variable is changed while the other parameters are fixed.

### 1. `total_keys` scaling
Changed variable:
- `total_keys`

Fixed variable:
- `n_parties = 3`

This experiment studies how system cost changes as the number of one-time keys grows.

### 2. `n_parties` scaling
Changed variable:
- `n_parties`

Fixed variable:
- `total_keys = 32`

This experiment studies how threshold overhead changes as more parties participate.

### 3. `k-of-n` scaling
Changed variable:
- `threshold_k`

Fixed variables:
- `n_parties = 4`
- `total_keys = 16`

This experiment studies how the k-of-n extension behaves when the threshold changes.

### 4. batch scaling
Changed variable:
- `batch_size`

Fixed variables:
- `total_keys = 32`
- `n_parties = 3`

This experiment studies how batch signing changes total cost and per-message cost.

### 5. Lamport vs Winternitz
Changed variable:
- OTS type

Fixed variables:
- `total_keys = 16`
- `n_parties = 3`
- `w = 16`

This experiment compares the Lamport-based threshold scheme with the Winternitz-based threshold scheme.

## What is compared

The benchmark currently includes these comparisons:

### A. Baseline vs threshold
It compares the original baseline implementation with the original threshold implementation under different `total_keys`.

Compared metrics:
- setup time
- sign time
- verify time
- signature size

### B. Threshold scaling with number of parties
It compares threshold performance under different values of `n_parties`.

Compared metrics:
- setup time
- sign time
- verify time

### C. k-of-n extension
It compares k-of-n performance under different values of `k`.

Compared metrics:
- sign time
- verify time
- signature size

It also checks correctness for:
- wrong message rejection
- less-than-k rejection
- reused key rejection

### D. Batch extension
It compares batch performance under different batch sizes.

Compared metrics:
- total batch sign time
- total batch verify time
- per-message sign time
- per-message verify time
- batch pack size

### E. Lamport vs Winternitz
It compares the two OTS backends in the threshold setting.

Compared metrics:
- setup time
- sign time
- verify time
- signature size

## Current output structure

The benchmark generates results in:

```text
results